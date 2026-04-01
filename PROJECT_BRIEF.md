# PROJECT BRIEF — ADG DEALER
## Hệ Thống Quản Lý & Phân Loại Khách Hàng / Đại Lý

Phiên bản: v1.0
Ngày cập nhật: 31/03/2026
Chủ dự án: Dương
Đơn vị: ADG (Ngành Vật liệu Xây dựng)

---

# 1. Giới thiệu

## 1.1. Mục đích

Tài liệu này là bản mô tả tổng quan (Project Brief) cho dự án "ADG Dealer — Hệ thống Quản lý & Phân loại Khách hàng / Đại lý". Tài liệu được biên soạn nhằm giúp tất cả các bên liên quan (chủ dự án, đội phát triển, đội kinh doanh) có cùng một hiểu biết thống nhất về mục tiêu, phạm vi, chức năng, dữ liệu và luồng hoạt động của hệ thống. Tài liệu cũng đóng vai trò làm cơ sở để đánh giá, nghiệm thu sản phẩm và làm nền tảng cho các tài liệu kỹ thuật chi tiết hơn trong tương lai.

## 1.2. Bối cảnh

ADG là doanh nghiệp sản xuất và phân phối vật liệu xây dựng (nhôm, cửa cuốn, nội thất tổng hợp) với mạng lưới hàng chục nghìn khách hàng trải dài từ Miền Bắc đến Miền Nam. Hiện tại, dữ liệu khách hàng đang được quản lý phân tán trên nhiều file Excel rời rạc bởi nhiều nhân viên kinh doanh (sales) khác nhau. Mỗi sales tự giữ một bản dữ liệu của riêng mình, dẫn đến tình trạng thông tin bị trùng lặp, không đồng nhất, và không có cái nhìn toàn cảnh từ cấp quản lý.

Một vấn đề nghiêm trọng nữa là không có tiêu chí phân loại khoa học. Cột "Loại khách hàng" trong các file Excel hiện tại có tới hơn 60 giá trị khác nhau, nhiều giá trị vô nghĩa hoặc gõ sai, khiến việc phân tích phân khúc khách hàng gần như bất khả thi. Công ty không thể trả lời được câu hỏi cơ bản nhất: trong 15 nghìn khách hàng, ai là đại lý tiềm năng đáng đầu tư nguồn lực, ai là khách vãng lai có thể bỏ qua.

Ngoài ra, không có hệ thống ghi nhận lịch sử thay đổi (audit trail), nên khi một thông tin bị sửa sai, không ai biết ai đã sửa, sửa lúc nào, và giá trị cũ là gì.

Dự án ADG Dealer ra đời để giải quyết trọn vẹn các vấn đề trên. Hệ thống tập trung hóa toàn bộ dữ liệu khách hàng vào một nền tảng web duy nhất, gán mã định danh bất biến cho mỗi khách hàng, tự động chấm điểm và phân hạng theo 9 tiêu chí chuyên ngành, và ghi lại mọi thao tác sửa đổi để đảm bảo tính minh bạch và kiểm soát.

---

# 2. Phạm vi Hệ thống (Scope)

## 2.1. Trong phạm vi (In Scope)

Hệ thống bao gồm các nhóm chức năng sau:

Thứ nhất là quản lý khách hàng. Hệ thống cho phép xem danh sách toàn bộ khách hàng dưới dạng bảng phân trang, tìm kiếm theo nhiều tiêu chí, lọc nhanh, thêm mới, sửa trực tiếp trên bảng hoặc qua form chi tiết, xóa mềm, khôi phục, hoàn tác thay đổi, sửa hàng loạt nhiều khách cùng lúc, và tìm-thay thế giá trị trong một cột. Mỗi khách hàng được gán một Mã KH duy nhất dạng KH-00001 và mã này không bao giờ thay đổi bất kể thông tin có được cập nhật ra sao.

Thứ hai là nhập liệu từ Excel. Hệ thống cho phép upload file Excel theo template 19 cột chuẩn, xem trước dữ liệu trước khi import, kiểm tra trùng lặp dựa trên số điện thoại, và lựa chọn một trong ba chiến lược xử lý trùng (smart merge, bỏ qua, hoặc đè toàn bộ).

Thứ ba là hệ thống chấm điểm và phân loại. Mỗi khách hàng được đánh giá trên 9 tiêu chí (C1 đến C9) với trọng số có thể tùy chỉnh. Dựa trên tổng điểm, hệ thống tự động xếp hạng Tier A, B, C hoặc D. Với các trường hợp đặc biệt mà khách chọn "Khác", hệ thống hỗ trợ gọi AI (Google Gemini) để phân tích và chấm điểm tự động.

Thứ tư là dashboard thống kê. Hệ thống cung cấp trang tổng hợp với các chỉ số chính và biểu đồ trực quan về phân bổ theo Tier, Tỉnh, Loại KH, và Nguồn.

Thứ năm là xuất dữ liệu. Hệ thống cho phép export toàn bộ hoặc theo bộ lọc ra file Excel đa sheet với định dạng chuyên nghiệp, bao gồm sheet dữ liệu khách hàng, sheet nhật ký thay đổi, và sheet tổng hợp dashboard.

Thứ sáu là nhật ký thay đổi. Mọi thao tác trên hệ thống đều được ghi lại đầy đủ, bao gồm thời gian, loại hành động, chi tiết thay đổi, mã khách hàng liên quan, và người thao tác.

## 2.2. Ngoài phạm vi (Out of Scope)

Các chức năng sau hiện chưa nằm trong phạm vi phiên bản này nhưng có thể phát triển trong tương lai: hệ thống đăng nhập và phân quyền nhiều người dùng, ứng dụng mobile, tích hợp Zalo OA hoặc SMS marketing, kết nối với hệ thống ERP hoặc kế toán, báo cáo doanh thu theo từng dealer, quy trình phê duyệt (approval workflow), và chatbot tư vấn dựa trên dữ liệu.

---

# 3. Mô tả Tổng quan

## 3.1. Đối tượng Người dùng

Người dùng chính của hệ thống ở phiên bản hiện tại là Dương, với vai trò vừa là quản lý dự án vừa là người vận hành hệ thống. Dương chịu trách nhiệm import dữ liệu từ các file Excel của đội sales, duy trì và làm sạch dữ liệu, cấu hình trọng số chấm điểm, review các trường hợp cần AI hỗ trợ, và export báo cáo cho ban lãnh đạo.

Trong tương lai, khi hệ thống mở rộng phân quyền, đối tượng người dùng sẽ bao gồm thêm nhân viên kinh doanh (sales), quản lý vùng miền, và ban giám đốc, mỗi vai trò có mức độ xem và chỉnh sửa dữ liệu khác nhau.

## 3.2. Luồng Người dùng (User Flow)

### Luồng 1: Import dữ liệu từ Excel

Bước 1. Người dùng truy cập trang "Import Excel" từ sidebar bên trái.

Bước 2. Người dùng kéo thả hoặc click chọn file Excel (.xlsx) cần import. File phải có ít nhất 3 header được hệ thống nhận diện (ví dụ: "Loại KH", "Họ Tên Chủ", "SĐT").

Bước 3. Hệ thống đọc file, tự động phát hiện dòng header, map các cột Excel vào 19 trường dữ liệu tương ứng trong hệ thống. Đồng thời, hệ thống chuẩn hóa toàn bộ số điện thoại (xóa ký tự rác, thêm số 0 đầu nếu thiếu, tách SĐT dính liền).

Bước 4. Hệ thống hiển thị màn hình Preview với thông tin: tổng số dòng có trong file, số lượng dòng bị trùng SĐT với dữ liệu đã có, và bảng xem trước 10 dòng đầu tiên. Nếu có dòng trùng, hệ thống còn hiển thị mẫu so sánh giữa dữ liệu mới và dữ liệu cũ.

Bước 5. Người dùng chọn chiến lược xử lý trùng. Có ba lựa chọn. Một là "Smart merge" (mặc định): với mỗi dòng trùng SĐT, hệ thống giữ lại giá trị cũ ở các ô mà dữ liệu mới để trống, chỉ ghi đè ở những ô có giá trị mới. Hai là "Bỏ qua": dòng nào trùng SĐT thì bỏ qua hoàn toàn, không thay đổi gì. Ba là "Đè toàn bộ": ghi đè toàn bộ thông tin của bản ghi cũ bằng dữ liệu mới.

Bước 6. Người dùng bấm nút "Import". Hệ thống xử lý từng dòng một theo thứ tự từ trên xuống dưới của file Excel. Mỗi dòng mới (SĐT chưa tồn tại) sẽ được chèn vào database và được cấp một Mã KH tự động (KH-00001, KH-00002...). Mỗi dòng trùng sẽ được xử lý theo chiến lược đã chọn. Sau khi chèn hoặc cập nhật, hệ thống tự động tính điểm C1-C9 và xếp hạng Tier cho bản ghi đó.

Bước 7. Hệ thống hiển thị kết quả import: bao nhiêu dòng được thêm mới, bao nhiêu dòng được cập nhật, bao nhiêu dòng bị bỏ qua. Người dùng có thể bấm "Xem danh sách KH" để kiểm tra dữ liệu vừa import.

### Luồng 2: Xem và tìm kiếm khách hàng

Bước 1. Người dùng truy cập trang "Khách hàng" (trang chủ). Hệ thống hiển thị bảng danh sách với 50 khách hàng mỗi trang, sắp xếp theo thứ tự ID tăng dần (tức là đúng thứ tự lần import đầu tiên).

Bước 2. Để tìm kiếm, người dùng có thể gõ từ khóa vào ô tìm kiếm. Mặc định hệ thống tìm trên nhiều cột cùng lúc (Mã KH, Họ tên, SĐT, Công ty, Tỉnh). Người dùng cũng có thể chọn dropdown "Tìm theo cột" để giới hạn phạm vi tìm kiếm vào một cột cụ thể, ví dụ chỉ tìm theo SĐT hoặc chỉ tìm theo Mã KH.

Bước 3. Để lọc nhanh, người dùng sử dụng các dropdown filter phía trên bảng: Loại KH, Khu vực, Tỉnh, Tier, Nguồn. Hệ thống tự động nạp danh sách giá trị có trong dữ liệu cho mỗi dropdown.

Bước 4. Để chuyển trang, người dùng bấm nút "Trước" hoặc "Sau" ở cuối bảng. Dòng thông tin trang hiện tại và tổng KH luôn hiển thị.

### Luồng 3: Sửa thông tin khách hàng

Có hai cách sửa thông tin:

Cách 1 — Sửa trực tiếp trên bảng (Inline editing). Người dùng double-click vào bất kỳ ô nào có thể sửa (SĐT, Loại KH, Tỉnh, Quận/Huyện, Địa chỉ, Khu vực, Nguồn, và các trường scoring). Ô đó chuyển thành ô nhập liệu. Người dùng gõ giá trị mới rồi nhấn Enter để lưu hoặc Escape để hủy. Hệ thống tự động lưu thay đổi, tính lại điểm nếu cần, và ghi lại thao tác vào nhật ký.

Cách 2 — Sửa qua form chi tiết. Người dùng double-click vào cột "Tên" của một khách hàng. Hệ thống mở popup modal hiển thị form chi tiết với 3 tab: tab "Thông tin chung" (10 trường cơ bản), tab "Chấm điểm AI" (9 trường scoring), và tab "Ghi chú Sale" (trường Thông Tin Chi Tiết dạng textarea). Trên đầu form, hệ thống hiển thị Tier và tổng điểm hiện tại. Người dùng sửa các trường cần thiết rồi bấm "Lưu". Hệ thống cập nhật dữ liệu, tính lại c_score và Tier, ghi log chi tiết những trường nào đã thay đổi (giá trị cũ → giá trị mới).

### Luồng 4: Hoàn tác thay đổi (Undo)

Bước 1. Sau khi sửa một khách hàng qua form chi tiết, hệ thống lưu tạm trạng thái trước khi sửa vào bộ nhớ trình duyệt.

Bước 2. Nếu người dùng nhận ra sửa sai, người dùng mở lại form chi tiết của khách hàng đó và bấm nút "Hoàn tác".

Bước 3. Hệ thống khôi phục toàn bộ các trường input về giá trị trước lần sửa cuối cùng, tính lại điểm, và ghi log "Undo".

### Luồng 5: Sửa hàng loạt và Tìm-Thay thế

Luồng Sửa hàng loạt (Batch edit). Bước 1: Người dùng tick chọn checkbox ở từng dòng hoặc tick "Chọn tất cả" ở header. Bước 2: Thanh công cụ batch hiện ra, hiển thị số lượng KH đã chọn. Bước 3: Người dùng chọn trường cần sửa (ví dụ "Loại KH") và nhập giá trị mới (ví dụ "Đại lý"). Bước 4: Bấm "Áp dụng", hệ thống cập nhật trường đó cho tất cả KH đã chọn cùng lúc.

Luồng Tìm và Thay thế. Bước 1: Người dùng bấm nút "Tìm & Thay thế" trên header. Bước 2: Popup hiện ra cho phép chọn cột, nhập giá trị cũ cần tìm (ví dụ "Hải Dương") và giá trị mới thay thế (ví dụ "Hải Phòng"). Bước 3: Người dùng bấm "Thay thế tất cả". Hệ thống tìm tất cả bản ghi có giá trị khớp chính xác trong cột đã chọn và đổi sang giá trị mới, đồng thời thông báo đã thay thế thành công bao nhiêu bản ghi.

### Luồng 6: Chấm điểm AI cho trường hợp đặc biệt

Bước 1. Khi import hoặc nhập liệu, nếu một khách hàng có bất kỳ tiêu chí Dropdown nào (C2, C3, C4, C5, C7, C8) được chọn giá trị "Khác", hệ thống đánh dấu khách hàng đó là "Cần review".

Bước 2. Người dùng truy cập trang "Cần review" từ sidebar. Trang này liệt kê tất cả khách hàng cần review, hiển thị rõ tiêu chí nào đang ở trạng thái "Khác".

Bước 3. Với mỗi khách hàng, người dùng bấm nút "AI C3" (hoặc C2, C4, C5, C7, C8 tương ứng). Hệ thống gửi nội dung trường "Thông Tin Chi Tiết" của khách hàng cùng rubric chấm điểm 3 mức (0, 1, 2) tới Google Gemini API.

Bước 4. Gemini phân tích nội dung và trả về kết quả: điểm (0, 1, hoặc 2) kèm lý do giải thích. Hệ thống cập nhật điểm cho tiêu chí đó, tính lại tổng điểm và Tier.

Bước 5. Nếu kết quả AI chưa chính xác, người dùng có thể sửa điểm thủ công. Khi tất cả các tiêu chí "Khác" đã được xử lý, người dùng bấm "Xong" để đánh dấu khách hàng đó đã review xong, và khách hàng sẽ biến mất khỏi danh sách cần review.

### Luồng 7: Export báo cáo Excel

Bước 1. Người dùng có thể áp dụng các bộ lọc (Loại KH, Khu vực, Tỉnh, Tier, Nguồn) trước để chỉ export phần dữ liệu mong muốn, hoặc không lọc gì để export toàn bộ.

Bước 2. Người dùng bấm nút "Export Excel" trên header trang Khách hàng.

Bước 3. Hệ thống tạo file Excel với 3 sheet. Sheet "Dữ Liệu Khách Hàng" chứa toàn bộ thông tin kèm điểm scoring và Tier, được định dạng màu sắc chuyên nghiệp. Sheet "Nhật Ký Thay Đổi" chứa lịch sử toàn bộ thao tác trên hệ thống. Sheet "Tổng Hợp" chứa bảng thống kê tổng quan, phân bổ Tier, Top 10 Tỉnh, và phân bổ theo Nguồn.

Bước 4. File Excel được tự động tải về máy của người dùng.

### Luồng 8: Cấu hình trọng số chấm điểm

Bước 1. Người dùng truy cập trang "Cấu hình" từ sidebar.

Bước 2. Hệ thống hiển thị 9 tiêu chí (C1 đến C9), mỗi tiêu chí kèm tên mô tả và ô nhập trọng số (đơn vị phần trăm).

Bước 3. Người dùng thay đổi các trọng số theo ý muốn. Hệ thống hiển thị tổng trọng số đang nhập. Tổng phải bằng đúng 100 phần trăm, nếu không đúng thì chỉ số tổng sẽ hiển thị màu đỏ cảnh báo.

Bước 4. Người dùng bấm "Lưu trọng số". Hệ thống lưu trọng số mới và lập tức tính lại tổng điểm (c_score) cùng Tier cho toàn bộ khách hàng trong hệ thống. Thao tác này cũng được ghi vào nhật ký, bao gồm cả giá trị trọng số cũ và mới.

---

# 4. Đặc tả Yêu cầu

## 4.1. Yêu cầu chức năng (Functional Requirements)

FR-01: Hệ thống phải cho phép hiển thị danh sách khách hàng dưới dạng bảng phân trang với tối đa 50 bản ghi mỗi trang, sắp xếp theo thứ tự ID tăng dần.

FR-02: Hệ thống phải cho phép tìm kiếm khách hàng theo từ khóa trên nhiều cột (Mã KH, Họ tên, SĐT, Tên công ty, Tỉnh) hoặc giới hạn tìm kiếm trên một cột cụ thể do người dùng chọn. Kết quả tìm kiếm phải phản hồi trong vòng 300 mili giây sau khi người dùng ngừng gõ (debounce).

FR-03: Hệ thống phải cho phép lọc nhanh khách hàng theo 5 tiêu chí: Loại KH, Khu vực, Tỉnh, Tier, và Nguồn. Danh sách giá trị trong mỗi bộ lọc phải được trích xuất tự động từ dữ liệu thực tế trong database.

FR-04: Hệ thống phải cho phép thêm mới khách hàng qua form gồm 19 trường input. Khi lưu, hệ thống tự động sinh Mã KH duy nhất theo format KH-XXXXX (ví dụ KH-00001) và tự động chấm điểm C1-C9 dựa trên dữ liệu vừa nhập.

FR-05: Hệ thống phải cho phép sửa thông tin khách hàng theo hai cách: sửa trực tiếp trên bảng bằng double-click (inline editing) và sửa qua form chi tiết dạng popup modal. Sau khi sửa, hệ thống phải tự tính lại điểm scoring và ghi log thay đổi.

FR-06: Hệ thống phải hỗ trợ xóa mềm (soft delete). Khách hàng bị xóa không bị mất khỏi database mà chỉ bị ẩn khỏi danh sách chính. Khách hàng đã xóa phải có thể được xem trên trang "KH đã xóa" và khôi phục lại trạng thái hoạt động.

FR-07: Hệ thống phải cho phép hoàn tác (undo) lần sửa cuối cùng trên một khách hàng, khôi phục toàn bộ các trường input về giá trị trước khi sửa.

FR-08: Hệ thống phải cho phép sửa hàng loạt (batch edit), tức là chọn nhiều khách hàng cùng lúc và thay đổi giá trị một trường cho tất cả các khách hàng đã chọn.

FR-09: Hệ thống phải có chức năng Tìm và Thay thế, cho phép đổi tất cả các bản ghi có một giá trị cụ thể trong một cột sang giá trị mới.

FR-10: Hệ thống phải cho phép import dữ liệu từ file Excel (.xlsx). Quá trình import gồm 3 bước: upload file, xem trước dữ liệu (preview), và xác nhận import. Hệ thống phải tự phát hiện dòng header trong file Excel (cần ít nhất 3 header được nhận diện).

FR-11: Khi import, hệ thống phải kiểm tra trùng lặp dựa trên Số Điện Thoại (SĐT). SĐT là tiêu chí duy nhất để xác định hai bản ghi thuộc về cùng một khách hàng. Hệ thống phải hỗ trợ 3 chiến lược xử lý trùng: Smart merge, Bỏ qua, và Đè toàn bộ.

FR-12: Khi import lần đầu từ database trống, thứ tự các bản ghi trên web phải giữ nguyên 100 phần trăm so với thứ tự trong file Excel gốc.

FR-13: Mã Khách hàng (ma_kh) phải là duy nhất, bất biến, và được sinh tự động theo format KH-XXXXX. Mã này không được thay đổi trong bất kỳ trường hợp nào: sửa thông tin, đổi loại KH, đổi khu vực, hay import đè.

FR-14: Hệ thống phải tự động chấm điểm C1-C9 cho mỗi khách hàng dựa trên 9 trường scoring input. Mỗi tiêu chí cho điểm 0, 1, hoặc 2. Tổng điểm (c_score) được tính bằng tổng của điểm từng tiêu chí nhân trọng số tương ứng, sau đó nhân 50 để quy về thang 100. Tier được phân hạng: A từ 75 điểm trở lên, B từ 50 đến 74, C từ 30 đến 49, D dưới 30.

FR-15: Khi khách hàng chọn giá trị "Khác" ở bất kỳ tiêu chí Dropdown nào (C2, C3, C4, C5, C7, C8), hệ thống phải đánh dấu khách hàng đó là "Cần review" và hiển thị trên trang Review. Trang Review phải cung cấp nút gọi AI Gemini để chấm điểm tự động dựa trên nội dung Thông Tin Chi Tiết.

FR-16: Hệ thống phải cho phép sửa điểm AI thủ công trong trường hợp kết quả AI chưa chính xác.

FR-17: Trọng số 9 tiêu chí phải có thể tùy chỉnh qua trang Cấu hình. Tổng trọng số phải bằng 100 phần trăm. Khi lưu trọng số mới, hệ thống phải tự tính lại c_score và Tier cho toàn bộ khách hàng.

FR-18: Hệ thống phải cung cấp trang Dashboard với 4 thẻ thống kê (tổng KH, có scoring, cần review, số khu vực) và 4 biểu đồ trực quan (phân bổ Tier, Top 10 Tỉnh, theo Loại KH, theo Nguồn).

FR-19: Hệ thống phải cho phép export dữ liệu ra file Excel (.xlsx) đa sheet với định dạng chuyên nghiệp (có header màu, freeze pane, Tier color-coded). Export phải hỗ trợ áp dụng bộ lọc trước khi xuất.

FR-20: Mọi thao tác trên hệ thống (thêm, sửa, xóa, import, undo, AI scoring, đổi trọng số, export) phải được ghi lại trong nhật ký thay đổi, bao gồm thời gian, loại hành động, chi tiết, mã KH, tên KH, và người thao tác. Thời gian hiển thị theo múi giờ Việt Nam (GMT+7).

## 4.2. Yêu cầu phi chức năng

NFR-01 Hiệu năng. Hệ thống phải xử lý được import file Excel chứa tới 15,000 dòng trong một lần mà không bị lỗi timeout hoặc crash. Trang danh sách khách hàng phải load dưới 2 giây cho mỗi trang 50 bản ghi.

NFR-02 Tính toàn vẹn dữ liệu. Mã KH phải là duy nhất tuyệt đối (ràng buộc UNIQUE trong database). SĐT đã chuẩn hóa phải giữ nguyên format xuyên suốt hệ thống. Không được mất dữ liệu khi xóa (chỉ soft delete).

NFR-03 Khả năng sử dụng. Giao diện phải trực quan, không cần đào tạo, sử dụng được ngay trên trình duyệt. Font chữ Inter dễ đọc, layout sidebar cố định bên trái giúp điều hướng nhanh.

NFR-04 Khả năng mở rộng. Cấu trúc code phải tách biệt rõ ràng giữa các tầng (routes, services, database) để dễ dàng bổ sung chức năng mới. Hệ thống scoring có thể tùy chỉnh trọng số mà không cần sửa code.

NFR-05 Bảo mật cơ bản. API key (Gemini) phải được lưu trong file .env, không hard-code trong mã nguồn. Hệ thống giới hạn kích thước file upload tối đa 50MB.

NFR-06 Tương thích. Hệ thống phải hoạt động trên các trình duyệt hiện đại (Chrome, Firefox, Edge). File Excel import và export phải tương thích với Microsoft Excel và Google Sheets.

---

# 5. Từ điển Dữ liệu Khách hàng

Phần này mô tả ý nghĩa nghiệp vụ của từng trường thông tin thuộc về một khách hàng/đại lý trong hệ thống. Đây không phải mô tả kỹ thuật database, mà là mô tả ở góc nhìn dữ liệu kinh doanh để đội sales và quản lý cùng hiểu.

### Mã Khách Hàng (ma_kh)

Mã định danh duy nhất của mỗi khách hàng trong hệ thống, ví dụ KH-00001. Mã này được sinh tự động khi khách hàng lần đầu tiên được thêm vào hệ thống (bằng tay hoặc qua import). Mã KH tồn tại suốt vòng đời của khách hàng và không bao giờ thay đổi, bất kể thông tin hay phân loại của khách hàng có thay đổi ra sao. Đây là "số chứng minh nhân dân" của mỗi khách hàng trên hệ thống ADG.

### Nhóm 1: Thông tin cơ bản (10 trường)

**Loại KH (loai_kh).** Phân loại nghiệp vụ của khách hàng, ví dụ: Đại lý, Đại lý sản xuất, Đại lý cửa cuốn, Thợ thi công, Xưởng sản xuất, Nhà thầu, Chủ nhà, Tư vấn thiết kế. Đây là trường phân loại chính để xác định khách hàng thuộc phân khúc nào trong chuỗi giá trị ngành VLXD. Một khách hàng có thể thay đổi loại theo thời gian, ví dụ từ Thợ lên Đại lý.

**Tên Công Ty / Đơn Vị (ten_cong_ty).** Tên doanh nghiệp, cửa hàng, hoặc tên thường gọi của khách hàng. Trong dữ liệu hiện tại, trường này chứa cả tên cá nhân (ví dụ "Anh Tuấn") lẫn tên công ty (ví dụ "Cty CP Kiến Trúc Xây Dựng MasHome"). Đây là trường được sử dụng phổ biến nhất để hiển thị tên khách hàng trên giao diện.

**Họ Tên Chủ (ho_ten).** Họ tên đầy đủ của chủ cửa hàng hoặc người đại diện liên hệ. Trong thực tế dữ liệu hiện tại, trường này đang trống ở hầu hết các bản ghi, vì thông tin tên thường được sales nhập vào trường Tên Công Ty thay vì tách riêng.

**Số Điện Thoại (sdt).** Số điện thoại liên lạc chính của khách hàng. Đây là trường quan trọng nhất vì được sử dụng làm tiêu chí duy nhất để xác định trùng lặp khi import dữ liệu. Mỗi khách hàng phải có ít nhất một SĐT và SĐT phải là duy nhất trong toàn bộ hệ thống. Trong trường hợp khách hàng có nhiều SĐT, các SĐT được phân tách bằng dấu gạch chéo (ví dụ: 0985586425/0365663966).

**Tỉnh (tinh).** Tỉnh hoặc thành phố nơi khách hàng có trụ sở hoặc cửa hàng chính, ví dụ: Hà Nội, TP Hồ Chí Minh, Hải Dương.

**Quận / Huyện (quan_huyen).** Quận hoặc huyện cụ thể trong tỉnh, giúp xác định vị trí chi tiết hơn.

**Địa Chỉ (dia_chi).** Địa chỉ đầy đủ hoặc mô tả vị trí cụ thể, ví dụ số nhà, tên đường, tên xã.

**Nguồn (nguon).** Nguồn gốc của dữ liệu khách hàng này, ví dụ: tên sales đã thu thập (Cường, Sơn), hoặc kênh thu thập (Hội viên HNC, Nhôm Topal, FAMI 2023). Thông tin này giúp truy vết xem ai đem khách hàng này vào hệ thống.

**Thông Tin Chi Tiết (thong_tin_chi_tiet).** Ghi chú dạng tự do (free text), chứa các thông tin bổ sung mà sales ghi lại trong quá trình làm việc với khách hàng: lịch sử liên hệ, nhu cầu, sản phẩm quan tâm, các cuộc gọi/gặp gỡ trước đó. Trường này cũng là dữ liệu mà AI Gemini phân tích khi cần chấm điểm tự động cho các trường hợp "Khác".

**Khu Vực (khu_vuc).** Vùng miền lớn mà khách hàng thuộc về. Hiện tại có hai giá trị: Miền Bắc và Miền Nam. Trường này giúp phân tách lãnh thổ quản lý theo vùng.

### Nhóm 2: Dữ liệu chấm điểm (9 trường — tương ứng 9 tiêu chí C1-C9)

Chín trường sau đây là dữ liệu đầu vào cho hệ thống chấm điểm phân loại dealer. Mỗi trường được đánh giá thành 3 mức: 0 (yếu), 1 (trung bình), 2 (tốt).

**Số KH quay lại/năm (so_kh_quay_lai) — Tiêu chí C1: Sở hữu khách hàng bền vững.** Số lượng khách hàng quay lại mua hàng mỗi năm. Nếu không có hoặc bằng 0 thì 0 điểm. Dưới 50 khách quay lại thì 1 điểm. Từ 50 khách trở lên thì 2 điểm. Tiêu chí này đo mức độ bền vững của nguồn khách hàng mà dealer đang sở hữu. Trọng số mặc định 20 phần trăm, cao nhất trong 9 tiêu chí.

**Biết lợi nhuận từng đơn (biet_loi_nhuan) — Tiêu chí C2: P&L độc lập.** Đánh giá khả năng quản lý tài chính của dealer. Giá trị có thể là: "Không biết" (0 điểm), "Biết LN nhưng DSO trên 60 ngày" (1 điểm), "Biết LN trên 15 phần trăm và DSO dưới hoặc bằng 60 ngày" (2 điểm), hoặc "Khác" (cần AI chấm). DSO là viết tắt của Days Sales Outstanding, tức số ngày trung bình để thu hồi công nợ.

**Đội thợ thi công (doi_tho) — Tiêu chí C3: Quản lý đội thi công.** Đánh giá năng lực thi công của dealer. Giá trị có thể là: "Không có đội" (0 điểm), "1-3 thợ rời theo vụ" (1 điểm), "Từ 2 thợ cơ hữu SLA ổn" (2 điểm), hoặc "Khác" (cần AI chấm). SLA là viết tắt của Service Level Agreement, tức cam kết chất lượng dịch vụ.

**Chính sách BH với khách (chinh_sach_bh) — Tiêu chí C4: Trách nhiệm cuối.** Đánh giá mức cam kết bảo hành của dealer với khách hàng cuối. Giá trị: "Đổ lỗi NCC" (0 điểm), "BH nhưng đòi hoàn NCC" (1 điểm), "Tự ký BH chịu CP" (2 điểm), hoặc "Khác". NCC là Nhà Cung Cấp, CP là Chi Phí.

**Mức quan tâm hợp tác (muc_quan_tam) — Tiêu chí C5: Động lực tham gia.** Đánh giá mức độ sẵn sàng hợp tác với ADG. Giá trị: "Không muốn đổi" (0 điểm), "Quan tâm chưa rõ lợi ích" (1 điểm), "Có nỗi đau cụ thể muốn giải" (2 điểm), hoặc "Khác".

**Bán kính KH gọi đến theo km (ban_kinh_km) — Tiêu chí C6: Kiểm soát địa bàn.** Phạm vi địa lý mà khách hàng cuối gọi đến dealer. Nếu bằng 0 hoặc không có thì 0 điểm. Dưới 5 km thì 1 điểm. Từ 5 km trở lên thì 2 điểm. Bán kính lớn cho thấy dealer có uy tín vượt ra ngoài khu vực lân cận.

**Cách quản lý data KH (quan_ly_data) — Tiêu chí C7: Kỷ luật dữ liệu.** Đánh giá mức độ chuyên nghiệp trong quản lý thông tin khách hàng. Giá trị: "Không ghi chép" (0 điểm), "Ghi Zalo/Excel rải rác" (1 điểm), "Có hệ thống xuất được lịch sử" (2 điểm), hoặc "Khác".

**Kiểm soát mua hàng (kiem_soat_mua_hang) — Tiêu chí C8: Chuỗi cung ứng.** Đánh giá khả năng chủ động trong chuỗi cung ứng. Giá trị: "Theo chỉ định NCC" (0 điểm), "Có 2-3 NCC lựa chọn" (1 điểm), "Chủ động thương lượng giá" (2 điểm), hoặc "Khác".

**Số người được giới thiệu (so_nguoi_gioi_thieu) — Tiêu chí C9: Ảnh hưởng cộng đồng.** Số người mà dealer đã giới thiệu cho ADG hoặc cho các dealer khác. Từ 3 người trở xuống thì 0 điểm. Từ 4 đến 7 người thì 1 điểm. Trên 7 người thì 2 điểm. Tiêu chí này đo mức độ ảnh hưởng và kết nối trong cộng đồng ngành.

---

# 6. Tổng kết

Dự án ADG Dealer là hệ thống quản lý khách hàng chuyên biệt cho ngành vật liệu xây dựng, được xây dựng để giải quyết ba vấn đề cốt lõi: dữ liệu phân tán trên nhiều file Excel, thiếu tiêu chí phân loại khoa học, và không có audit trail.

Hệ thống hiện tại đã hoàn thiện đầy đủ các chức năng cốt lõi bao gồm quản lý CRUD khách hàng, import Excel thông minh với cơ chế kiểm tra trùng bằng SĐT, chấm điểm tự động 9 tiêu chí (kết hợp logic rules và AI Gemini), dashboard trực quan, export đa sheet, và nhật ký thay đổi toàn diện. Mã Khách hàng dạng KH-XXXXX đã được triển khai để đảm bảo mỗi khách hàng có một định danh duy nhất, bất biến xuyên suốt vòng đời.

Về dữ liệu, hệ thống được thiết kế để quản lý quy mô từ 15,000 đến 50,000 khách hàng, với nguồn dữ liệu đầu vào chính là các file Excel tổng hợp từ đội kinh doanh. SĐT là yếu tố định danh nghiệp vụ then chốt, đảm bảo tính chính xác tuyệt đối khi hợp nhất dữ liệu từ nhiều nguồn.

Các bước tiếp theo bao gồm chuẩn hóa cột Loại KH từ hơn 60 giá trị rời rạc về khoảng 10 nhóm chính, hoàn thiện giao diện responsive cho thiết bị di động, và đánh giá khả năng mở rộng phân quyền để nhiều người dùng có thể cùng sử dụng hệ thống.
