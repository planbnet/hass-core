"""Provides device triggers for LIVISI Smart Home."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components.automation import (
    AutomationActionType,
    AutomationTriggerInfo,
)
from homeassistant.components.device_automation import DEVICE_TRIGGER_BASE_SCHEMA
from homeassistant.components.homeassistant.triggers import state as state_trigger
from homeassistant.const import (
    CONF_DEVICE_ID,
    CONF_DOMAIN,
    CONF_ENTITY_ID,
    CONF_PLATFORM,
    CONF_TYPE,
    STATE_OFF,
    STATE_ON,
)
from homeassistant.core import CALLBACK_TYPE, HomeAssistant
from homeassistant.helpers import (
    config_validation as cv,
    entity_registry as er,
    device_registry as dr,
)
from homeassistant.helpers.typing import ConfigType

from . import DOMAIN

TRIGGER_TYPES = {"button_pressed"}

TRIGGER_SCHEMA = DEVICE_TRIGGER_BASE_SCHEMA.extend(
    {
        vol.Required(CONF_ENTITY_ID): cv.entity_id,
        vol.Required(CONF_TYPE): vol.In(TRIGGER_TYPES),
    }
)


async def async_get_triggers(
    hass: HomeAssistant, device_id: str
) -> list[dict[str, Any]]:
    """List device triggers for LIVISI Smart Home devices."""
    device_registry = dr.async_get(hass)

    # TODO: Define devices without entities https://developers.home-assistant.io/docs/device_registry_index/#defining-devices

    # TODO: get device via unique id (device_id passed to this function is something that hass assigns it seems)
    dev = device_registry.async_get(device_id)
    if dev is None:
        return None

"""     {"area_id":"garten",
     "configuration_url":null,
     "config_entries":["ed69a6e8a98208ed85df8d40b5ba53e5"],
     "connections":[],
     "disabled_by":null,
     "entry_type":null,
     "hw_version":null,
     "id":"60749597315e0ab0340d4db88ccf20c9",
     "identifiers":[["livisi","9a47b6ef43f940e8aa022ded47d32199"]],
     "manufacturer":"RWE",
     "model":"PSSO",
     "name_by_user":null,
     "name":"Lichterkette",
     "sw_version":null,
     "via_device_id":null}'
 """

    # TODO: Check device type and add button pressed action if it is appropriate

    # In a first shot, we should get this working for the button_pressed events of the ISS2 wall switch,
    # as that one has a supported device

    return [
        {
            CONF_PLATFORM: "device",
            CONF_DEVICE_ID: device_id,
            CONF_DOMAIN: DOMAIN,
            CONF_TYPE: "button_pressed",
        }
    ]


async def async_attach_trigger(
    hass: HomeAssistant,
    config: ConfigType,
    action: AutomationActionType,
    automation_info: AutomationTriggerInfo,
) -> CALLBACK_TYPE:
    """Attach a trigger."""
    # TODO Implement your own logic to attach triggers.
    # Use the existing state or event triggers from the automation integration.

    if config[CONF_TYPE] == "turned_on":
        to_state = STATE_ON
    else:
        to_state = STATE_OFF

    state_config = {
        state_trigger.CONF_PLATFORM: "state",
        CONF_ENTITY_ID: config[CONF_ENTITY_ID],
        state_trigger.CONF_TO: to_state,
    }
    state_config = await state_trigger.async_validate_trigger_config(hass, state_config)
    return await state_trigger.async_attach_trigger(
        hass, state_config, action, automation_info, platform_type="device"
    )
