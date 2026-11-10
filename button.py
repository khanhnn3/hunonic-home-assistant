"""Nút bấm khóa / mở khóa cửa cuốn Hunonic cho Home Assistant.

Giao thức (docs/api.md): lệnh cửa cuốn gửi payload
{"sdr": <action>, "u": <userId>, "src": 1} — 1=mở, 2=đóng, 3=dừng,
4=KHÓA, 5=MỞ KHÓA. cover.py đã khai báo sẵn hằng DOOR_LOCK /
DOOR_UNLOCK nhưng bản gốc không tạo entity nào để người dùng bấm
khóa; bản fork 1.14.3 bổ sung 2 nút bấm cho mỗi thiết bị họ sdoor
(DOOR_TYPES), dùng chung thiết bị (device) với entity cover.

Khóa ở đây là khóa điều khiển trên bộ điều khiển cửa cuốn (như nút
khóa trong app Hunonic) — bấm nút chỉ gửi lệnh, cover không đổi
trạng thái mở/đóng.
"""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, DOOR_TYPES
from .coordinator import HunonicCoordinator
from .entity_setup import setup_entities

_LOGGER = logging.getLogger(__name__)

# ── Action codes cửa cuốn (khớp cover.py / docs/api.md) ──────────────────────
DOOR_LOCK = 4
DOOR_UNLOCK = 5


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Thiết lập button entities (tự thêm thiết bị mới khi danh sách thay đổi)."""
    def _build(coordinator: HunonicCoordinator, device: dict[str, Any]):
        if device.get("root_type", "") in DOOR_TYPES:
            return [
                HunonicDoorLockButton(coordinator, device),
                HunonicDoorUnlockButton(coordinator, device),
            ]
        return []

    setup_entities(hass, entry, async_add_entities, _build)


class _HunonicDoorButtonBase(CoordinatorEntity[HunonicCoordinator], ButtonEntity):
    """Base class cho nút khóa / mở khóa cửa cuốn."""

    _action: int = 0
    _key: str = ""
    _suffix: str = ""

    def __init__(self, coordinator: HunonicCoordinator, device: dict[str, Any]) -> None:
        super().__init__(coordinator)
        self._device = device
        self._device_id: str = str(device.get("id", ""))
        self._root_id: str = str(device.get("root_id", ""))
        self._root_type: str = str(device.get("root_type", ""))

    @property
    def unique_id(self) -> str:
        return f"hunonic_button_{self._device_id}_{self._key}"

    @property
    def name(self) -> str:
        return f"{self._device.get('name', self._device_id)} - {self._suffix}"

    @property
    def device_info(self) -> DeviceInfo:
        info = DeviceInfo(
            identifiers={(DOMAIN, self._root_id)},
            name=str(self._device.get("name", self._device_id)),
            manufacturer="Hunonic",
            model=self._root_type,
        )
        hid = self._device.get("home_id")
        if hid:  # gom thiết bị dưới "trạm trung chuyển" của nhà
            info["via_device"] = (DOMAIN, f"home_{hid}")
        return info

    @property
    def available(self) -> bool:
        return self.coordinator.is_device_online(self._device_id)

    async def async_press(self) -> None:
        """Gửi lệnh khóa / mở khóa (sdr 4 / 5) đến cửa cuốn."""
        payload = {
            "sdr": self._action,
            "u": self.coordinator._user_id,
            "src": 1,
        }
        await self.coordinator.async_control_device(self._device, payload)


class HunonicDoorLockButton(_HunonicDoorButtonBase):
    """Nút khóa cửa cuốn (sdr = 4) — chặn điều khiển như nút khóa trên app."""

    _attr_icon = "mdi:lock"
    _action = DOOR_LOCK
    _key = "lock"
    _suffix = "Khóa"


class HunonicDoorUnlockButton(_HunonicDoorButtonBase):
    """Nút mở khóa cửa cuốn (sdr = 5)."""

    _attr_icon = "mdi:lock-open-variant"
    _action = DOOR_UNLOCK
    _key = "unlock"
    _suffix = "Mở khóa"
