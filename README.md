Wumpus World — PyGame (Dual Agents)

Phiên bản mô phỏng Wumpus World bằng Python + Pygame, hiển thị 2 agents trên 2 bản đồ giống hệt để so sánh hành vi. README này là bản sẵn sàng copy — paste vào README.md.

Giới thiệu

Wumpus World là một bài toán kinh điển trong trí tuệ nhân tạo: agent di chuyển trên lưới, tránh hố (pits) và Wumpus, tìm vàng rồi quay về cửa ra. Project này triển khai:

Một agent thông minh (SmartAgent) dùng các luật tin tưởng (belief rules) + A* với ước lượng rủi ro để ra quyết định.

Một agent cơ bản (AgentNormal) thực hiện hành vi đơn giản để so sánh.

Giao diện đồ hoạ sử dụng Pygame, hiển thị hai khung song song (trái/phải) cùng một bản đồ (độc lập về trạng thái).

Thành viên nhóm (Lớp 23 CLC02)

Nguyễn Bách Khoa

Trương Quang Huy

Nguyễn Nhật Nam

Phan Trung Tuấn

Trần Danh Thiện

Yêu cầu

Python 3.8 trở lên

pygame

Cài pygame:

pip install pygame

Cách chạy

Clone repository:

git clone https://github.com/thien2603/Wumpus-World-Agent cd

Khởi chạy:

python main.py

Lưu ý: file entrypoint của project mẫu là main.py. Nếu repo của bạn dùng tên khác, chạy file entrypoint tương ứng.

Hướng dẫn chơi / Điều khiển

Khi chạy chương trình, menu chính hiện lên. Chọn Start Game để bắt đầu.

Trong popup nhập:

N — kích thước bản đồ (NxN), nguyên ≥ 2.

K — số Wumpus, nguyên ≥ 0 (không nên quá lớn so với diện tích bản đồ).

Bàn phím:

S - Restart trò chơi

D — bật/tắt chế độ debug (hiện thông tin nội bộ agent).

X hoặc đóng cửa sổ — thoát chương trình.

Mô tả giao diện

Màn hình chia làm hai khung song song:

Trái: SmartAgent (hành vi nâng cao).

Phải: AgentNormal (hành vi cơ bản).

Mỗi khung vẽ lưới, các ô, agent, Wumpus, hố, vàng (nếu để hiển thị), và thanh trạng thái (score, vị trí, hướng, debug info...).

Thanh status hiển thị điểm, vị trí agent, số ô đã thăm, số nghi vấn pit/wumpus, v.v.

Gợi ý cấu hình/tuỳ chỉnh

Thay đổi cấu hình mặc định trong constants.py (N, K, PIT_PROB, kích thước ô, màu sắc...).

Cấu trúc thư mục (gợi ý) / ├─ main.py ├─ constants.py ├─ world.py ├─ agents.py ├─ Agent.py ├─ draw.py ├─ menu.py ├─ img/ │ └─ logo_game.jpg └─ README.md

Phát triển & đóng góp

Fork → tạo branch → commit → PR.

Khi thêm tính năng, giữ interface hàm create_world(n,k) để dễ test tự động.

Viết unit-test cho agent nếu muốn kiểm tra logic belief/risk.

License

Không có license

Liên hệ

Nhóm lớp 23 CLC02 — nếu cần hỗ trợ thêm: liên hệ trực tiếp với các thành viên nhóm.
