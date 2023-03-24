"""Constants for the Livisi Smart Home integration."""
import logging
from typing import Final

LOGGER = logging.getLogger(__package__)
DOMAIN = "livisi"

LIVISI_EVENT = f"{DOMAIN}_event"

CONF_HOST = "host"
CONF_PASSWORD: Final = "password"
AVATAR = "Avatar"
AVATAR_PORT: Final = 9090
CLASSIC_PORT: Final = 8080
DEVICE_POLLING_DELAY: Final = 60
LIVISI_STATE_CHANGE: Final = "livisi_state_change"
LIVISI_REACHABILITY_CHANGE: Final = "livisi_reachability_change"

SWITCH_DEVICE_TYPES: Final = ["ISS", "ISS2", "PSS", "PSSO"]
BUTTON_DEVICE_TYPES: Final = ["ISS2", "WSS2", "BRM8"]
MOTION_DEVICE_TYPES: Final = ["WMD", "WMDO"]
VRCC_DEVICE_TYPE: Final = "VRCC"

EVENT_BUTTON_PRESSED = "button_pressed"
EVENT_MOTION_DETECTED = "motion_detected"

MAX_TEMPERATURE: Final = 30.0
MIN_TEMPERATURE: Final = 6.0
