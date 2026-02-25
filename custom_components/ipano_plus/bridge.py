"""Bridge for iPano Plus communication."""
import asyncio
import json
import logging
import socket
from datetime import datetime
from typing import Dict, Any, Optional
import time

from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .const import (
    DOMAIN,
    MSG_TYPE_BUTTON,
    MSG_TYPE_BACKLIGHT_CHANGE,
    MSG_TYPE_RELAY_CHANGE,
    MSG_TYPE_PROXIMITY,
    MSG_TYPE_HEARTBEAT,
    MSG_TYPE_BACKLIGHT_CONTROL,
    MSG_TYPE_RELAY_CONTROL,
    MSG_TYPE_SCREEN_WAKE,
    BUTTON_MAP,
    BACKLIGHT_COLORS,
    EVENT_BUTTON_PRESSED,
    EVENT_PROXIMITY_DETECTED,
    EVENT_RELAY_CHANGED,
    SIGNAL_BACKLIGHT_UPDATE,
    SIGNAL_RELAY_UPDATE,
    SIGNAL_BUTTON_EVENT,
    SIGNAL_PROXIMITY_UPDATE,
)

_LOGGER = logging.getLogger(__name__)


class iPanoBridge:
    """Bridge to communicate with iPano Plus device."""

    def __init__(self, hass: HomeAssistant, config: Dict[str, Any]):
        """Initialize the bridge."""
        self.hass = hass
        self.config = config
        self.host = config.get("host", config.get("ip") or None)
        self.port = config.get("port", 3124)
        self.name = config.get("name", "iPano Plus")

        # Connection
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self.connected = False
        self.reconnect_task: Optional[asyncio.Task] = None
        self.listen_task: Optional[asyncio.Task] = None
        self.heartbeat_task: Optional[asyncio.Task] = None
        self.last_heartbeat = 0.0

        # State tracking
        self.button_states = {131: False, 132: False, 133: False, 134: False}
        self.relay_states = {0: False, 1: False}
        self.backlight_states = {0: 0, 1: 0, 2: 0, 3: 0}
        self.proximity_state = False

        _LOGGER.info(f"iPano Bridge initialized for {self.host}:{self.port}")

    async def test_connection(self, timeout: float = 3.0) -> bool:
        """Quick test to see if the device accepts TCP connections."""
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port), timeout=timeout
            )
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass
            return True
        except Exception as err:
            _LOGGER.debug(f"test_connection failed: {err}")
            return False

    async def async_start(self):
        """Start the bridge connection."""
        _LOGGER.info(f"Starting iPano Plus bridge for {self.host}:{self.port}")
        await self._connect_with_retry()

    async def _connect_with_retry(self, max_retries: int = 5):
        """Connect with retry logic."""
        for attempt in range(max_retries):
            try:
                await self._connect()
                if self.connected:
                    return
            except Exception as e:
                _LOGGER.error(f"Connection attempt {attempt + 1} failed: {e}")

            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                _LOGGER.info(f"Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)

        _LOGGER.error("Failed to connect after multiple attempts")

    async def _connect(self):
        """Establish TCP connection to iPano."""
        try:
            _LOGGER.debug(f"Connecting to {self.host}:{self.port}")
            self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
            self.connected = True
            self.last_heartbeat = time.time()

            _LOGGER.info(f"Connected to iPano Plus at {self.host}:{self.port}")

            # Start listening & heartbeat
            self.listen_task = asyncio.create_task(self._listen_loop())
            self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())

            # small delay then query initial states
            await asyncio.sleep(1)
            await self._query_initial_states()

            # Fire connection event (bus + dispatcher)
            payload = {
                "device": self.name,
                "button": "system",
                "action": "connected",
                "timestamp": datetime.now().isoformat(),
            }
            self.hass.bus.async_fire(EVENT_BUTTON_PRESSED, payload)
            async_dispatcher_send(self.hass, SIGNAL_BUTTON_EVENT, payload)

        except (ConnectionRefusedError, socket.gaierror) as err:
            _LOGGER.error(f"Connection refused: {err}")
            self.connected = False
        except asyncio.TimeoutError as err:
            _LOGGER.error(f"Connection timeout: {err}")
            self.connected = False
        except OSError as err:
            _LOGGER.error(f"Network error: {err}")
            self.connected = False
        except Exception as err:
            _LOGGER.error(f"Unexpected error: {err}")
            self.connected = False

    async def _heartbeat_loop(self):
        """Send heartbeat regularly; update last_heartbeat if ack received."""
        while self.connected:
            try:
                current_time = time.time()
                if current_time - self.last_heartbeat > 15:
                    success = await self._send_message(
                        {"type": MSG_TYPE_HEARTBEAT, "data": "ok", "state": 200, "msg": ""}
                    )
                    if success:
                        self.last_heartbeat = current_time
                        _LOGGER.debug("Heartbeat sent")
            except Exception as e:
                _LOGGER.debug(f"Heartbeat error: {e}")

            await asyncio.sleep(5)

    async def _listen_loop(self):
        """Listen for newline-delimited JSON messages."""
        buffer = ""
        while self.connected:
            try:
                data = await asyncio.wait_for(self.reader.read(4096), timeout=30)
                if not data:
                    _LOGGER.warning("Connection closed by iPano (no data)")
                    self.connected = False
                    break

                buffer += data.decode("utf-8", errors="ignore")

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if line:
                        await self._process_message(line)

            except asyncio.TimeoutError:
                _LOGGER.debug("Read timeout, continue listening")
                continue
            except asyncio.CancelledError:
                _LOGGER.debug("Listen loop cancelled")
                break
            except (ConnectionResetError, ConnectionAbortedError) as e:
                _LOGGER.warning(f"Connection reset: {e}")
                self.connected = False
                break
            except Exception as err:
                _LOGGER.error(f"Error in listen loop: {err}")
                self.connected = False
                break

        # Try to reconnect
        if not self.connected:
            await self._handle_disconnection()

    async def _handle_disconnection(self):
        """Handle disconnection and reconnect attempts."""
        _LOGGER.warning("Disconnected from iPano, scheduling reconnect...")

        if self.heartbeat_task:
            self.heartbeat_task.cancel()

        if self.writer:
            try:
                self.writer.close()
                await asyncio.sleep(0.1)
            except Exception:
                pass

        # Reconnect after short delay
        await asyncio.sleep(5)
        if not self.connected:
            _LOGGER.info("Attempting to reconnect...")
            await self._connect_with_retry(max_retries=3)

    async def _process_message(self, message: str):
        """Process incoming JSON message from the panel."""
        try:
            _LOGGER.debug(f"Raw message received: {message}")
            data = json.loads(message)
            msg_type = data.get("type")
            state = data.get("state", 200)

            if state != 200:
                _LOGGER.warning(f"Message with non-200 state: {data}")
                return

            _LOGGER.debug(f"Processing message type {msg_type}: {data}")

            if msg_type == MSG_TYPE_BUTTON:
                await self._handle_button_event(data)
            elif msg_type == MSG_TYPE_RELAY_CHANGE:
                await self._handle_relay_change(data)
            elif msg_type == MSG_TYPE_BACKLIGHT_CHANGE:
                await self._handle_backlight_change(data)
            elif msg_type == MSG_TYPE_PROXIMITY:
                await self._handle_proximity(data)
            elif msg_type == MSG_TYPE_HEARTBEAT:
                _LOGGER.debug("Heartbeat acknowledged")
                self.last_heartbeat = time.time()
            else:
                _LOGGER.debug(f"Unhandled message type {msg_type}")

        except json.JSONDecodeError as err:
            _LOGGER.error(f"Invalid JSON from iPano: {message}, error: {err}")
        except Exception as err:
            _LOGGER.error(f"Error processing message: {err}")

    async def _handle_button_event(self, data: Dict[str, Any]):
        """Handle button press/release event and notify Home Assistant."""
        try:
            event_data = data.get("data", {})
            key_code = event_data.get("keyCode")
            action = event_data.get("action")  # 0=press, 1=release
            repeat_count = event_data.get("repeatCount", 0)

            if key_code in BUTTON_MAP:
                button_name = BUTTON_MAP[key_code]
                is_pressed = (action == 0)
                self.button_states[key_code] = is_pressed

                payload = {
                    "device": self.name,
                    "button": button_name,
                    "action": "pressed" if is_pressed else "released",
                    "repeat_count": repeat_count,
                    "key_code": key_code,
                    "timestamp": datetime.now().isoformat(),
                }

                # Fire bus event and dispatcher signal
                self.hass.bus.async_fire(EVENT_BUTTON_PRESSED, payload)
                async_dispatcher_send(self.hass, SIGNAL_BUTTON_EVENT, payload)

                _LOGGER.info(f"Button {button_name} {'pressed' if is_pressed else 'released'}")
            else:
                _LOGGER.warning(f"Unknown button keyCode: {key_code}")

        except Exception as e:
            _LOGGER.error(f"Error handling button event: {e}")

    async def _handle_relay_change(self, data: Dict[str, Any]):
        """Handle relay status change."""
        try:
            relay_data_list = data.get("data", [])

            if not isinstance(relay_data_list, list):
                _LOGGER.error(f"Invalid relay data format: {relay_data_list}")
                return

            for relay_data in relay_data_list:
                relay_num = relay_data.get("num")
                state = relay_data.get("val", False)

                if relay_num in self.relay_states:
                    self.relay_states[relay_num] = state

                    payload = {
                        "device": self.name,
                        "relay": relay_num + 1,
                        "state": "on" if state else "off",
                        "timestamp": datetime.now().isoformat(),
                    }

                    # Fire bus event and dispatcher
                    self.hass.bus.async_fire(EVENT_RELAY_CHANGED, payload)
                    async_dispatcher_send(self.hass, SIGNAL_RELAY_UPDATE, self.relay_states)

                    _LOGGER.info(f"Relay {relay_num + 1}: {'ON' if state else 'OFF'}")
                else:
                    _LOGGER.debug(f"Ignoring relay {relay_num} (unsupported index)")

        except Exception as e:
            _LOGGER.error(f"Error handling relay change: {e}")

    async def _handle_backlight_change(self, data: Dict[str, Any]):
        """Handle backlight status change and notify listeners."""
        try:
            backlight_data_list = data.get("data", [])

            if not isinstance(backlight_data_list, list):
                _LOGGER.error(f"Invalid backlight data format: {backlight_data_list}")
                return

            for light_data in backlight_data_list:
                button_num = light_data.get("num")
                value = light_data.get("val", 0)

                if 0 <= button_num <= 3:
                    old_value = self.backlight_states.get(button_num, 0)
                    self.backlight_states[button_num] = value
                    if old_value != value:
                        _LOGGER.info(
                            f"Button {button_num + 1} backlight changed: {BACKLIGHT_COLORS.get(value, 'unknown')}"
                        )
                else:
                    _LOGGER.warning(f"Invalid button number in backlight data: {button_num}")

            # Notify listeners about backlight state change
            async_dispatcher_send(self.hass, SIGNAL_BACKLIGHT_UPDATE, self.backlight_states)

        except Exception as e:
            _LOGGER.error(f"Error handling backlight change: {e}")

    async def _handle_proximity(self, data: Dict[str, Any]):
        """Handle proximity sensor event."""
        try:
            detected = data.get("data", False)
            self.proximity_state = bool(detected)

            payload = {
                "device": self.name,
                "detected": self.proximity_state,
                "timestamp": datetime.now().isoformat(),
            }

            # Fire bus event and dispatcher
            self.hass.bus.async_fire(EVENT_PROXIMITY_DETECTED, payload)
            async_dispatcher_send(self.hass, SIGNAL_PROXIMITY_UPDATE, self.proximity_state)

            _LOGGER.info(f"Proximity sensor: {'detected' if self.proximity_state else 'clear'}")

        except Exception as e:
            _LOGGER.error(f"Error handling proximity event: {e}")

    async def _query_initial_states(self):
        """Query initial device states (relays and backlights)."""
        try:
            await self._send_message({"type": MSG_TYPE_RELAY_QUERY})
            await asyncio.sleep(0.2)
            await self._send_message({"type": MSG_TYPE_BACKLIGHT_CHANGE if False else 12})
            _LOGGER.debug("Initial state queries sent")
        except Exception as err:
            _LOGGER.error(f"Error querying initial states: {err}")

    async def _send_message(self, data: Dict[str, Any]) -> bool:
        """Send JSON message to iPano, terminated with newline."""
        if not self.connected or not self.writer:
            _LOGGER.warning("Cannot send message - not connected to iPano")
            return False

        try:
            message = json.dumps(data) + "\n"
            self.writer.write(message.encode())
            await self.writer.drain()
            _LOGGER.debug(f"Sent: {data}")
            return True
        except Exception as e:
            _LOGGER.error(f"Error sending message: {e}")
            self.connected = False
            return False

    # Public API methods used by services and entities
    async def async_wake_screen(self) -> bool:
        success = await self._send_message({"type": MSG_TYPE_SCREEN_WAKE})
        if success:
            _LOGGER.info("Screen wake command sent")
        return success

    async def async_set_backlight(self, button: str, color: str) -> bool:
        color_map = {"off": 0, "white": 1, "yellow": 2, "both": 3}
        value = color_map.get(color.lower(), 0)

        if isinstance(button, str) and button.lower() == "all":
            return await self.async_set_all_backlights(color)

        try:
            btn_num = int(button) - 1
            if 0 <= btn_num <= 3:
                return await self._send_message(
                    {"type": MSG_TYPE_BACKLIGHT_CONTROL, "data": {"num": btn_num, "val": value}}
                )
        except Exception:
            _LOGGER.error("Invalid button argument for set_backlight")

        return False

    async def async_set_all_backlights(self, color: str) -> bool:
        color_map = {"off": 0, "white": 1, "yellow": 2, "both": 3}
        value = color_map.get(color.lower(), 0)
        success = True
        for btn_num in range(4):
            ok = await self._send_message(
                {"type": MSG_TYPE_BACKLIGHT_CONTROL, "data": {"num": btn_num, "val": value}}
            )
            success = success and ok
            await asyncio.sleep(0.05)
        return success

    async def async_control_relay(self, relay: int, state: bool) -> bool:
        try:
            relay_num = int(relay) - 1
            if relay_num in self.relay_states:
                success = await self._send_message(
                    {"type": MSG_TYPE_RELAY_CONTROL, "data": {"num": relay_num, "val": bool(state)}}
                )
                if success:
                    _LOGGER.info(f"Relay {relay} set to {'ON' if state else 'OFF'}")
                return success
            else:
                _LOGGER.error(f"Invalid relay number: {relay}")
                return False
        except Exception as e:
            _LOGGER.error(f"Error controlling relay: {e}")
            return False

    async def async_stop(self):
        """Stop the bridge connection and cancel tasks."""
        _LOGGER.info("Stopping iPano Plus bridge")
        self.connected = False

        if self.listen_task:
            self.listen_task.cancel()
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
        if self.reconnect_task:
            self.reconnect_task.cancel()

        if self.writer:
            try:
                self.writer.close()
                try:
                    await self.writer.wait_closed()
                except Exception:
                    pass
            except Exception:
                pass

        _LOGGER.info("iPano Plus bridge stopped")

    async def async_get_connection_status(self) -> Dict[str, Any]:
        """Get current connection status."""
        return {
            "connected": self.connected,
            "host": self.host,
            "port": self.port,
            "last_heartbeat": self.last_heartbeat,
            "buttons": self.button_states,
            "relays": self.relay_states,
            "proximity": self.proximity_state,
        }
