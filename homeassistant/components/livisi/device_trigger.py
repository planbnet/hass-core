"""Provides device triggers for LIVISI Smart Home."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components.device_automation import DEVICE_TRIGGER_BASE_SCHEMA
from homeassistant.components.homeassistant.triggers import event as event_trigger
from homeassistant.const import (
    CONF_DEVICE_ID,
    CONF_DOMAIN,
    CONF_ENTITY_ID,
    CONF_EVENT,
    CONF_PLATFORM,
    CONF_TYPE,
)
from homeassistant.core import CALLBACK_TYPE, HomeAssistant

from homeassistant.helpers import (
    config_validation as cv,
    device_registry as dr,
)
from homeassistant.helpers.trigger import TriggerActionType, TriggerInfo
from homeassistant.helpers.typing import ConfigType

from . import DOMAIN

from .const import (
    BUTTON_DEVICE_TYPES,
    EVENT_BUTTON_PRESSED,
    EVENT_MOTION_DETECTED,
    MOTION_DEVICE_TYPES,
    LIVISI_EVENT,
)

BUTTON_TRIGGER_TYPES = {
    "button_1_pressed",
    "button_2_pressed",
    "button_1_long_pressed",
    "button_2_long_pressed",
}

MOTION_TRIGGER_TYPES = {
    "motion_detected",
}

TRIGGER_TYPES = BUTTON_TRIGGER_TYPES.union(MOTION_TRIGGER_TYPES)

TRIGGER_SCHEMA = DEVICE_TRIGGER_BASE_SCHEMA.extend(
    {
        vol.Optional(CONF_ENTITY_ID): cv.entity_id,
        vol.Required(CONF_TYPE): vol.In(TRIGGER_TYPES),
    }
)


async def async_get_triggers(
    hass: HomeAssistant, device_id: str
) -> list[dict[str, Any]]:
    """List device triggers for LIVISI Smart Home devices."""

    dev_reg: dr.DeviceRegistry = dr.async_get(hass)
    if (dev := dev_reg.async_get(device_id)) is None:
        raise ValueError(f"Device ID {device_id} is not valid")

    triggers = []

    if dev.model in BUTTON_DEVICE_TYPES:
        triggers += [
            {
                CONF_PLATFORM: "device",
                CONF_DEVICE_ID: device_id,
                CONF_DOMAIN: DOMAIN,
                CONF_TYPE: trigger_type,
            }
            for trigger_type in BUTTON_TRIGGER_TYPES
        ]

    if dev.model in MOTION_DEVICE_TYPES:
        triggers += [
            {
                CONF_PLATFORM: "device",
                CONF_DEVICE_ID: device_id,
                CONF_DOMAIN: DOMAIN,
                CONF_TYPE: trigger_type,
            }
            for trigger_type in MOTION_TRIGGER_TYPES
        ]

    return triggers


async def async_attach_trigger(
    hass: HomeAssistant,
    config: ConfigType,
    action: TriggerActionType,
    trigger_info: TriggerInfo,
) -> CALLBACK_TYPE:
    """Attach a trigger."""

    if config[CONF_TYPE] in BUTTON_TRIGGER_TYPES:
        button_index = 1
        press_type = "ShortPress"
        if config[CONF_TYPE] == "button_1_pressed":
            button_index = 1
        elif config[CONF_TYPE] == "button_2_pressed":
            button_index = 2
        elif config[CONF_TYPE] == "button_1_long_pressed":
            button_index = 1
            press_type = "LongPress"
        elif config[CONF_TYPE] == "button_2_long_pressed":
            button_index = 2
            press_type = "LongPress"

        event_config = event_trigger.TRIGGER_SCHEMA(
            {
                event_trigger.CONF_PLATFORM: CONF_EVENT,
                event_trigger.CONF_EVENT_TYPE: LIVISI_EVENT,
                event_trigger.CONF_EVENT_DATA: {
                    CONF_TYPE: EVENT_BUTTON_PRESSED,
                    CONF_DEVICE_ID: config[CONF_DEVICE_ID],
                    "button_index": button_index,
                    "press_type": press_type,
                },
            }
        )
        return await event_trigger.async_attach_trigger(
            hass, event_config, action, trigger_info, platform_type="device"
        )
    elif config[CONF_TYPE] in MOTION_TRIGGER_TYPES:
        event_config = event_trigger.TRIGGER_SCHEMA(
            {
                event_trigger.CONF_PLATFORM: CONF_EVENT,
                event_trigger.CONF_EVENT_TYPE: LIVISI_EVENT,
                event_trigger.CONF_EVENT_DATA: {
                    CONF_TYPE: EVENT_MOTION_DETECTED,
                    CONF_DEVICE_ID: config[CONF_DEVICE_ID],
                },
            }
        )
        return await event_trigger.async_attach_trigger(
            hass, event_config, action, trigger_info, platform_type="device"
        )
