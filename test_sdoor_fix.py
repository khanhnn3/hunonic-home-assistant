"""Test độc lập cho bản sửa sdoor (không cần cài Home Assistant).

Cách chạy:
  python3 test_sdoor_fix.py <thư_mục_hunonic> <door|nodoor>
  - door   : kỳ vọng root_type sdoor/sdoor1 ĐƯỢC tạo cover (bản đã sửa)
  - nodoor : kỳ vọng KHÔNG được tạo cover (bản gốc 1.14.1, để đối chứng)

Test nạp const.py + cover.py THẬT của integration (chỉ stub các module
homeassistant.* và coordinator), kiểm tra:
  1. Điều kiện phân loại trong cover.async_setup_entry (DOOR_TYPES).
  2. Payload lệnh open/close/stop/set_position của HunonicDoor.
  3. Parse state: current_cover_position / is_closed từ state {"pcn": ...}.
"""
import asyncio
import enum
import importlib
import sys
import types
from pathlib import Path


def install_stubs() -> None:
    ha = types.ModuleType("homeassistant")
    ha.__path__ = []
    sys.modules["homeassistant"] = ha

    comp = types.ModuleType("homeassistant.components")
    comp.__path__ = []
    sys.modules["homeassistant.components"] = comp

    cover_mod = types.ModuleType("homeassistant.components.cover")

    class CoverDeviceClass(enum.Enum):
        GARAGE = "garage"
        SHUTTER = "shutter"

    class CoverEntity:
        pass

    class CoverEntityFeature(enum.IntFlag):
        OPEN = 1
        CLOSE = 2
        STOP = 8
        SET_POSITION = 4
        OPEN_TILT = 16
        CLOSE_TILT = 32
        STOP_TILT = 64
        SET_TILT_POSITION = 128

    cover_mod.CoverDeviceClass = CoverDeviceClass
    cover_mod.CoverEntity = CoverEntity
    cover_mod.CoverEntityFeature = CoverEntityFeature
    sys.modules["homeassistant.components.cover"] = cover_mod

    ce = types.ModuleType("homeassistant.config_entries")

    class ConfigEntry:
        pass

    ce.ConfigEntry = ConfigEntry
    sys.modules["homeassistant.config_entries"] = ce

    core = types.ModuleType("homeassistant.core")

    class HomeAssistant:
        pass

    def callback(fn):
        return fn

    core.HomeAssistant = HomeAssistant
    core.callback = callback
    sys.modules["homeassistant.core"] = core

    helpers = types.ModuleType("homeassistant.helpers")
    helpers.__path__ = []
    sys.modules["homeassistant.helpers"] = helpers

    dr = types.ModuleType("homeassistant.helpers.device_registry")

    class DeviceInfo(dict):
        pass

    dr.DeviceInfo = DeviceInfo
    sys.modules["homeassistant.helpers.device_registry"] = dr

    ep = types.ModuleType("homeassistant.helpers.entity_platform")
    ep.AddEntitiesCallback = object
    sys.modules["homeassistant.helpers.entity_platform"] = ep

    ent = types.ModuleType("homeassistant.helpers.entity")

    class Entity:
        pass

    ent.Entity = Entity
    sys.modules["homeassistant.helpers.entity"] = ent

    uc = types.ModuleType("homeassistant.helpers.update_coordinator")

    class CoordinatorEntity:
        def __init__(self, coordinator=None):
            self.coordinator = coordinator

        def __class_getitem__(cls, item):
            return cls

    uc.CoordinatorEntity = CoordinatorEntity
    sys.modules["homeassistant.helpers.update_coordinator"] = uc


class FakeCoordinator:
    """Ghi lại payload điều khiển + cấp state mẫu."""

    def __init__(self) -> None:
        self._user_id = 12345
        self.sent: list[tuple] = []
        self.state: dict = {}
        self.raw: dict = {}

    async def async_control_device(self, device, payload, use_gateway=False):
        self.sent.append((device, payload, use_gateway))

    def get_device_state(self, root_id):
        return self.state

    def get_device_raw(self, device_id):
        return self.raw

    def is_device_online(self, device_id):
        return True


def main() -> int:
    tree = Path(sys.argv[1]).resolve()
    expect = sys.argv[2]
    install_stubs()

    pkg = types.ModuleType("hpkg")
    pkg.__path__ = [str(tree)]
    sys.modules["hpkg"] = pkg

    # Stub coordinator để cover.py không kéo theo MQTT/API thật.
    coord_stub = types.ModuleType("hpkg.coordinator")

    class HunonicCoordinator:
        pass

    coord_stub.HunonicCoordinator = HunonicCoordinator
    sys.modules["hpkg.coordinator"] = coord_stub

    const = importlib.import_module("hpkg.const")
    cover = importlib.import_module("hpkg.cover")

    failures = []

    # 1) Phân loại root_type (đúng điều kiện _build trong cover.py)
    # Các type MỚI thêm ở 1.14.2 — bản gốc phải KHÔNG có, bản sửa phải CÓ.
    for rt in ("sdoor", "sdoor1", "sdoorv2", "sdoorpro", "sdoor11"):
        is_door = rt in const.DOOR_TYPES
        if expect == "door" and not is_door:
            failures.append(f"root_type {rt!r} KHÔNG thuộc DOOR_TYPES (sẽ không có cover)")
        if expect == "nodoor" and is_door:
            failures.append(f"root_type {rt!r} thuộc DOOR_TYPES ngoài kỳ vọng nodoor")
    # Các type CŨ (đã có từ 1.14.1) — phải thuộc DOOR_TYPES ở cả hai bản.
    for rt in ("sdoor2", "sdoor12"):
        if rt not in const.DOOR_TYPES:
            failures.append(f"root_type cũ {rt!r} bị mất khỏi DOOR_TYPES")
    print(f"DOOR_TYPES = {const.DOOR_TYPES}")

    if expect == "nodoor":
        if failures:
            print("ĐỐI CHỨNG GỐC: FAIL bất ngờ:", failures)
            return 1
        print("ĐỐI CHỨNG GỐC OK: sdoor/sdoor1 bị bỏ qua đúng như đã chẩn đoán trên HA thật.")
        return 0

    # 2) Payload lệnh của HunonicDoor
    device = {
        "id": "dev1",
        "root_id": "HUN1653006659sdoor1",
        "root_type": "sdoor1",
        "name": "Cửa cuốn",
        "home_id": 1,
    }
    fake = FakeCoordinator()
    ent = object.__new__(cover.HunonicDoor)
    ent._device = device
    ent._device_id = "dev1"
    ent._root_id = device["root_id"]
    ent._root_type = "sdoor1"
    ent.coordinator = fake

    async def run_cmds():
        await ent.async_open_cover()
        await ent.async_close_cover()
        await ent.async_stop_cover()
        await ent.async_set_cover_position(position=72)
        await ent.async_set_cover_position(position=0)

    asyncio.run(run_cmds())
    payloads = [p for (_d, p, _g) in fake.sent]
    expected = [
        {"sdr": 1, "u": 12345, "src": 1},
        {"sdr": 2, "u": 12345, "src": 1},
        {"sdr": 3, "u": 12345, "src": 1},
        {"sdr": 1, "u": 12345, "src": 1, "pcn": 72},
        {"sdr": 2, "u": 12345, "src": 1, "pcn": 0},
    ]
    print("Payloads gửi đi:", payloads)
    if payloads != expected:
        failures.append(f"Payload lệch kỳ vọng: {payloads} != {expected}")

    # 3) Parse state vị trí
    fake.state = {"pcn": 72}
    if ent.current_cover_position != 72 or ent.is_closed is not False:
        failures.append(f"Parse pcn=72 sai: pos={ent.current_cover_position} is_closed={ent.is_closed}")
    fake.state = {"pcn": 0}
    if ent.current_cover_position != 0 or ent.is_closed is not True:
        failures.append(f"Parse pcn=0 sai: pos={ent.current_cover_position} is_closed={ent.is_closed}")
    fake.state = {}
    if ent.current_cover_position is not None:
        failures.append(f"Không có pcn phải trả None, nhận {ent.current_cover_position}")
    print("Parse state: pcn=72 ->", 72, "| pcn=0 -> đóng | không có pcn -> None : OK")

    # 4) Gate không bị ảnh hưởng
    if "gate" not in const.GATE_TYPES or "gatehun" not in const.GATE_HUB_TYPES:
        failures.append("GATE_TYPES/GATE_HUB_TYPES bị thay đổi ngoài ý muốn")

    if failures:
        print("FAIL:", failures)
        return 1
    print("PASS: sdoor/sdoor1 có cover; payload mở/đóng/dừng/đặt-vị-trí đúng docs/api.md; parse pcn đúng.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
