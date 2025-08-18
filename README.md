# Wumpus World — PyGame (Dual Agents)

**Mô tả ngắn:**  
Phiên bản mô phỏng *Wumpus World* bằng Python + Pygame. Chương trình hiển thị **2 agents** chạy trên **2 bản đồ giống hệt** (tách biệt trạng thái) để so sánh hành vi: một agent thông minh (SmartAgent) và một agent cơ bản (AgentNormal).

---

## 📌 Mục lục
1. [Giới thiệu](#giới-thiệu)  
2. [Tính năng chính](#tính-năng-chính)  
3. [Yêu cầu & Cài đặt](#yêu-cầu--cài-đặt)  
4. [Cách chạy](#cách-chạy)  
5. [Điều khiển & Hướng dẫn chơi](#điều-khiển--hướng-dẫn-chơi)  
6. [Cấu trúc dự án](#cấu-trúc-dự-án)  
7. [Gợi ý tuỳ chỉnh](#gợi-ý-tuỳ-chỉnh)  
8. [Thành viên nhóm (Lớp 23 CLC02)](#thành-viên-nhóm-lớp-23-clc02)  
9. [Đóng góp](#đóng-góp)  
10. [License & Liên hệ](#license--liên-hệ)

---

## Giới thiệu
*Wumpus World* là bài toán cổ điển trong AI: agent di chuyển trên lưới NxN, tránh **pit** (hố) và **Wumpus**, tìm **vàng** rồi quay về ô xuất phát. Project này mô phỏng hành vi của hai loại agent để thấy tác dụng của các chiến lược khác nhau.

- **SmartAgent**: sử dụng các quy tắc tin cậy (belief rules) + A* với ước lượng rủi ro để lập kế hoạch và ra quyết định.  
- **AgentNormal**: agent đơn giản để so sánh (heuristic/rule-based cơ bản).

Giao diện sử dụng **Pygame**, chia màn hình làm hai khung (trái/phải), mỗi khung hiển thị một agent trên bản đồ giống nhau nhưng trạng thái độc lập.

---

## Tính năng chính
- Tạo bản đồ ngẫu nhiên (số Wumpus, xác suất pit có thể thay đổi).  
- SmartAgent dùng forward-chaining để cập nhật niềm tin và A* để lập kế hoạch an toàn.  
- Hiển thị trực quan (grid, agent, pit, wumpus, vàng, percepts nếu bật debug).  
- Popup cho phép thay đổi tham số **N** (kích thước) và **K** (số Wumpus) trước khi khởi động.

---

## Yêu cầu & Cài đặt
- Python 3.8+
- pygame

Cài pygame (pip):
```bash
pip install pygame
```

Clone repo:
```bash
git clone https://github.com/thien2603/Wumpus-World-Agent.git
cd Wumpus-World-Agent
```

---

## Cách chạy
Mặc định entrypoint là `main.py` (hoặc `main1.py` / `main_shared.py` tuỳ repo). Chạy:
```bash
python main.py
```

Nếu file entrypoint khác, chạy file tương ứng, ví dụ:
```bash
python main1.py
```

---

## Điều khiển & Hướng dẫn chơi
Khi chạy sẽ hiện menu chính. Chọn **Start Game** để bắt đầu. Popup yêu cầu nhập:
- `N` — kích thước bản đồ (NxN), số nguyên ≥ 2.  
- `K` — số Wumpus, số nguyên ≥ 0 (không nên quá lớn so với diện tích bản đồ).

Phím tắt trong game:
- `S` — Restart trò chơi (tạo world mới).  
- `D` — Bật/tắt chế độ debug (hiện percepts/niềm tin agent).  
- `M` — Move Wumpus (thủ công, nếu có).  
- `Space` — Step (thực hiện một bước cho cả hai agent nếu đang tạm dừng).  
- `1`/`2` — Toggle auto cho Agent trái/phải.  
- `A` — Bật/tắt chế độ auto cho cả hai agent.  
- `X` hoặc đóng cửa sổ — Thoát.

**Mẹo:** không nên đặt số Wumpus quá lớn so với `N*N` vì có thể gây bế tắc hoặc chết sớm cho agent.

---

## Cấu trúc dự án (gợi ý)
```
├─ main.py (entrypoint)
├─ constants.py
├─ world.py
├─ agents.py
├─ Agent.py
├─ draw.py
├─ menu.py
├─ img/
│  └─ logo_game.jpg
└─ README.md
```

---

## Gợi ý tuỳ chỉnh
- Thay đổi tham số mặc định trong `constants.py` (N, K, PIT_PROB, kích thước ô, màu sắc...).  
- `world.create_world(n, k)` hỗ trợ truyền `n, k` để tạo world theo tham số runtime. Giữ interface này để dễ test.  
- Nếu muốn agent đọc kích thước động, sửa module agent để tham chiếu kích thước thế giới từ `len(world)` thay vì import cứng `N` từ `constants`.

---

## Thành viên nhóm (Lớp 23 CLC02)
- Nguyễn Bách Khoa  
- Trương Quang Huy  
- Nguyễn Nhật Nam  
- Phan Trung Tuấn  
- Trần Danh Thiện

---

## Đóng góp
1. Fork repository.  
2. Tạo branch feature/bugfix.  
3. Commit & push.  
4. Tạo Pull Request.

Khi thêm tính năng, giữ interface `create_world(n, k)` để đảm bảo tương thích với menu. Nếu thay đổi API module, ghi rõ trong PR.

---

## License & Liên hệ
- License: *Không có license* (nếu muốn public, cân nhắc thêm MIT/BSD...).  
- Liên hệ: Nhóm lớp 23 CLC02 (các thành viên ở trên).

---
