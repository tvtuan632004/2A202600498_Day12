# Day 12 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found
1. **Hardcoded API key** trực tiếp trong source code thay vì dùng các biến môi trường (`.env`).
2. **Port bị ấn định tĩnh (ví dụ: 8000)** thay vì có thể cấu hình thông qua OS injection.
3. Kích hoạt **Debug mode (`debug=True`)** trên môi trường có khả năng bị truy cập bởi users.
4. **Không có Health check (`/health` và `/ready`)** khiến Orchestrator không rõ được sự tồn tại của server.
5. **Không có thiết lập Graceful shutdown**: Tắt server thì app dừng làm gián đoạn mọi process đang chạy, dễ dẫn đến mất thông tin.

### Exercise 1.3: Comparison table
| Feature | Develop | Production | Tại sao quan trọng? |
|---------|---------|------------|----------------|
| Config  | Hardcode thẳng trong code | Dùng Environment Variables (`.env`) | Bảo mật secrets và tuân thủ tiêu chuẩn the twelves factor app, giúp linh hoạt trên các môi trường. |
| Health check | Không có | Có (/health, /ready) | Giúp Nginx, K8s hay Cloud Provider biết nên lúc nào thì ngắt luồng (restart container). |
| Logging | Dùng `print()` | Structured Logging định dạng JSON | Giúp log aggregator (như Elastic/Kibana, Datadog) dễ theo dõi. |
| Shutdown | Dừng đột ngột máy chủ (Kill-9) | Graceful Shutdown qua Signal Handler | Đảm bảo xử lý trọn vẹn request cuối từ client trước khi bị tắt (disconnect db/redis/..). |

## Part 2: Docker

### Exercise 2.1: Dockerfile questions
1. Base image là: `python:3.11` (phiên bản full Python distribution của Debian).
2. Working directory: `/app`.
3. Tại sao cần `COPY requirements.txt` trước bước COPY mã nguồn?: Nhằm tận dụng bộ nhớ cache của từng layer trong Docker. Layer requirements hiếm khi thay đổi, vì thế pip install sẽ không phải tải cài lại từ đầu nếu ta chỉ sửa một vài file source code. 
4. CMD vs ENTRYPOINT khác nhau thế nào?: `CMD` cung cấp shell run mặc định và có thể bị tùy biến command ghi đè bằng cấu trúc chạy `docker run <image> <command>`. Còn `ENTRYPOINT` quy định app được chạy file nào, lệnh được passed khi bắt đầu container được append vào array arg của execution script của ENTRYPOINT.

### Exercise 2.3: Image size comparison
- Develop: ~1.0 GB (`python:3.11`)
- Production: ~150-200 MB (`python:3.11-slim`)
- Khác biệt: Tiết kiệm tới **80-85%** thông qua việc bỏ đi các thư viện đồ họa phụ trợ không phục vụ cho môi trường production server và gom quá trình qua Multi-Stage Build.

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment
- URL: `https://ai-agent-v1-production.up.railway.app`
- Screenshot: `[Link to screenshot nằm trong thư mục screenshots/]`

## Part 4: API Security

### Exercise 4.1-4.3: Test results
- Khi request mà không có xác thực Key Authorization: **Mã lỗi 401 Unauthorized**.
- Authentication flow JWT xác suất với endpoints /token.
- Rate limiter áp dụng với thư viện limit token sliding window trên REDIS. Test script sau 15 requests cùng vòng sẽ output exception message chứa **429 Too Many Requests**.

### Exercise 4.4: Cost guard implementation
- Kiểm tra số Token (Input & Output) mà Prompt sử dụng. 
- Sau khi được giá trị cost, cost được update lại vào DB trong Memory như Redis, với Key Tracking theo user (`budget:{user_id}:{month_year}`). Redis In-memory tracking chạy cực nhanh. 
- Khi người dùng chạm ngưỡng ngân sách `$10/User/Month` thì Agent sẽ dừng và chặn không gọi lên LLM API đồng thời trả HTTP code 503 Out-of-Budget limit.

## Part 5: Scaling & Reliability

### Exercise 5.1-5.5: Implementation notes
- Health checks chia làm 2 phần: **Liveness** để detect crash loop (trả 200 OK) và **Readiness** để loadbalancer xem agent đã sẵn sàng nối DB, redis hay chưa (có thể là 503 Not ready).
- Tách rời State để trở nên **Stateless**: Không còn lưu array history (trạng thái conversation) trực tiếp trong RAM của các biến global code ở App. Chuyển phần state đó sang chia sẻ chung trong REDIS cache. Khi nhiều containers được chạy, bất kỳ container nào cũng có thể xử lý phiên mà không xảy ra miss data.
- **Nginx Load Balancer**: Container NGINX được sử dụng như proxy trung chuyển chia traffic theo Round-Robin tới các node (replica agents scale x3).
