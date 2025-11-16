# Doro Discord Bot 🌸 V4.1 (Phiên Bản Node.js)

Bot Discord đa chức năng dễ thương với hệ thống nhạc, kinh tế, casino, kết hôn, trò chuyện AI và nối từ! Hiện được vận hành bởi Node.js với hỗ trợ đa ngôn ngữ!

> 🇻🇳 **Tiếng Việt** (hiện tại) | 🇺🇸 **[English](README.md)**

**Phiên Bản:** V4.1 | **Ngôn Ngữ:** Tiếng Việt | **Trạng Thái:** ✅ Hoạt Động

## ✨ Tính Năng Chính

### 🎵 Hệ Thống Nhạc
- Phát nhạc từ SoundCloud (ổn định hơn YouTube!)
- Quản lý hàng đợi với bỏ qua, tạm dừng, tiếp tục
- Tự động rời sau khi không hoạt động
- Hiển thị bài đang phát

### 🎨 Hệ Thống Profile
- Profile người dùng với thông tin
- Hiển thị tiến trình cấp độ
- Thông tin kinh tế
- Hỗ trợ avatar

### 💰 Hệ Thống Kinh Tế  
- Phần thưởng hàng ngày (1200-1800 xu cơ bản)
- Hệ thống chuỗi ngày với thưởng
- Tiến trình cấp độ với XP
- Ngân hàng gửi/rút tiền
- Chuyển tiền giữa người dùng

### 🎰 Trò Chơi Casino
- **Tung Xu** - Đặt cược truyền thống ngửa hay sấp
- **Quay Số** - Máy quay số 3 trục với jackpot
- **Roulette** - Đặt cược đỏ/đen/số
- **Blackjack** - Trải nghiệm blackjack đầy đủ với hit/stand

### 🏪 Hệ Thống Cửa Hàng
- Nhiều vật phẩm để mua:
  - 💍 Nhẫn cưới (cho hệ thống kết hôn)
  - 📦 Hộp phần thưởng với phần thưởng ngẫu nhiên
  - 🍀 Vật phẩm may mắn cho thưởng casino
  - 🎀 Vật phẩm trang trí và sưu tầm
- Quản lý túi đồ
- Trang bị và sử dụng vật phẩm

### 💍 Hệ Thống Kết Hôn & Cửa Hàng
- **Nhẫn Cửa Hàng** - Mua nhẫn tăng thưởng hàng ngày:
  - 💍 Nhẫn Tình Yêu (+5% daily) - 50,000 xu
  - 💕 Nhẫn Đôi (+10% daily) - 120,000 xu
  - 🦆 Nhẫn Uyên Ương (+15% daily) - 250,000 xu
  - 💎 Nhẫn Vĩnh Cửu (+25% daily) - 500,000 xu
  - ✨ Nhẫn Định Mệnh (+50% daily) - 1,000,000 xu
- Cầu hôn người dùng khác (cần nhẫn)
- Chấp nhận/từ chối lời cầu hôn
- Hiển thị trạng thái kết hôn
- Có tùy chọn ly hôn

### 🤖 Trò Chuyện AI
- Nhắc @Doro để trò chuyện AI dễ thương
- Phản hồi do NVIDIA cung cấp
- Tính cách thích ứng dựa trên người dùng
- Nhớ ngữ cảnh cuộc trò chuyện

### 🎮 Lệnh Vui
- Chuyển đổi văn bản (OwO, UwU, mock text)
- Tung xúc xắc ngẫu nhiên
- Hồ sơ người dùng với thẻ đẹp
- Hệ thống AFK với tự động trả lời

### 🌍 Đa Ngôn Ngữ
- Hỗ trợ tiếng Anh và tiếng Việt
- Chuyển đổi ngôn ngữ theo server
- Sử dụng slash command `/language` để thay đổi

### ⚡ Tối Ưu Hiệu Suất
- Độ trễ cực thấp (< 30ms thời gian phản hồi)
- Smart caching để tra cứu tức thời
- Xử lý tin nhắn được tối ưu
- Quản lý bộ nhớ tự động

## 🆕 Có Gì Mới Trong V4.1

- 🔕 **Chặn Ping** - Bot bỏ qua tin nhắn chứa `@everyone` / `@here` và toàn bộ output (kể cả `!say`) được làm sạch nên không ping cả server.
- 🎧 **Sửa Khởi Tạo Nhạc** - DisTube được khởi tạo cùng Discord client nên nhạc chạy ổn định trên các máy hỗ trợ voice (máy thật/VPS).
- ⚙️ **GitHub Actions Runner** - Thêm `.github/workflows/bot.yml` để lint mỗi lần push và có thể chạy bot trực tiếp từ Actions bằng secrets của repo.
- 🚀 **Tối Ưu Độ Trễ** - Bộ phân tích tin nhắn gọn hơn cùng lệnh `npm run lint` mới giúp giữ latency và API ping ở mức thấp nhất.

## Cập Nhật Trước Đó (V4.1)

- 🎵 **Hệ Thống Nhạc Hoàn Chỉnh** - Phát YouTube với queue, skip, pause, resume
- ⚡ **Đã Sửa Latency** - Khôi phục cài đặt tối ưu, API latency về 20-50ms
- 🎧 **Hỗ Trợ Voice** - Tích hợp @discordjs/voice với play-dl
- 📊 **Quản Lý Hàng Đợi** - Xem queue, đang phát, tự động phát tiếp
- 🔧 **Tối Ưu Cân Bằng** - Cân bằng hoàn hảo giữa hiệu suất và chức năng

### Cập Nhật Trước Đó (V4.1)
- 🌍 AI nhận biết ngôn ngữ - Nói tiếng Việt/Anh theo server
- 💬 AI trả lời tự nhiên - Sửa khoảng cách emoji
- 🌐 Hỗ trợ ngôn ngữ đầy đủ - Tất cả lệnh respect ngôn ngữ

### Cập Nhật Trước Đó (V4.1)
- 🐛 Sửa lỗi nghiêm trọng - Bot không khởi động
- 💍 Hiệu ứng nhẫn hoạt động - Nhẫn tăng thưởng daily
- 📊 Bảng xếp hạng - Theo dõi top users
- 🎴 Game Blackjack - Casino blackjack hoàn chỉnh
- 💰 Cân bằng kinh tế - Daily 1200-1800 xu

### Cập Nhật Trước Đó (V4.1)
- ✅ Hệ thống đa ngôn ngữ - Hỗ trợ đầy đủ tiếng Anh & tiếng Việt
- ✅ Slash Commands - Lệnh `/language` và `/ping`
- ✅ Độ trễ cực thấp - Tối ưu cho < 30ms phản hồi
- ✅ Hệ thống help thông minh - Tự động dịch theo ngôn ngữ server
- ✅ AI cải thiện - 15+ phản hồi đa dạng cho chủ bot

## 🚀 Cài Đặt Nhanh

### Yêu Cầu
- Node.js 22.12.0 trở lên
- Token Bot Discord
- API Keys (tùy chọn):
  - Khóa API NVIDIA (cho trò chuyện AI)

### Cài Đặt

1. Clone hoặc tải xuống file bot

2. Cài đặt dependencies:
```bash
npm install
```

3. Tạo file `.env` với token của bạn:
```env
DISCORD_BOT_TOKEN=token_bot_cua_ban
NVIDIA_API_KEY=khoa_nvidia_cua_ban
BOT_OWNER_IDS=discord_id_cua_ban
```

4. Chạy bot:
```bash
npm start
```

Hoặc cho chế độ phát triển với tự động khởi động lại:
```bash
npm run dev
```

## 📝 Danh Sách Lệnh

**Prefix mặc định:** `!` (có thể thay đổi)

### 🎵 Lệnh Nhạc
- `!play [bài hát]` - Phát hoặc thêm bài hát vào hàng đợi
- `!skip` - Bỏ qua bài hiện tại
- `!queue` - Xem hàng đợi
- `!pause/resume` - Tạm dừng/tiếp tục phát
- `!stop` - Dừng và xóa hàng đợi
- `!np` - Đang phát

### 💰 Lệnh Kinh Tế
- `!balance [@user]` - Kiểm tra số dư
- `!daily` - Nhận phần thưởng hàng ngày (với bonus nhẫn!)
- `!deposit [số tiền]` - Gửi vào ngân hàng
- `!withdraw [số tiền]` - Rút từ ngân hàng
- `!give @user [số tiền]` - Chuyển tiền (phí 10%)
- `!leaderboard [loại]` - Xem top 10 users (balance/level/streak/wins)

### 🎰 Lệnh Casino
- `!cf [h/t] [cược]` - Tung xu
- `!slots [cược]` - Máy quay số
- `!bj [cược]` - Blackjack (1.5x cho natural 21)

### 🏪 Lệnh Cửa Hàng
- `!shop [trang/danh mục]` - Duyệt cửa hàng
- `!buy [vật phẩm]` - Mua vật phẩm
- `!inventory [@user]` - Xem túi đồ
- `!use [vật phẩm]` - Sử dụng vật phẩm
- `!equip [vật phẩm]` - Trang bị vật phẩm

### 💍 Lệnh Kết Hôn
- `!marry @user` - Cầu hôn (cần nhẫn)
- `!accept` - Chấp nhận lời cầu hôn
- `!reject` - Từ chối lời cầu hôn
- `!divorce` - Ly hôn
- `!marriage [@user]` - Xem thông tin kết hôn

### ⚙️ Lệnh Tiện Ích
- `!help` - Xem tất cả lệnh
- `!ping` - Kiểm tra độ trễ bot
- `!avatar [@user]` - Lấy avatar
- `!afk [lý do]` - Đặt trạng thái AFK
- `!setprefix <prefix>` - Thay đổi prefix server (Chỉ Admin)

### 🤖 Trò Chuyện AI
- **@Doro [tin nhắn]** - Trò chuyện với Doro AI
- `!reset` - Xóa lịch sử trò chuyện AI

### 🌍 Slash Commands
- `/language` - Thay đổi ngôn ngữ bot cho server (Chỉ Admin)
- `/ping` - Kiểm tra độ trễ và thời gian phản hồi

## ⚙️ Cấu Hình

### Đặt Chủ Sở Hữu Bot
Thêm Discord ID trong `.env`:
```env
BOT_OWNER_IDS=id1,id2,id3
```

### Tùy Chỉnh Kinh Tế
Chỉnh sửa giá trị trong `systems/economySystem.js`:
- Số dư ban đầu
- Số tiền thưởng hàng ngày  
- Yêu cầu XP cho cấp độ
- Tỷ lệ thắng casino

### Điều Chỉnh Giá Cửa Hàng
Chỉnh sửa giá trong `systems/shopSystem.js`:
- Giá nhẫn
- Chi phí hộp phần thưởng
- Hiệu ứng vật phẩm

### Tính Cách AI
Tùy chỉnh tính cách Doro trong `systems/aiSystem.js`:
- Phong cách phản hồi
- Sử dụng emoji
- Hành vi chủ sở hữu vs người dùng thông thường

## 🎨 Điểm Nổi Bật Tính Năng

### Thẻ Hồ Sơ Đẹp
- Thẻ thiết kế tùy chỉnh với thống kê người dùng
- Thanh tiến trình cấp độ và XP
- Hiển thị trạng thái kết hôn
- Thống kê kinh tế
- Huy hiệu và thành tích

### Phản Hồi AI Thông Minh  
- Cuộc trò chuyện nhận biết ngữ cảnh
- Tính cách thích ứng với người dùng
- Phản hồi dễ thương và vui tươi
- Phản ứng emoji

### Hệ Thống Chuỗi Ngày
- Chuỗi đăng nhập hàng ngày
- Phần thưởng tăng dần cho sự nhất quán
- Nhân thưởng
- Thưởng dựa trên cấp độ

## 🐛 Khắc Phục Sự Cố

### Bot Không Phản Hồi
- Kiểm tra bot đã bật các intent cần thiết
- Xác minh prefix là `!` 
- Đảm bảo bot có quyền trong kênh

### Nhạc Không Phát
- Xác minh ffmpeg đã được cài đặt
- Kiểm tra quyền kênh thoại
- Đảm bảo link YouTube hợp lệ
- **⚠️ GitHub Actions không thể dùng voice!** Nhạc chỉ hoạt động khi bot chạy local

### AI Không Hoạt Động
- Xác nhận API keys trong `.env`
- Kiểm tra giới hạn tỷ lệ API
- Xác minh kết nối internet

### Vấn Đề Kinh Tế
- Dữ liệu lưu trong file JSON
- Kiểm tra quyền file
- Sao lưu dữ liệu thường xuyên

## 📚 Lưu Trữ Dữ Liệu

Tất cả dữ liệu được lưu cục bộ trong file JSON:
- `economy_data.json` - Số dư và thống kê người dùng
- `shop_data.json` - Kho cửa hàng
- `user_inventory.json` - Vật phẩm người dùng
- `marriage_data.json` - Hồ sơ kết hôn
- `afk_data.json` - Trạng thái AFK
- `disabled_commands.json` - Lệnh bị vô hiệu hóa
- `language_data.json` - Cài đặt ngôn ngữ server

## 🎯 Mẹo & Thủ Thuật

1. **Chuỗi Ngày Hàng Ngày** - Đừng phá vỡ chuỗi để nhận phần thưởng tối đa!
2. **Chiến Lược Cửa Hàng** - Mua nhẫn trước khi cầu hôn
3. **Mẹo Casino** - Bắt đầu với cược nhỏ
4. **Tăng Cấp** - Nhận XP từ nhận thưởng hàng ngày và hoạt động
5. **Thẻ Hồ Sơ** - Tùy chỉnh thẻ của bạn với thành tích

## 🌟 Tính Năng Đặc Biệt

- **Chế Độ Vô Hạn** - Chủ sở hữu nhận tài nguyên không giới hạn
- **Vô Hiệu Hóa Lệnh** - Vô hiệu hóa lệnh cụ thể mỗi server
- **Tự Động AFK** - Tự động đặt AFK khi được nhắc
- **Trợ Giúp Thông Minh** - Hệ thống trợ giúp dựa trên danh mục
- **Phản Hồi Nhanh** - Tối ưu hóa cho phản ứng nhanh (< 30ms)
- **Đa Ngôn Ngữ** - Hỗ trợ tiếng Anh và tiếng Việt

## ⚡ Tối Ưu Hóa Hiệu Suất

Bot được tối ưu hóa cho độ trễ cực thấp:
- ✅ Caching thông minh cho tra cứu O(1)
- ✅ Tải song song tất cả hệ thống
- ✅ Sweep bộ nhớ cache tự động
- ✅ Giảm thiểu REST API calls
- ✅ Độ trễ phản hồi < 30ms

## 🆕 Có Gì Mới Trong V4.1

- 🔕 **Chặn Ping** - Tự động bỏ qua `@everyone`/`@here` và làm sạch mọi tin nhắn bot gửi đi để không tạo ping không cần thiết.
- 🎧 **Sửa Khởi Tạo Nhạc** - DisTube luôn nạp cùng Discord client nên lệnh nhạc hoạt động ngay lập tức trên những môi trường hỗ trợ voice (máy thật/VPS).
- ⚙️ **GitHub Actions Runner** - Workflow mới lint code khi push và cho phép khởi chạy bot trực tiếp từ Actions với secrets.
- 🚀 **Tối Ưu Độ Trễ** - Bổ sung `npm run lint` và giảm xử lý dư thừa giúp giữ độ trễ & API latency ở mức thấp.

---

> **Lưu ý:** Bot này đã được chỉnh sửa để bạn có thể dễ dàng tùy chỉnh thành bất kỳ bot nào bạn muốn. Nếu bạn không biết cách làm, chỉ cần đưa cho AI. Nếu thất bại... quá tệ! 😝

## 📄 Giấy Phép

Tự do sử dụng, chỉnh sửa và phân phối. Không yêu cầu ghi công.

## 🤝 Tín Dụng

- Được hỗ trợ bởi Discord.js
- AI bởi NVIDIA 
- Được tạo với 💖 bởi Doro

## 🔧 GitHub Actions Workflow

1. Thêm các secrets `DISCORD_BOT_TOKEN`, `NVIDIA_API_KEY`, `BOT_OWNER_IDS`, `REPO_TOKEN` (PAT có quyền repo/workflow) và (nếu cần) `DISCORD_WEBHOOK_URL` tại **Settings → Secrets and variables → Actions**.
2. Mỗi lần push lên `main`, workflow `doro-bot` sẽ tự chạy bước lint (`npm run lint`) trên Node.js 22.12.0 để đảm bảo mọi file `.js` hợp lệ.
3. Để chạy bot trực tiếp từ GitHub, mở tab **Actions**, chọn workflow `doro-bot` rồi bấm **Run workflow**. Job `run-bot` sẽ cài đặt dependency production và chạy `node index.js` trên Node.js 22.12.0 (các lệnh nhạc vẫn cần máy hỗ trợ voice, runner chỉ dùng cho tính năng text).
4. Khi chạy `run-bot`, workflow sẽ tự động restart bot nếu bị crash, chạy trong ~6 giờ (dừng sớm 20 giây), commit các file dữ liệu `.json`, và nếu đã qua 5,5 giờ kèm commit thành công thì sẽ tự kích hoạt workflow tiếp theo để phiên mới nối tiếp ngay.
- Chạy với Node.js 22.12.0 cho hiệu suất tối ưu
- Tự động cài đặt FFmpeg cho phương tiện
- Theo dõi và quản lý trạng thái qua GitHub

### Cấu Hình Secrets

Thêm các secrets sau vào GitHub repository của bạn:
- `DISCORD_BOT_TOKEN` - Token bot Discord của bạn
- `NVIDIA_API_KEY` - Khóa API NVIDIA của bạn
- `BOT_OWNER_IDS` - Discord ID của bạn (phân cách bằng dấu phẩy)
- `DISCORD_WEBHOOK_URL` - (Tùy chọn) URL webhook Discord cho thông báo

---

*Doro Bot - Người Bạn Đồng Hành Discord Dễ Thương Của Bạn!* 🌸
