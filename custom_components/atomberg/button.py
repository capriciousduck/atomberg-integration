"""Button platform for Atomberg integration."""

from logging import getLogger

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_CONTROL_METHOD, ControlMethod
from .coordinator import AtombergDataUpdateCoordinator
from .device import ATTR_BRIGHTNESS, AtombergDevice
from .entity import AtombergEntity, platform_async_setup_entry
from .ir_button import async_setup_entry as ir_async_setup_entry

_LOGGER = getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Atomberg button entities from a config entry."""
    if entry.data.get(CONF_CONTROL_METHOD) == ControlMethod.IR:
        await ir_async_setup_entry(hass, entry, async_add_entities)
    else:
        await platform_async_setup_entry(
            hass, entry, async_add_entities, AtombergFanButtonEntity
        )


class AtombergFanButtonEntity(AtombergEntity, ButtonEntity):
    """Button entity for Atomberg fans."""

    def __init__(
        self, coordinator: AtombergDataUpdateCoordinator, device: AtombergDevice
    ) -> None:
        """Init Button entity."""
        super().__init__(coordinator, device, _LOGGER)
        self._attr_name = self._device.name + " Toggle LED Brightness"
        self._attr_translation_key = "toggle_led_brightness"
        self._attr_unique_id = self._get_unique_id(Platform.BUTTON, "toggle_led_brightness")

        # We only want to show this if it supports brightness control
        self._attr_entity_registry_enabled_default = self._device.supports_brightness_control

    async def async_press(self) -> None:
        """Press the button."""
        current_brightness = self.device_state.get(ATTR_BRIGHTNESS, 100)

        if current_brightness >= 100:
            new_brightness = 50
        elif current_brightness >= 50:
            new_brightness = 10
        else:
            new_brightness = 100

        cmd = {ATTR_BRIGHTNESS: new_brightness}
        await self._device.async_send_light_command(cmd)
