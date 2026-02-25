"""Constants for the iPano Plus integration."""

DOMAIN = "ipano_plus"

# Defaults
DEFAULT_PORT = 3124
DEFAULT_NAME = "iPano Plus"
DEFAULT_HOST = "192.168.2.120"

# Configuration keys
CONF_HOST = "host"
CONF_PORT = "port"
CONF_NAME = "name"

# Message types
MSG_TYPE_BUTTON = 0
MSG_TYPE_BACKLIGHT_CHANGE = 10
MSG_TYPE_BACKLIGHT_CONTROL = 11
MSG_TYPE_SCREEN_WAKE = 20
MSG_TYPE_FOREGROUND_QUERY = 30
MSG_TYPE_START_APPLICATION = 40
MSG_TYPE_RELAY_CHANGE = 50
MSG_TYPE_RELAY_CONTROL = 51
MSG_TYPE_RELAY_QUERY = 52
MSG_TYPE_PROXIMITY = 60
MSG_TYPE_PROXIMITY_SET = 61
MSG_TYPE_PROXIMITY_QUERY = 62
MSG_TYPE_HEARTBEAT = 500

# For 6-inch iPano Plus
NUM_BUTTONS = 4
NUM_RELAYS = 2
BUTTON_KEYCODES = [131, 132, 133, 134]

# Button mappings
BUTTON_MAP = {
    131: "button_1",
    132: "button_2",
    133: "button_3",
    134: "button_4",
}

# Backlight colors
BACKLIGHT_COLORS = {
    0: "off",
    1: "white",
    2: "yellow",
    3: "both",
}

# Events (bus + dispatcher keys)
EVENT_BUTTON_PRESSED = "ipano_button_pressed"
EVENT_PROXIMITY_DETECTED = "ipano_proximity_detected"
EVENT_RELAY_CHANGED = "ipano_relay_changed"

# Dispatcher signals (internal)
SIGNAL_BACKLIGHT_UPDATE = f"{DOMAIN}_backlight_update"
SIGNAL_RELAY_UPDATE = f"{DOMAIN}_relay_update"
SIGNAL_BUTTON_EVENT = f"{DOMAIN}_button_event"
SIGNAL_PROXIMITY_UPDATE = f"{DOMAIN}_proximity_update"

# Service names
SERVICE_WAKE_SCREEN = "wake_screen"
SERVICE_SET_BACKLIGHT = "set_backlight"
SERVICE_SET_ALL_BACKLIGHTS = "set_all_backlights"
SERVICE_PULSE_BACKLIGHT = "pulse_backlight"
SERVICE_FADE_BACKLIGHT = "fade_backlight"
SERVICE_BREATHING_BACKLIGHT = "breathing_backlight"
SERVICE_CONTROL_RELAY = "control_relay"
