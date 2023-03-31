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

from .const import BUTTON_COUNT, CONF_SUBTYPE

from . import DOMAIN

from .const import (
    MOTION_DEVICE_TYPES,
    LIVISI_EVENT,
)

BUTTON_TRIGGER_TYPES = {"button_press", "button_long_press"}

MOTION_TRIGGER_TYPES = {
    "motion_detected",
}

BUTTON_TRIGGER_SUBTYPES = {
    f"button_{idx}" for idx in range(1, max(BUTTON_COUNT.values()) + 1)
}

TRIGGER_SCHEMA = DEVICE_TRIGGER_BASE_SCHEMA.extend(
    {
        vol.Optional(CONF_ENTITY_ID): cv.entity_id,
        vol.Required(CONF_TYPE): vol.In(BUTTON_TRIGGER_TYPES | MOTION_TRIGGER_TYPES),
        vol.Optional(CONF_SUBTYPE): vol.In(BUTTON_TRIGGER_SUBTYPES),
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

    buttons = BUTTON_COUNT.get(dev.model)
    if buttons is not None:
        triggers += [
            {
                CONF_PLATFORM: "device",
                CONF_DEVICE_ID: device_id,
                CONF_DOMAIN: DOMAIN,
                CONF_TYPE: trigger_type,
                CONF_SUBTYPE: trigger_subtype,
            }
            for trigger_type in BUTTON_TRIGGER_TYPES
            for trigger_subtype in {f"button_{idx}" for idx in range(1, buttons + 1)}
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

    trigger = config[CONF_TYPE]

    event_data = {
        CONF_TYPE: trigger,
        CONF_DEVICE_ID: config[CONF_DEVICE_ID],
    }

    if trigger in BUTTON_TRIGGER_TYPES:
        event_data["button_index"] = int(trigger.split("_")[1])
        event_data["press_type"] = (
            "LongPress" if trigger.find("long_press" != -1) else "ShortPress"
        )

    event_config = event_trigger.TRIGGER_SCHEMA(
        {
            event_trigger.CONF_PLATFORM: CONF_EVENT,
            event_trigger.CONF_EVENT_TYPE: LIVISI_EVENT,
            event_trigger.CONF_EVENT_DATA: event_data,
        }
    )
    return await event_trigger.async_attach_trigger(
        hass, event_config, action, trigger_info, platform_type="device"
    )
