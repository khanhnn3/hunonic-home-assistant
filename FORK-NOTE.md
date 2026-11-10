# FORK NOTE — bản sửa sdoor (1.14.2)

Bản này dựa trên **vietnam-hunonic v1.14.1** của tác giả gốc
(github.com/home-assistant-plugins/vietnam-hunonic, giấy phép MIT — giữ nguyên
LICENSE và ghi công tác giả gốc; bản sửa chỉ dùng cá nhân, phi thương mại,
đúng tinh thần lưu ý trong README của repo gốc).

## Vấn đề

Thiết bị cửa cuốn Hunonic Smart Door đời đầu (root_type `sdoor` / `sdoor1`,
firmware 211205) trong Home Assistant chỉ có 4 sensor chẩn đoán (kết nối,
MAC Bluetooth, phiên bản, thông báo offline) — **không có entity cover** để
điều khiển, dù app Hunonic điều khiển bình thường và cổng (gate) vẫn có cover.

## Nguyên nhân gốc

`custom_components/hunonic/const.py`, hằng `DOOR_TYPES`: bản 1.14.1 chỉ liệt
kê `sdoor2`–`sdoor12` (và còn thiếu `sdoor11`), **thiếu toàn bộ họ sdoor thế hệ
đầu/tên gốc**: `sdoor`, `sdoor1`, `sdoorv2`, `sdoorpro` — trong khi chính
`docs/api.md` của repo tài liệu hóa lệnh điều khiển cửa cuốn
`{"sdr": <action>, "u": <userId>, "src": 1}` (1=mở, 2=đóng, 3=dừng, 4=khóa,
5=mở khóa) cho đúng nhóm `sdoor, sdoorv2, sdoorpro`.

Hệ quả dây chuyền: `cover.py` (`_build`) trả danh sách rỗng cho các thiết bị
này → không tạo `HunonicDoor`; `sensor.py` (`_COVER_TYPES` gồm `DOOR_TYPES`)
cũng bỏ qua → không có cả sensor vị trí.

## Thay đổi (so với v1.14.1)

1. `custom_components/hunonic/const.py` — `DOOR_TYPES`: thêm `sdoor`,
   `sdoor1`, `sdoorv2`, `sdoorpro` và `sdoor11`.
2. `hunonic/models.py` — `_DOOR_TYPES`: đồng bộ cùng danh sách (thư viện
   client dùng chung; integration HA không import trực tiếp lúc chạy).
3. `custom_components/hunonic/manifest.json` — version `1.14.1` → `1.14.2`.
4. `custom_components/hunonic/cover.py` — chỉ sửa docstring của
   `HunonicDoor` cho khớp phạm vi mới. **Không sửa logic gửi lệnh**: class
   `HunonicDoor` có sẵn đã gửi đúng payload tài liệu hóa trong docs/api.md,
   gồm cả đặt vị trí `{"sdr": 1|2, "pcn": <0-100>}`.

Sau khi sửa, thiết bị sdoor/sdoor1 sẽ có: entity **cover** (mở/đóng/dừng/đặt
vị trí %, device_class shutter) + sensor **"Vị trí" (%)** đọc từ trường `pcn`
của state — cùng cơ chế các bản sdoor2–sdoor12 đang dùng.

## Đã kiểm chứng

- `python3 -m py_compile` toàn bộ file .py: OK.
- Test độc lập (`test_sdoor_fix.py`, stub tối thiểu Home Assistant, nạp code
  thật của const.py/cover.py):
  - Bản gốc 1.14.1: sdoor/sdoor1 KHÔNG thuộc DOOR_TYPES (tái hiện lỗi).
  - Bản sửa 1.14.2: payload mở/đóng/dừng lần lượt là `{"sdr":1|2|3,"u":uid,
    "src":1}`; đặt vị trí gửi kèm `pcn`; parse state `{"pcn":72}` → vị trí
    72, chưa đóng; `{"pcn":0}` → đã đóng; không có `pcn` → None. PASS.

## Chưa kiểm chứng / lưu ý

- Chưa chạy trên Home Assistant thật với thiết bị vật lý: việc thiết bị
  sdoor đời đầu có chấp nhận lệnh `sdr` và có báo `pcn` trong state hay không
  cần xác nhận trên máy thật (docs của repo ghi lệnh này cho họ sdoor, nhưng
  tác giả chưa từng map chúng vào cover nên có thể chưa test thực tế).
- Chỉ số **"Ô thoáng %"** mà app Hunonic hiển thị: không tìm thấy trường
  tương ứng trong code/docs của repo (chỉ có `pcn` = % độ mở) → **không thêm**,
  tránh bịa protocol.

---

## Bổ sung v1.14.3 — nút Khóa / Mở khóa cho cửa cuốn

### Vấn đề

Bản gốc (và bản fork 1.14.2) điều khiển cửa cuốn họ `sdoor` được
mở / đóng / dừng / đặt vị trí, nhưng **không có cách bấm KHÓA / MỞ KHÓA**
trong Home Assistant — người dùng phải mở app Hunonic để khóa điều khiển
cửa. Donald yêu cầu bổ sung nút khóa khi dùng dashboard điều khiển cửa
cuốn ("điều khiển cửa cuốn thiết nút khoá" — 2026-11-11).

### Cơ sở giao thức (không bịa)

`docs/api.md` của repo tài liệu hóa đầy đủ lệnh cửa cuốn
`{"sdr": <action>, "u": <userId>, "src": 1}` với **4 = khóa, 5 = mở khóa**;
`custom_components/hunonic/cover.py` cũng đã khai báo sẵn hằng
`DOOR_LOCK = 4` / `DOOR_UNLOCK = 5` nhưng không dùng ở đâu — class
`HunonicDoor` không có method khóa, và Home Assistant không có service
cover nào tương ứng khóa. Cách đúng chuẩn HA: tạo **button entity**.

### Thay đổi (so với v1.14.2)

1. `custom_components/hunonic/button.py` — **file mới**: platform `button`.
   Mỗi thiết bị thuộc `DOOR_TYPES` có thêm 2 entity:
   - `<tên cửa> - Khóa` — `unique_id = hunonic_button_<device_id>_lock`,
     icon `mdi:lock`, bấm gửi `{"sdr": 4, "u": <userId>, "src": 1}`.
   - `<tên cửa> - Mở khóa` — `unique_id = hunonic_button_<device_id>_unlock`,
     icon `mdi:lock-open-variant`, bấm gửi `{"sdr": 5, "u": <userId>, "src": 1}`.
   Hai nút dùng chung `device_info` (identifiers theo `root_id`) với cover
   nên nằm cùng một thiết bị trong HA; `available` theo trạng thái online
   của coordinator như các platform khác.
2. `custom_components/hunonic/const.py` — `PLATFORMS`: thêm `"button"`
   (ngay sau `"cover"`).
3. `custom_components/hunonic/manifest.json` — version `1.14.2` → `1.14.3`.

### Đã kiểm chứng

- `python3 -m py_compile` toàn bộ file .py: OK.
- Test độc lập (`test_button_lock.py`, stub tối thiểu Home Assistant, nạp
  code thật của const.py/button.py): thiết bị `sdoor1` tạo đúng 2 nút,
  thiết bị công tắc `wsdatic3v` tạo 0 nút; bấm Khóa gửi đúng
  `{"sdr": 4, "u": uid, "src": 1}`, bấm Mở khóa gửi `sdr: 5`; tên /
  unique_id / icon đúng đặc tả. PASS.

### Chưa kiểm chứng / lưu ý

- Chưa chạy trên thiết bị vật lý: bộ điều khiển sdoor đời đầu (fw 211205)
  có thực thi lệnh khóa `sdr: 4/5` hay không cần xác nhận trên cửa thật —
  giao thức có tài liệu và app Hunonic có nút khóa, nhưng entity button là
  đường gửi mới từ HA.
