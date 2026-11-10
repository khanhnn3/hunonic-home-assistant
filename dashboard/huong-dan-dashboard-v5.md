# Hướng dẫn cài Dashboard v5 — giao diện kiểu app Hunonic + đồng hồ, lịch dương, lịch âm

**V5 có gì mới:** thẻ thiết bị đổi sang **Mushroom** (ô to, icon + dòng "Đang bật/Đang tắt", icon xanh lá khi bật — giống app hãng), trên cùng có **header đồng hồ + lịch dương + ÂM LỊCH chữ to**. Có 2 bản sẵn: `dashboard-dieu-khien-nha.yaml` (**2 ô/hàng**, mặc định) và `dashboard-3-cot.yaml` (**3 ô/hàng**). Làm lần lượt từng bước, bước nào xong mới sang bước sau.

---

## Bước 1 — Cài Mushroom (bắt buộc, làm 1 lần)

1. Mở Home Assistant → **Cài đặt (Settings) → Chợ (Marketplace)**.
2. Tìm **"Mushroom"** → mở ra → **Tải xuống / Cài đặt (Download)**.
3. Cài xong, tải lại trang (trên trình duyệt: `Ctrl + F5`; trên app điện thoại: đóng app mở lại).

> Chưa cài Mushroom mà dán dashboard trước thì các thẻ sẽ báo lỗi "Custom element doesn't exist" — cứ quay lại bước này là hết.

## Bước 2 — Cài bản vá Hunonic 1.14.2 (cho thẻ Cửa cuốn)

Làm theo file **`huong-dan-cai-ban-sua-sdoor.md`** đã có. Xong bước này trang thiết bị Cửa cuốn mới có mục Điều khiển và dashboard mới có `cover.nha_moi_cua_cuon_nha_moi` để bấm.

## Bước 3 — Thêm camera cửa cuốn (cho thẻ Camera)

Nếu chưa làm: **Cài đặt → Thiết bị & dịch vụ → Thêm tích hợp → Generic Camera**, dán link RTSP của camera, đặt tên đúng **"Cam_Cua_Cuon"** (để sinh entity `camera.nha_moi_cam_cua_cuon`) — chi tiết như đã hướng dẫn ở chat. Xong thì thẻ camera trên dashboard tự có hình.

## Bước 4 — Nạp sensor đồng hồ + lịch âm vào Home Assistant

Mở SSH vào box TX3. **Mỗi lần chỉ dán ĐÚNG 1 lệnh**, chờ lệnh chạy xong mới dán lệnh tiếp theo (dán nhiều dòng cùng lúc là lệnh bị lỗi).

**4.0 Kiểm tra trước** (kỳ vọng: lệnh không in ra gì cả; nếu có in ra dòng `sensor:` hoặc `command_line:` thì DỪNG LẠI, chụp màn hình gửi lại, đừng làm tiếp):

```
grep -E '^(sensor|command_line):' /opt/homeassistant/configuration.yaml
```

**4.1 → 4.3 Tạo file script lịch âm** — dán lần lượt 3 lệnh sau (mỗi lệnh rất dài nhưng chỉ là 1 dòng, cứ dán nguyên):

```
echo 'IyEvdXNyL2Jpbi9lbnYgcHl0aG9uMwojIC0qLSBjb2Rpbmc6IHV0Zi04IC0qLQoiIiIKbGljaF9hbS5weSAtIEluIHJhIG5nYXkgYW0gbGljaCBWaWV0IE5hbSBjaG8gaG9tIG5heSAoaG9hYyBuZ2F5IGNoaSBkaW5oKS4KClRodWF0IHRvYW4gSG8gTmdvYyBEdWMgKGFtIGxpY2ggVmlldCBOYW0sIG11aSBnaW8gKzcpLgpDaGF5OgogICAgcHl0aG9uMyBsaWNoX2FtLnB5ICAgICAgICAgICAgICAtPiBuZ2F5IGFtIGN1YSBob20gbmF5CiAgICBweXRob24zIGxpY2hfYW0ucHkgMTAvMTEvMjAyNiAgIC0+IG5nYXkgYW0gY3VhIG5nYXkgZHVvbmcgY2hpIGRpbmgKQ2hpIGR1bmcgdGh1IHZpZW4gY2h1YW4gKG1hdGgsIHN5cywgZGF0ZXRpbWUpIG5lbiBjaGF5IGR1b2MgbmdheQp0cm9uZyBjb250YWluZXIgSG9tZSBBc3Npc3RhbnQgdGFpIC9jb25maWcvbGljaF9hbS5weS4KIiIiCgppbXBvcnQgbWF0aAppbXBvcnQgc3lzCmZyb20gZGF0ZXRpbWUgaW1wb3J0IGRhdGUKClRJTUVfWk9ORSA9IDcgICMgVmlldCBOYW0gR01UKzcKCkNBTiA9IFsiR2nDoXAiLCAi4bqkdCIsICJCw61uaCIsICLEkGluaCIsICJN4bqtdSIsICJL4bu3IiwgIkNhbmgiLCAiVMOibiIsICJOaMOibSIsICJRdcO9Il0KQ0hJID0gWyJUw70iLCAiU+G7rXUiLCAiROG6p24iLCAiTcOjbyIsICJUaMOsbiIsICJU4bu1IiwgIk5n4buNIiwgIk3DuWkiLCAiVGjDom4iLCAiROG6rXUiLCAiVHXhuqV0IiwgIkjhu6NpIl0KCgpkZWYgamRfZnJvbV9kYXRlKGRkLCBtbSwgeXkpOgogICAgIiIiTmdheSBKdWxpYW4gdHUgbmdheSBkdW9uZyBkZC9tbS95eS4iIiIKICAgIGEgPSAoMTQgLSBtbSkgLy8gMTIKICAgIHkgPSB5eSArIDQ4MDAgLSBhCiAgICBtID0gbW0gKyAxMiAqIGEgLSAzCiAgICBqZCA9IGRkICsgKDE1MyAqIG0gKyAyKSAvLyA1ICsgMzY1ICogeSArIHkgLy8gNCAtIHkgLy8gMTAwICsgeSAvLyA0MDAgLSAzMjA0NQogICAgaWYgamQgPCAyMjk5MTYxOgogICAgICAgIGpkID0gZGQgKyAoMTUzICogbSArIDIpIC8vIDUgKyAzNjUgKiB5ICsgeSAvLyA0IC0gMzIwODMKICAgIHJldHVybiBqZAoKCmRlZiBuZXdfbW9vbl9kYXkoaywgdGltZV96b25lKToKICAgICIiIk5nYXkgSnVsaWFuIChzbyBuZ3V5ZW4sIHRoZW8gbXVpIGdpbykgY3VhIG5nYXkgc29jIHRodSBrLiIiIgogICAgVCA9IGsgLyAxMjM2Ljg1CiAgICBUMiA9IFQgKiBUCiAgICBUMyA9IFQyICogVAogICAgZHIgPSBtYXRoLnBpIC8gMTgwCiAgICBqZDEgPSAyNDE1MDIwLjc1OTMzICsgMjkuNTMwNTg4NjggKiBrICsgMC4wMDAxMTc4ICogVDIgLSAwLjAwMDAwMDE1NSAqIFQzCiAgICBqZDEgKz0gMC4wMDAzMyAqIG1hdGguc2luKCgxNjYuNTYgKyAxMzIuODcgKiBUIC0gMC4wMDkxNzMgKiBUMikgKiBkcikKICAgIE0gPSAzNTkuMjI0MiArIDI5LjEwNTM1NjA4ICogayAtIDAuMDAwMDMzMyAqIFQyIC0gMC4wMDAwMDM0NyAqIFQzCiAgICBNcHIgPSAzMDYuMDI1MyArIDM4NS44MTY5MTgwNiAqIGsgKyAwLjAxMDczMDYgKiBUMiArIDAuMDAwMDEyMzYgKiBUMwogICAgRiA9IDIxLjI5NjQgKyAzOTAuNjcwNTA2NDYgKiBrIC0gMC4wMDE2NTI4ICogVDIgLSAwLjAwMDAwMjM5ICogVDMKICAgIEMxID0gKDAuMTczNCAtIDAuMDAwMzkzICogVCkgKiBtYXRoLnNpbihNICogZHIpICsgMC4wMDIxICogbWF0aC5zaW4oMiAqIGRyICogTSkKICAgIEMxICs9IC0wLjQwNjggKiBtYXRoLnNpbihNcHIgKiBkcikgKyAwLjAxNjEgKiBtYXRoLnNpbigyICogZHIgKiBNcHIpCiAgICBDMSArPSAtMC4wMDA0ICogbWF0aC5zaW4oMyAqIGRyICogTXByKQogICAgQzEgKz0gMC4wMTA0ICogbWF0aC5zaW4oMiAqIGRyICogRikgLSAwLjAwNTEgKiBtYXRoLnNpbigoTSArIE1wcikgKiBkcikKICAgIEMxICs9IC0wLjAwNzQgKiBtYXRoLnNpbigoTSAtIE1wcikgKiBkcikg' > /tmp/lich_am.b64
```

```
echo 'KyAwLjAwMDQgKiBtYXRoLnNpbigoMiAqIEYgKyBNKSAqIGRyKQogICAgQzEgKz0gLTAuMDAwNCAqIG1hdGguc2luKCgyICogRiAtIE0pICogZHIpIC0gMC4wMDA2ICogbWF0aC5zaW4oKDIgKiBGICsgTXByKSAqIGRyKQogICAgQzEgKz0gMC4wMDEwICogbWF0aC5zaW4oKDIgKiBGIC0gTXByKSAqIGRyKSArIDAuMDAwNSAqIG1hdGguc2luKCgyICogTXByICsgTSkgKiBkcikKICAgIGlmIFQgPCAtMTE6CiAgICAgICAgZGVsdGFfdCA9IDAuMDAxICsgMC4wMDA4MzkgKiBUICsgMC4wMDAyMjYxICogVDIgLSAwLjAwMDAwODQ1ICogVDMgLSAwLjAwMDAwMDA4MSAqIFQgKiBUMwogICAgZWxzZToKICAgICAgICBkZWx0YV90ID0gLTAuMDAwMjc4ICsgMC4wMDAyNjUgKiBUICsgMC4wMDAyNjIgKiBUMgogICAgamRfbmV3ID0gamQxICsgQzEgLSBkZWx0YV90CiAgICByZXR1cm4gbWF0aC5mbG9vcihqZF9uZXcgKyAwLjUgKyB0aW1lX3pvbmUgLyAyNCkKCgpkZWYgc3VuX2xvbmdpdHVkZShqZG4sIHRpbWVfem9uZSk6CiAgICAiIiJLaW5oIHR1eWVuIG1hdCB0cm9pIHRhaSBudWEgZGVtIG5nYXkgSnVsaWFuIGpkbiwgdHJhIHZlIGNoaSBzbyAwLi4xMSAobW9pIDMwIGRvKS4iIiIKICAgIFQgPSAoamRuIC0gMjQ1MTU0NS41IC0gdGltZV96b25lIC8gMjQpIC8gMzY1MjUKICAgIFQyID0gVCAqIFQKICAgIGRyID0gbWF0aC5waSAvIDE4MAogICAgTSA9IDM1Ny41MjkxMCArIDM1OTk5LjA1MDMwICogVCAtIDAuMDAwMTU1OSAqIFQyIC0gMC4wMDAwMDA0OCAqIFQgKiBUMgogICAgTDAgPSAyODAuNDY2NDUgKyAzNjAwMC43Njk4MyAqIFQgKyAwLjAwMDMwMzIgKiBUMgogICAgREwgPSAoMS45MTQ2MDAgLSAwLjAwNDgxNyAqIFQgLSAwLjAwMDAxNCAqIFQyKSAqIG1hdGguc2luKGRyICogTSkKICAgIERMICs9ICgwLjAxOTk5MyAtIDAuMDAwMTAxICogVCkgKiBtYXRoLnNpbihkciAqIDIgKiBNKSArIDAuMDAwMjkwICogbWF0aC5zaW4oZHIgKiAzICogTSkKICAgIEwgPSAoTDAgKyBETCkgKiBkcgogICAgTCA9IEwgLSBtYXRoLnBpICogMiAqIG1hdGguZmxvb3IoTCAvIChtYXRoLnBpICogMikpCiAgICByZXR1cm4gbWF0aC5mbG9vcihMIC8gbWF0aC5waSAqIDYpCgoKZGVmIGdldF9sdW5hcl9tb250aF8xMSh5eSwgdGltZV96b25lKToKICAgICIiIk5nYXkgYmF0IGRhdSB0aGFuZyAxMSBhbSBsaWNoIGN1YSBuYW0gYW0gY2h1YSB0aGFuZyAxMSBjdWEgbmFtIGR1b25nIHl5LiIiIgogICAgb2ZmID0gamRfZnJvbV9kYXRlKDMxLCAxMiwgeXkpIC0gMjQxNTAyMQogICAgayA9IG1hdGguZmxvb3Iob2ZmIC8gMjkuNTMwNTg4ODUzKQogICAgbm0gPSBuZXdfbW9vbl9kYXkoaywgdGltZV96b25lKQogICAgaWYgc3VuX2xvbmdpdHVkZShubSwgdGltZV96b25lKSA+PSA5OgogICAgICAgIG5tID0gbmV3X21vb25fZGF5KGsgLSAxLCB0aW1lX3pvbmUpCiAgICByZXR1cm4gbm0KCgpkZWYgZ2V0X2xlYXBfbW9udGhfb2Zmc2V0KGExMSwgdGltZV96b25lKToKICAgICIiIlZpIHRyaSB0aGFuZyBuaHVhbiB0aW5oIHR1IHRoYW5nIDExIChhMTEgbGEgbmdheSBiYXQgZGF1IHRoYW5nIDExKS4iIiIKICAgIGsgPSBtYXRoLmZsb29yKChhMTEgLSAyNDE1MDIxLjA3Njk5ODY5NSkgLyAyOS41MzA1ODg4NTMgKyAwLjUpCiAgICBsYXN0ID0gMAogICAgaSA9IDEgICMgYmF0IGRhdSB0dSB0aGFuZyBuZ2F5IHNhdSB0aGFuZyAxMQogICAgYXJjID0gc3VuX2xvbmdpdHVkZShuZXdfbW9vbl9kYXkoayArIGksIHRpbWVfem9uZSksIHRpbWVfem9uZSkKICAgIHdoaWxlIGFyYyAhPSBsYXN0IGFuZCBpIDwgMTQ6CiAgICAgICAgbGFzdCA9IGFyYwogICAgICAgIGkgKz0gMQogICAgICAgIGFyYyA9IHN1bl9sb25naXR1ZGUobmV3X21vb25fZGF5KGsgKyBpLCB0aW1lX3pvbmUpLCB0aW1lX3pvbmUpCiAgICByZXR1cm4g' >> /tmp/lich_am.b64
```

```
echo 'aSAtIDEKCgpkZWYgc29sYXJfdG9fbHVuYXIoZGQsIG1tLCB5eSwgdGltZV96b25lPVRJTUVfWk9ORSk6CiAgICAiIiJEb2kgbmdheSBkdW9uZyBzYW5nIGFtOiB0cmEgdmUgKG5nYXksIHRoYW5nLCBuYW0sIGxhX3RoYW5nX25odWFuIDAvMSkuIiIiCiAgICBkYXlfbnVtYmVyID0gamRfZnJvbV9kYXRlKGRkLCBtbSwgeXkpCiAgICBrID0gbWF0aC5mbG9vcigoZGF5X251bWJlciAtIDI0MTUwMjEuMDc2OTk4Njk1KSAvIDI5LjUzMDU4ODg1MykKICAgIG1vbnRoX3N0YXJ0ID0gbmV3X21vb25fZGF5KGsgKyAxLCB0aW1lX3pvbmUpCiAgICBpZiBtb250aF9zdGFydCA+IGRheV9udW1iZXI6CiAgICAgICAgbW9udGhfc3RhcnQgPSBuZXdfbW9vbl9kYXkoaywgdGltZV96b25lKQogICAgYTExID0gZ2V0X2x1bmFyX21vbnRoXzExKHl5LCB0aW1lX3pvbmUpCiAgICBiMTEgPSBhMTEKICAgIGlmIGExMSA+PSBtb250aF9zdGFydDoKICAgICAgICBsdW5hcl95ZWFyID0geXkKICAgICAgICBhMTEgPSBnZXRfbHVuYXJfbW9udGhfMTEoeXkgLSAxLCB0aW1lX3pvbmUpCiAgICBlbHNlOgogICAgICAgIGx1bmFyX3llYXIgPSB5eSArIDEKICAgICAgICBiMTEgPSBnZXRfbHVuYXJfbW9udGhfMTEoeXkgKyAxLCB0aW1lX3pvbmUpCiAgICBsdW5hcl9kYXkgPSBkYXlfbnVtYmVyIC0gbW9udGhfc3RhcnQgKyAxCiAgICBkaWZmID0gbWF0aC5mbG9vcigobW9udGhfc3RhcnQgLSBhMTEpIC8gMjkpCiAgICBsdW5hcl9sZWFwID0gMAogICAgbHVuYXJfbW9udGggPSBkaWZmICsgMTEKICAgIGlmIGIxMSAtIGExMSA+IDM2NToKICAgICAgICBsZWFwX21vbnRoX2RpZmYgPSBnZXRfbGVhcF9tb250aF9vZmZzZXQoYTExLCB0aW1lX3pvbmUpCiAgICAgICAgaWYgZGlmZiA+PSBsZWFwX21vbnRoX2RpZmY6CiAgICAgICAgICAgIGx1bmFyX21vbnRoID0gZGlmZiArIDEwCiAgICAgICAgICAgIGlmIGRpZmYgPT0gbGVhcF9tb250aF9kaWZmOgogICAgICAgICAgICAgICAgbHVuYXJfbGVhcCA9IDEKICAgIGlmIGx1bmFyX21vbnRoID4gMTI6CiAgICAgICAgbHVuYXJfbW9udGggLT0gMTIKICAgIGlmIGx1bmFyX21vbnRoID49IDExIGFuZCBkaWZmIDwgNDoKICAgICAgICBsdW5hcl95ZWFyIC09IDEKICAgIHJldHVybiBsdW5hcl9kYXksIGx1bmFyX21vbnRoLCBsdW5hcl95ZWFyLCBsdW5hcl9sZWFwCgoKZGVmIGNhbl9jaGlfeWVhcihsdW5hcl95ZWFyKToKICAgIGNhbiA9IENBTlsobHVuYXJfeWVhciArIDYpICUgMTBdCiAgICBjaGkgPSBDSElbKGx1bmFyX3llYXIgKyA4KSAlIDEyXQogICAgcmV0dXJuIGNhbiArICIgIiArIGNoaQoKCmRlZiBmb3JtYXRfbHVuYXIoZGQsIG1tLCB5eSk6CiAgICBsZCwgbG0sIGx5LCBsZWFwID0gc29sYXJfdG9fbHVuYXIoZGQsIG1tLCB5eSkKICAgIHMgPSAiJTAyZC0lMDJkLSVzIiAlIChsZCwgbG0sIGNhbl9jaGlfeWVhcihseSkpCiAgICBpZiBsZWFwOgogICAgICAgIHMgKz0gIiAobmh14bqtbikiCiAgICByZXR1cm4gcwoKCmRlZiBtYWluKCk6CiAgICBpZiBsZW4oc3lzLmFyZ3YpID4gMToKICAgICAgICBwYXJ0cyA9IHN5cy5hcmd2WzFdLnNwbGl0KCIvIikKICAgICAgICBpZiBsZW4ocGFydHMpICE9IDM6CiAgICAgICAgICAgIHByaW50KCJEaW5oIGRhbmcgbmdheSBwaGFpIGxhIGRkL21tL3l5eXkiKQogICAgICAgICAgICByZXR1cm4gMQogICAgICAgIGRkLCBtbSwgeXkgPSAoaW50KHApIGZvciBwIGluIHBhcnRzKQogICAgZWxzZToKICAgICAgICB0b2RheSA9IGRhdGUudG9kYXkoKQogICAgICAgIGRkLCBtbSwgeXkgPSB0b2RheS5kYXksIHRvZGF5Lm1vbnRoLCB0b2RheS55ZWFyCiAgICBwcmludChmb3JtYXRfbHVuYXIoZGQsIG1tLCB5eSkpCiAgICByZXR1cm4gMAoKCmlmIF9fbmFtZV9fID09ICJfX21haW5fXyI6CiAgICBzeXMuZXhpdChtYWluKCkpCg==' >> /tmp/lich_am.b64
```

**4.4 Giải mã thành file script:**

```
base64 -d /tmp/lich_am.b64 > /opt/homeassistant/lich_am.py
```

**4.5 Chạy thử ngay** (kỳ vọng in ra ngày âm của hôm nay, dạng "02-10-Bính Ngọ" — số ngày/tháng sẽ theo đúng ngày bạn chạy):

```
docker exec homeassistant python3 /config/lich_am.py
```

**4.6 Sao lưu cấu hình trước khi sửa:**

```
cp /opt/homeassistant/configuration.yaml /opt/homeassistant/configuration.yaml.bak-v5
```

**4.7 Thêm cấu hình sensor** (1 lệnh duy nhất):

```
printf '%s\n' '' '# --- Dong ho + lich am (Dashboard v5) ---' 'sensor:' '  - platform: time_date' '    display_options:' "      - 'time'" "      - 'date'" '' 'command_line:' '  - sensor:' '      name: "Lich Am"' '      unique_id: lich_am_vn' '      command: "python3 /config/lich_am.py"' '      scan_interval: 1800' >> /opt/homeassistant/configuration.yaml
```

> Sensor cố ý đặt tên không dấu "Lich Am" để Home Assistant sinh đúng entity `sensor.lich_am` cho dashboard. Sau này muốn hiện tên có dấu, vào **Cài đặt → Thiết bị & dịch vụ → Entities → sensor.lich_am → đổi Tên hiển thị** thành "Âm lịch" (chỉ đổi tên hiển thị, không đổi entity).

**4.8 Kiểm tra cấu hình** (kỳ vọng thấy dòng **"Successful config"**; nếu báo lỗi thì chụp màn hình gửi lại, chưa restart):

```
docker exec homeassistant python3 -m homeassistant --script check_config -c /config
```

## Bước 5 — Khởi động lại Home Assistant

```
docker restart homeassistant
```

Chờ khoảng 2 phút, mở **Cài đặt → Thiết bị & dịch vụ → Entities**, tìm `sensor.lich_am` — thấy hiện chữ "02-10-Bính Ngọ" là đạt. (`sensor.time` và `sensor.date` cũng xuất hiện sau lần restart này.)

> Nếu sau restart mà Home Assistant không lên: chạy `cp /opt/homeassistant/configuration.yaml.bak-v5 /opt/homeassistant/configuration.yaml` rồi `docker restart homeassistant` để quay về như cũ, rồi chụp màn hình gửi lại.

## ⚠️ Trước khi dán dashboard — Đặt tên thiết bị & mã entity (đọc kỹ để cài phát ăn ngay)

Home Assistant 2026 **tự sinh mã entity từ tên khu vực (nhà) + tên thiết bị**, còn file dashboard mẫu đang trỏ vào mã của **nhà mẫu**. Bỏ qua bước này, các thẻ sẽ báo "Không tìm thấy thực thể" — đây là lỗi hay gặp nhất khi mang bản mẫu sang nhà khác.

### Cách A — Đặt tên theo chuẩn mẫu (ít phải sửa nhất)

- Khu vực/nhà chính: **Nhà mới**
- Trong app Hunonic, đặt tên thiết bị: **Đèn 1**, **Đèn 2**, **Đèn 3**, **Đèn Cửa Cuốn + Quạt**, **Ổ cắm Nhà mới**
- Thiết bị cửa cuốn (Smart Door): **Cửa cuốn**
- Camera: thêm bằng **Generic Camera**, đặt tên đúng **Cam_Cua_Cuon**, gán vào khu vực của nhà

Đặt trùng mẫu thì các mã `switch.*` gần như khớp ngay. Riêng **cover cửa cuốn và camera** luôn có tiền tố nhà/thiết bị trong mã (nhà mẫu: `cover.nha_moi_cua_cuon_nha_moi`, `camera.nha_moi_cam_cua_cuon`) → **bắt buộc đối chiếu bằng Cách B**.

### Cách B — Lấy mã thật bằng 1 lệnh (chuẩn cho mọi nhà)

SSH vào máy chạy Home Assistant và chạy 1 lệnh:

```
python3 -c "import json;d=json.load(open('/opt/homeassistant/.storage/core.entity_registry'));[print(e['entity_id']) for e in d['data']['entities'] if e['entity_id'].startswith(('switch.','cover.','camera.'))]"
```

Mở file dashboard bằng Notepad, bấm **Ctrl+H** thay từng mã mẫu dưới đây bằng mã thật của nhà bạn, rồi mới dán ở Bước 6:

`camera.nha_moi_cam_cua_cuon` · `cover.nha_moi_cua_cuon_nha_moi` · `button.nha_moi_cua_cuon_nha_moi_khoa` · `button.nha_moi_cua_cuon_nha_moi_mo_khoa` · `switch.den_1` · `switch.den_2` · `switch.den_3` · `switch.den_cua_cuon_quat` · `switch.o_cam_nha_moi` · `switch.nha_k2_den_1` · `switch.nha_k2_den_2` · `switch.den_2_nha_k2` · `switch.den_ong` · `switch.den_sofa` · `switch.giua_nha` · `switch.me` · `switch.me_2`

Thiết bị nào nhà bạn không có thì sau khi dán, xóa thẻ tương ứng trong chế độ Sửa dashboard (dấu ⋮ trên thẻ → Xóa).

## Bước 6 — Dán dashboard v5

1. Mở dashboard **Điều khiển nhà** → **Sửa (Edit)** → menu **⋮** → **Raw configuration editor**.
2. Mở file **`dashboard-dieu-khien-nha.yaml`** (bản 2 cột) → copy toàn bộ → dán đè → **Lưu (Save)**.
3. Muốn bản 3 ô/hàng thì dùng file **`dashboard-3-cot.yaml`** thay cho file trên, cách dán y hệt. Muốn có **cả 2 bản cho người dùng tự chọn**: dán file **`dashboard-dieu-khien-nha-2-va-3-cot.yaml`** — dashboard sẽ có 2 tab trên cùng là "2 cột" và "3 cột", bấm tab nào thì dùng bản đó — hai tab mang biểu tượng số ② và ③ ở thanh trên cùng cho người dùng dễ phân biệt.

## Bước 7 — Đối chiếu nhanh: thẻ nào cần điều kiện gì

| Phần trên dashboard | Cần bước nào xong trước |
|---|---|
| Đèn, ổ cắm (thẻ Mushroom) | Bước 1 |
| Thẻ **Cửa cuốn + Camera chung một ô** (hình trực tiếp, hình trực tiếp ở trên và 3 ô nút icon ↑ ■ ↓ ngay bên dưới, cùng một khối) | **Bước 2** (cho nút bấm) + **Bước 3** (cho hình camera) |
| **Header** đồng hồ / lịch dương / lịch âm | Bước 4 + Bước 5 |

---

## Tùy chỉnh theo nhu cầu (không cần đụng YAML)

Mọi thiết bị trên dashboard là **từng thẻ riêng lẻ**, nên chỉnh bằng tay ngay trong Home Assistant được hết:

**Đổi bản 2 cột ↔ 3 cột:** dán lại dashboard bằng file còn lại (xem Bước 6). Cơ chế: mỗi nhóm (section) là một lưới **12 cột cố định** — ô rộng 6 cột = 2 ô/hàng, ô rộng 4 cột = 3 ô/hàng. Số ô mỗi hàng **giống nhau trên mọi thiết bị** (thẻ không tự co theo màn hình); khác nhau chỉ ở chỗ: trên **điện thoại** các nhóm xếp chồng dọc, trên **màn hình rộng/máy tính** các nhóm nằm cạnh nhau (tối đa 2 nhóm cạnh nhau). Bản **2 cột**: ô to, chữ rõ, dễ bấm — hợp điện thoại. Bản **3 cột**: gọn, thấy được nhiều thiết bị cùng lúc — hợp máy tính bảng / màn hình lớn.

**Sắp xếp lại vị trí:** vào **Sửa dashboard** → **nhấn giữ thẻ** rồi kéo tới vị trí mới (kéo được cả giữa các nhóm; kéo cả nhóm bằng nút di chuyển ở góc nhóm) → **Xong**. Thứ tự trong file chỉ là mặc định ban đầu, thích thế nào kéo thế đó.

**Đổi kích thước 1 thẻ:** Sửa dashboard → chọn thẻ → tab **Bố cục (Layout)** → chỉnh số cột thẻ chiếm (ví dụ cho thẻ Camera chiếm hết hàng: đặt "full").

**Ẩn thiết bị không dùng:** Sửa dashboard → chọn thẻ → **Xóa thẻ**. Muốn thêm lại: **Thêm thẻ → Mushroom** → chọn entity tương ứng.

**Nhà có cổng tự động:** bản mẫu mặc định KHÔNG để sẵn thẻ cổng — nhà nào có thì tự thêm: **Thêm thẻ → Mushroom Cover Card** → chọn entity cổng (dạng `cover.cong_...`) → kéo vào nhóm **Điều khiển chính**.

### Khi lắp cho khách (tên thiết bị khác bản mẫu)

- **Dùng ngay không cần sửa:** bản vá Hunonic, script + header lịch âm (sensor giờ/lịch do hệ thống sinh, nhà nào cũng giống nhau), khung giao diện và các loại thẻ.
- **Phải đối chiếu lại:** các thẻ đèn / cửa cuốn / camera đang trỏ vào **mã entity của nhà mẫu** (mã sinh từ tên thiết bị trong app Hunonic + tên nhà). Nhà khách đặt tên khác thì mã khác — dán nguyên si sẽ hiện cảnh báo "không tìm thấy entity" ở các thẻ đó.
- **Quy trình chuẩn khi lắp cho khách:**
  1. Ưu tiên **đặt tên thiết bị theo mẫu ngay khi khai báo** trong app Hunonic cho khách (Đèn 1, Đèn 2, Đèn 3, Ổ cắm, Cửa cuốn...) và đặt tên camera là **Cam_Cua_Cuon** → phần lớn mã khớp sẵn.
  2. Mở **Cài đặt → Thiết bị & dịch vụ → tab Thực thể** của nhà khách, ghi lại mã thật của từng thiết bị.
  3. Mở file dashboard bằng Notepad, dùng **Tìm & thay thế (Ctrl+H)** thay mã mẫu bằng mã thật. Các mã mẫu cần thay: `switch.den_1`, `switch.den_2`, `switch.den_3`, `switch.den_cua_cuon_quat`, `switch.o_cam_nha_moi`, `switch.nha_k2_den_1`, `switch.nha_k2_den_2`, `switch.den_2_nha_k2`, `switch.den_ong`, `switch.den_sofa`, `switch.giua_nha`, `switch.me`, `switch.me_2`, `cover.nha_moi_cua_cuon_nha_moi` (mã cover sinh theo **tên nhà** của khách), `button.nha_moi_cua_cuon_nha_moi_khoa`, `button.nha_moi_cua_cuon_nha_moi_mo_khoa` (2 nút khóa của cửa cuốn, cần bản Hunonic 1.14.3), `camera.nha_moi_cam_cua_cuon` (khớp sẵn nếu đặt tên camera là Cam_Cua_Cuon).
  4. Dán file đã sửa như Bước 6. Thẻ nào nhà khách không có thiết bị tương ứng thì xóa thẻ đó trong chế độ Sửa dashboard.

**Đổi tên hiển thị trên thẻ:** Sửa dashboard → chọn thẻ → sửa ô **Primary** (với thẻ công tắc) hoặc **Tên** (với thẻ cổng/cửa cuốn). Đổi icon cũng ở màn hình này (ô **Icon**, gõ dạng `mdi:lightbulb`).

---

*Ghi chú kỹ thuật: lịch âm tính bằng thuật toán Hồ Ngọc Đức (múi giờ +7, đúng lịch Việt Nam) chạy ngay trên box, không cần internet. Script đã được kiểm chứng với Tết 2025/2026/2027, Rằm tháng 8 (Trung thu) 2025/2026, các tháng nhuận 2020/2023/2025 và ngày 10/11/2026 (2/10 âm) — đều khớp lịch vạn niên.*
