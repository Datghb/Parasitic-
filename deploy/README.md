# Deploy trên VPS

Trước lần chạy đầu tiên, tạo hai file biến môi trường thật từ các file mẫu:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

Điền đầy đủ giá trị cần thiết trong:

- `backend/.env`
- `frontend/.env`

Hai file `.env` chứa cấu hình riêng và secret, không được commit lên Git.

## DNS và HTTPS

Trước khi chạy Compose, cả hai domain phải có DNS `A record` trỏ về địa chỉ
IPv4 của VPS:

- `diachung.dpdns.org`
- `api.theoria-lab.io.vn`

Nếu DNS chưa trỏ đúng, Caddy sẽ không thể lấy chứng chỉ HTTPS từ Let's Encrypt.

## Firewall

Chỉ cần mở hai cổng public trên VPS:

- `80/tcp`
- `443/tcp`

Không cần mở cổng `3000` hoặc `8000`. Frontend và backend chỉ được truy cập
trong Docker network nội bộ thông qua Caddy.

## Khởi chạy

Chạy các service từ thư mục root của repo:

```bash
docker compose -f deploy/compose.yaml up --build -d
```

Caddy tự động lấy và gia hạn chứng chỉ HTTPS. Chứng chỉ được lưu trong named
volume `caddy_data`; không xóa volume này khi deploy lại.

Lệnh `docker compose down` thông thường không xóa named volume. Không sử dụng
`docker compose down -v` trừ khi chủ động muốn xóa dữ liệu chứng chỉ.
