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
