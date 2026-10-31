
## 1. Nhiệm vụ và kết quả phải đạt

Làm lại bộ hồ sơ Indoor Pod V5 thành một hệ thống kỹ thuật dễ đọc, có thể truy vết, đủ để người thiết kế, xưởng và người lắp hiểu cùng một cách. Mỗi chi tiết phải trả lời được: là gì, lắp ở đâu, làm bằng gì, làm thế nào, gắn với ai, vì sao có hình dạng/lỗ như vậy, kiểm tra bằng gì.

Thứ tự bắt buộc: yêu cầu và kiến trúc sản phẩm → bản vẽ lắp tổng → bản vẽ cụm và mối nối → bản vẽ từng chi tiết → dữ liệu gia công và đo kiểm. Không xuất thêm hàng chục sheet part theo template cũ trước khi sửa được nền tảng này.

Những kích thước hiện tại chưa được xác nhận phải mang trạng thái rõ ràng. Nếu cần đổi kiểu dáng, kích thước bao, kiến trúc, vật liệu chính hoặc phương án liên kết quan trọng, lập đề xuất thay đổi có lý do và xin anh duyệt trước khi coi đó là thiết kế đã chốt.

Không ghi đè hoặc xóa bộ Rev01-FA. Tạo thư mục làm việc riêng, liên kết về nguồn và ghi nhật ký thay đổi. Đề xuất mã revision mới trước khi phát hành; không tự biến bản nháp thành bản được phép sản xuất.

## 2. Kiểm kê và thống nhất nguồn dữ liệu trước

1. Lập danh mục CAD gốc, STEP, PDF, DXF, BOM, spec, bản tính, dữ liệu nhà cung cấp và kết quả thử.
2. Với mỗi file, ghi mã tài liệu, revision, trạng thái, ngày, file nguồn và quan hệ với assembly/part.
3. Tìm CAD native có parameter, feature, component và drawing liên kết. Nếu chỉ có STEP thì ghi rõ giới hạn: chưa chứng minh được lịch sử feature, sketch constraint hoặc joint của CAD gốc.
4. Đọc toàn bộ các mục HOLD/TO SELECT/TO DESIGN/TO DRAW; đưa về một Issue Register có ID, part/cụm bị ảnh hưởng, việc cần làm, người xác nhận và điều kiện đóng issue.
5. Xác định nguồn kiểm soát từng loại thông tin: CAD kiểm soát hình học danh nghĩa; bản vẽ kiểm soát kích thước chức năng, datum, dung sai, vật liệu và hoàn thiện; BOM kiểm soát cấu hình và số lượng; quy trình kiểm soát cách làm và lắp. Chúng phải cùng revision và khớp nhau. Khi mâu thuẫn, dừng phát hành hạng mục liên quan và sửa nguồn; không để xưởng tự chọn file tin hơn.
6. Reconcile BOM với assembly theo từng mã. Tách số instance CAD, số chi tiết vật lý, linh kiện nằm trong cụm mua sẵn, số lượng trong bộ kit và số dự phòng. Không kết luận khớp chỉ vì một tổng số có vẻ hợp lý.

Các sai khác phải xử lý sớm trong bộ hiện tại gồm: insert M6 830001 và lỗ TV của 211000; latch/keeper giữ chỗ; trần chưa đủ chi tiết; Rev01/Rev01b lẫn trong tên file; quy tắc tháo bead kính; 615 tổng qty BOM so với 582 instance mà báo cáo model nêu. Các số này là đầu vào cần đối chiếu, chưa phải kết luận lỗi vật lý.

## 3. Hệ đo và quy ước ISO

### 3.1 Đơn vị kiểm soát

- Kích thước cơ khí: mm. Góc: °. Khối lượng trong BOM: kg. Lực: N; mô men: N·m; ứng suất: MPa; khối lượng riêng: kg/m³; khối lượng trên diện tích: kg/m². Lưu lượng có thể dùng m³/h khi ghi rõ.
- Khung tên ghi rõ UNITS: mm; đơn vị khác phải ghi trực tiếp tại đại lượng hoặc tiêu đề cột. Không cần lặp chữ mm sau mọi con số nếu toàn sheet đã khai báo nhất quán. Không để bảng tọa độ hoặc dung sai thiếu đơn vị.
- Chuẩn hóa cả SPEC, BOM, FAI, hướng dẫn lắp, đóng gói và hình minh họa; không chỉ đổi khung tên PDF.
- Với model/DXF đã là mm, không scale toàn bộ 25.4 lần. Kiểm tra đơn vị import/export và đo lại kích thước tham chiếu đã biết sau round-trip.
- Chuyển các đại lượng inch/lb thành giá trị metric có quy tắc làm tròn theo chức năng. Ví dụ tính đổi: 0.5 lb/ft² ≈ 2.441 kg/m²; 1 lb/ft² ≈ 4.882 kg/m². Xác nhận đúng loại MLV, không đổi thành kg/m³ hoặc hiểu thành khối lượng của một tấm.
- Các tên thương mại như TV 55 inch, container 40 ft HC, mã profile hoặc ren inch mua sẵn có thể giữ trong cột tên/catalog; thông số kiểm soát gia công phải ghi rõ theo metric. Chuyển đơn vị không đồng nghĩa đổi TV, container, linh kiện catalog, ren hoặc thị trường điện của sản phẩm.
- Nếu cần dữ liệu imperial để làm việc với vận tải Mỹ, đưa vào phụ lục logistics và ghi là dữ liệu tham chiếu. Không dùng hai bộ số làm hai nguồn kiểm soát độc lập.

### 3.2 Bộ quy ước bản vẽ

Áp dụng một hệ ISO thống nhất. Với dự án này, dùng first-angle projection như hướng hiện có, có ký hiệu phép chiếu và bố trí view đúng; ISO không tự động đồng nghĩa first-angle. Phải ghi rõ hướng nhìn, nhất là chi tiết có tay trái/phải hoặc bản vẽ xoay so với tư thế lắp.

Chọn và ghi edition/amendment áp dụng trong Drawing Standard của dự án. Tài liệu cần đối chiếu:

| Chủ đề | Tài liệu để kiểm tra |
|---|---|
| Trình bày kích thước và dung sai | ISO 129-1:2018 và amendment áp dụng |
| Hình chiếu trực giao | ISO 5456-2:1996 |
| Ký hiệu dung sai hình học | ISO 1101:2017 |
| Datum và hệ datum | ISO 5459:2024 |
| Dung sai kích thước chung cho phạm vi phù hợp | ISO 2768-1:1989, class được chỉ định và nhà cung cấp xác nhận |
| Đặc tả hình học chung khi cần | ISO 22081:2021, có giá trị, phạm vi và hệ datum thích hợp |

Không đóng dấu “ISO” rồi coi như đã tuân thủ. Không tự gắn ISO 2768-m lên mọi vật liệu/quy trình, đặc biệt gỗ, PET/felt, kính và cụm sandwich. Chúng cần yêu cầu riêng theo chức năng và năng lực chế tạo. Không sao chép ISO 2768-mK như quy ước mặc định: ISO 2768-2 đã được thay thế; ISO 22081 cũng không phải bảng K thay thế trực tiếp. Không trộn cách diễn giải ISO GPS với ASME một cách tùy ý.

Các trang ISO công khai chỉ xác nhận phạm vi và edition; khi áp dụng điều khoản chi tiết, cần bản tiêu chuẩn đầy đủ và người kiểm tra hiểu ISO GPS.

### 3.3 Quy ước trục tọa độ: 3D dùng X/Y/Z, 2D chỉ dùng X/Y

Đây là yêu cầu trình bày của chủ sở hữu, áp dụng thống nhất cho CAD, drawing, bảng lỗ, DXF, FAI và tài liệu giải thích:

- Trong không gian 3D, chỉ dùng X, Y, Z. Bản tổng phải thể hiện gốc O, chiều dương và hướng trước/sau/trái/phải; chốt một hệ trục thuận tay phải và giữ xuyên suốt assembly/part. Hệ tọa độ local của part vẫn gọi X/Y/Z, nhưng phải ghi rõ tên hệ và quan hệ với hệ toàn pod.
- Trên bản vẽ 2D, mỗi view/bảng tọa độ gia công chỉ dùng X và Y trong mặt phẳng view, có gốc và chiều dương rõ ràng; mặc định X sang phải, Y lên trên trên view đã định hướng. Bảng lỗ dùng cột X (mm), Y (mm). Chiều sâu, chiều dày, mặt vào và hướng khoan ghi bằng tên đặc tính riêng, không thêm cột tọa độ Z vào bảng 2D.
- Không dùng u/v/c hoặc u/v/w thay tên trục trong bộ làm lại. Các ký hiệu A/B/C cho datum, H01… cho lỗ hoặc tên section vẫn giữ đúng chức năng; chúng không phải tên trục tọa độ.
- Không đơn thuần đổi nhãn trục rồi giữ nguyên các giá trị. Khi một mặt 3D được chiếu sang view 2D, phải khai báo mapping và biến đổi tọa độ, kể cả chiều dấu/gốc. Ví dụ front view có thể lấy X-3D theo phương ngang và Z-3D theo phương đứng; trong view đó hai tọa độ vẫn đặt tên X-2D và Y-2D, với mapping ghi rõ cạnh view. Mỗi view có gốc riêng phải được định danh để không lẫn các bảng X/Y.
- Giữ quy ước phép chiếu và orientation; không mirror, xoay hoặc đổi gốc ngầm giữa PDF và DXF. Nếu flat pattern dùng hệ X/Y khác view chi tiết sau chấn, ghi rõ quan hệ và kiểm tra feature tương ứng.
- Chuyển hệ tọa độ không thay thế việc chọn datum theo chức năng. Kiểm tra lại vị trí tâm lỗ trên CAD–PDF–DXF sau chuyển đổi; không đổi hình học hoặc vị trí lỗ chỉ để có số tọa độ đẹp.

## 4. Kiến trúc sản phẩm và đặt tên part

### 4.1 Có một cây assembly duy nhất

Cây tối thiểu: POD assembly → BASE / WALL / FRONT / CEILING / LINING / AIR / ELECTRICAL / INTERIOR; PACKAGING là cấu hình giao hàng có quan hệ tới POD. Mỗi cụm có mã, tên, BOM, drawing lắp và giao diện sang cụm bên cạnh.

Phân biệt rõ manufactured part, bonded subassembly, hardware-fitted subassembly, purchased item và installation kit. 211000 chứa nhiều lớp và khung LVL: cần định nghĩa đó là cụm dán với chi tiết con, hoặc một cụm mua/gia công theo specification kiểm soát. Một STEP chứa nhiều body và một dòng “glued and pressed” không tự cung cấp quy trình chế tạo cụm này.

### 4.2 Quy tắc tên

Giữ part number hiện có nếu vẫn nhận diện đúng vật tư. Không đổi toàn bộ mã chỉ để đẹp. Tên hiển thị theo cấu trúc: [cụm] - [chức năng/chi tiết] - [vị trí] - [biến thể cần phân biệt]. Tên phải rõ ở BOM, cây CAD, PDF, STEP, DXF và nhãn thực tế.

Ví dụ cấu trúc tên, không phải lệnh đổi mã hàng loạt:

| Mã | Tên dễ nhận diện |
|---|---|
| 110006 | BASE - CORNER KEY - FRONT LEFT |
| 110002 | BASE - SIDE RAIL - COMMON LH/RH |
| 120001 | FRAME - CORNER POST - COMMON, TOP MARKED |
| 211000 | WALL - BONDED PANEL - COMMON STRUCTURE |
| 210005 | WALL - PANEL ASSY - START |
| 210001 | WALL - PANEL ASSY - INTERMEDIATE |
| 210003 | WALL - PANEL ASSY - END |
| 350011 | FRONT FASCIA - SEAM BACKER - TOP LEFT |

Chỉ dùng COMMON khi đã xác nhận hình học và thao tác gia công giống nhau. Assembly START/INTERMEDIATE/END và mã vị trí L1/B2/R2 là hai lớp thông tin khác nhau, không gộp thành một tên mơ hồ. Trước/trái/phải phải được định nghĩa trên bản tổng, ví dụ nhìn từ bên ngoài hướng vào cửa. Không suy ra từ góc camera.

Tên file theo một mẫu: PARTNO_REV_DESCRIPTIVE-NAME_DOCTYPE.ext. Revision trong tên file, khung tên, BOM và manifest phải đồng nhất; trạng thái DRAFT/HOLD/REVIEW/FA-APPROVED/PRODUCTION-APPROVED nằm ở trường riêng. Không dùng các tên final/final2/new/latest. Một thay đổi làm mất khả năng thay thế lẫn nhau phải được đánh giá để tách mã; không chỉ sửa tên.

Linh kiện tiêu chuẩn phải có hãng, exact SKU, kích thước, vật liệu/cấp bền, lớp phủ và tài liệu nguồn. “M8”, “keo tốt”, “or equal” hoặc mô hình giữ chỗ chưa phải định nghĩa vật tư được chốt.

### 4.3 Tìm hiểu phụ kiện trước khi cập nhật model và bản vẽ

Phải nghiên cứu, lựa chọn và kiểm tra giao diện của các part giữ/bắt kính và các phụ kiện liên quan trước khi cập nhật chúng hoặc pattern lắp của chúng vào bộ CAD/bản vẽ làm lại. Không vẽ một hình tưởng tượng cho vừa rồi mới tìm vật tư để thay vào sau.

Phạm vi gồm kẹp/nẹp kính, stop/bead, clip, gioăng, setting/location block, bản lề/pivot, closer, tay nắm, latch/keeper, insert, rivnut/clinch nut, móc treo và các phụ kiện khác có ảnh hưởng tới hình học, tải, thao tác lắp hoặc bảo trì. Phân biệt món mua sẵn với part tự thiết kế; part tự thiết kế vẫn phải dựa trên giao diện thật của kính, clip và hardware ghép với nó.

Trình tự bắt buộc:

1. Xác định chức năng, tải, vị trí sử dụng, vật liệu nền và chiều dày kính/tấm thực tế cần phục vụ; tách số đã chốt với số đang là giả định.
2. Tìm phương án thực có tài liệu: ưu tiên catalog, bản vẽ kích thước/CAD, datasheet và hướng dẫn lắp của đúng hãng, đúng SKU/variant. Ghi link/file nguồn, revision/ngày tra cứu, nhà cung cấp và tình trạng đặt mua; một ảnh bán hàng chưa đủ xác định giao diện.
3. Kiểm tra kích thước bao, pattern lỗ, ren/vít, mặt tỳ, chiều vào, dải kẹp/chiều dày tương thích, tải và điều kiện rating, lớp đệm/gioăng, khoảng hở và đường tháo. Riêng phụ kiện kính phải kiểm tra cả loại kính, trạng thái cạnh, yêu cầu lỗ/khoét trên kính nếu có, độ ăn kính, điểm kê và khả năng thay kính. Không suy phụ kiện dùng cho một chiều dày/loại kính sẽ dùng được cho loại khác.
4. Khi dữ liệu thiếu hoặc mâu thuẫn, ghi câu hỏi cần supplier confirmation và yêu cầu mẫu đo/thử khi cần. Chưa có xác nhận thì giữ HOLD ở giao diện liên quan; chỉ định khoảng không gian dự phòng có nhãn UNVERIFIED khi cần nghiên cứu bố trí, chưa cập nhật pattern lỗ hoặc kích thước cắt kính như dữ liệu thiết kế đã chốt.
5. Lập bảng lựa chọn phụ kiện: chức năng → PN/SKU/variant → nguồn → thông số giao diện → khả năng cung ứng → tương thích → việc còn cần xác nhận → trạng thái. Nêu lý do chọn và các đánh đổi khi thay phương án.
6. Sau khi đủ dữ liệu giao diện để tích hợp, mới cập nhật đồng bộ CAD, bản lắp/part, BOM, hole/feature register và FAI. Dùng hình học theo dữ liệu đã kiểm tra; ghi phần nào đã xác minh theo tài liệu và phần nào còn cần mẫu thử. Đủ dữ liệu để vẽ không đồng nghĩa đã được xác nhận bằng thử vật lý hoặc được phép sản xuất.

Không tự đặt mua hay liên hệ/gửi thông tin cho nhà cung cấp khi chưa được anh cho phép. Việc tra cứu tài liệu công khai và lập danh sách câu hỏi cần xác nhận có thể thực hiện ngay.

### 4.4 Bàn giao body có sketch/feature chỉnh sửa được trong CAD gốc

Yêu cầu của chủ sở hữu: về sau phải sửa trực tiếp kích thước, hình dạng, vị trí lỗ và chi tiết của từng body do dự án thiết kế, thay vì phải dựng lại từ một solid không có lịch sử.

STEP là bản trao đổi hình học, không phải nơi lưu đầy đủ sketch, constraint, parameter và timeline của Fusion. Thêm đường sketch rời vào file xuất hoặc lưu STEP dưới đuôi .f3d không đáp ứng yêu cầu. Bật Capture Design History sau khi import STEP cũng không khôi phục lịch sử dựng hình đã mất. Autodesk xác nhận giới hạn sketch và timeline của luồng import này: [sketch trong STEP import](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Imported-STEP-PART-IGES-files-don-t-contain-sketches-when-opened-in-Fusion.html), [design history của file import](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Imported-files-do-not-contain-timeline-features-in-Fusion-360.html).

Bộ bàn giao bắt buộc gồm CAD native có tham số để chỉnh sửa và STEP xuất từ đúng phiên bản CAD đó. Với workflow Fusion hiện tại, giao .f3d cho thiết kế phù hợp hoặc .f3z khi cần đóng gói assembly và các thiết kế liên kết; kèm đủ nguồn/phụ thuộc để mở và chỉnh sửa. Không coi chỉ đổi định dạng hay có một imported Base Feature là đã có model tham số.

Mỗi part/body tự thiết kế phải đáp ứng:

1. Có component/part number và tên body rõ, liên kết được với BOM/drawing. Mỗi body truy được sketch/feature tạo ra nó; không bắt buộc tạo sketch trùng lặp khi một sketch/feature chung có chủ đích điều khiển nhiều body, nhưng quan hệ phải rõ và chỉnh sửa được.
2. Có sketch cụ thể theo chức năng: biên dạng chính, mặt cắt, layout lỗ/slot hoặc đường dẫn cần thiết. Sketch nằm trên plane/datum được định nghĩa, dùng trục theo §3.3; có kích thước điều khiển và geometric constraints. Sketch thiết kế phải fully constrained; không dùng Fix toàn bộ đường để che việc thiếu quan hệ/kích thước chỉnh sửa.
3. Body thực sự được dựng và điều khiển bằng các sketch/feature đó: Extrude/Revolve/Sweep/Loft, Hole/Cut, Pattern, Fillet/Chamfer hoặc sheet-metal features tùy loại part. Không gắn thêm sketch minh họa lên một imported solid rồi gọi là body có tham số.
4. Có parameter đặt tên dễ hiểu, có unit, dùng cho các kích thước sẽ cần chỉnh: chiều dài/rộng/cao/dày, góc, bán kính, vị trí/pitch/số lỗ và các giao diện liên quan. Giữ pattern và quan hệ đối xứng bằng feature/constraint phù hợp; không sửa từng lỗ thủ công khi chúng thuộc cùng pattern thiết kế.
5. Có feature tree/timeline được đặt tên theo công năng; không có feature lỗi, sketch/reference mất liên kết hoặc phụ thuộc vòng. Ghi rõ external reference và đóng gói đủ nguồn; không xóa lịch sử hoặc flatten model trong file bàn giao.
6. Với tấm chấn, dùng mô hình sheet metal có thickness, bend rule/radius và flat pattern chỉnh sửa được khi công cụ hỗ trợ; với part khác dùng chuỗi dựng phù hợp. Không ép mọi hình học vào một sketch phức tạp khó sửa.
7. Với cụm sandwich/panel nhiều vật liệu, tách các part/body/lớp theo cấu tạo cần chế tạo và quản lý; có sketch/layout và tham số điều khiển tương ứng. Không coi một khối ngoài duy nhất là định nghĩa đủ các lớp và frame bên trong.

Linh kiện mua sẵn có thể dùng CAD hãng như imported reference với SKU/variant và trạng thái rõ; không phải dựng lại ren, chi tiết cơ cấu nội bộ hay sketch của hãng chỉ để có cây feature. Tuy nhiên toàn bộ part do dự án tự thiết kế để ghép với chúng phải có sketch/feature và tham số chỉnh sửa được. Mọi ngoại lệ với body tự thiết kế phải được nêu rõ để anh quyết định, không tự bỏ yêu cầu.

Nếu tìm được CAD gốc, kiểm tra và hoàn thiện cây tham số ngay trên nguồn đó. Nếu chỉ còn STEP, giữ STEP cũ làm hình học tham chiếu rồi dựng lại part tự thiết kế bằng sketch/feature, đối chiếu với nguồn và yêu cầu kỹ thuật đã chốt. Chỉ tạo các feature mới trên imported body có thể hỗ trợ sửa cục bộ, nhưng chưa đáp ứng việc sửa toàn bộ biên dạng gốc; phải ghi rõ giới hạn và phần đã dựng lại.

Kiểm tra khả năng sửa trước khi bàn giao:

- Mở file native từ bộ bàn giao, kiểm tra nguồn/phụ thuộc, sketch constraints, feature health và mapping body → sketch/feature/parameter. Bảng mapping này phải truy được từng body tự thiết kế; có sketch nhưng không điều khiển hình học là không đạt.
- Trên bản sao thử nghiệm, thay một kích thước điều khiển và một tham số lỗ/pattern khi có, tối thiểu trên một part đại diện mỗi họ cấu tạo và các giao diện quan trọng. Rebuild để chứng minh đúng body thay đổi, các quan hệ liên quan cập nhật và không phát sinh feature lỗi. Ghi trước/sau, tham số đã đổi và kết quả; hoàn nguyên giá trị thiết kế trước khi xuất bản bàn giao.
- Đối chiếu native ở giá trị thiết kế với STEP nguồn hoặc geometry thay đổi đã được anh duyệt: kích thước chính, tâm/trục lỗ, orientation, hình dạng và topology/solid hợp lệ. Khai báo ngưỡng và phương pháp đối chiếu; khác biệt do dựng lại phải được xử lý hoặc ghi thành thay đổi có kiểm soát.
- Xuất lại STEP/DXF/PDF từ cùng revision native sau khi rebuild; mở lại để kiểm tra đơn vị, hình học và ID part. Việc mở STEP thành công không chứng minh sketch/timeline đã được giữ; khả năng sửa phải được kiểm tra trong native.

### 4.5 Manifest nguồn chỉnh sửa

Với mỗi part tự thiết kế, manifest phải chỉ ra: Part/Rev → file native/component → body → sketch/feature tạo hình → parameter chính → drawing/STEP/DXF cùng revision → trạng thái kiểm tra khả năng sửa. Script sinh CAD có thể bàn giao thêm để tái tạo, nhưng không thay file native có thể mở và sửa trực tiếp.

## 5. Bản vẽ lắp tổng phải đứng trước bản vẽ part

### 5.1 Bộ GA: tổng thể sản phẩm

GA-001 và các sheet tiếp theo nếu cần phải có:

- Front, rear, left, right, top; thêm bottom khi cần hiểu vị trí chân/đường liên kết; một isometric để nhận diện.
- Mặt cắt dọc và ngang đi qua tường–đế–trần, cửa và kính; hướng cắt, hatch và tên lớp vật liệu rõ ràng.
- Kích thước bao ở tường/cột; footprint lớn nhất kể cả fascia/đế nhô; kích thước trong; kích thước cửa thông thủy theo trạng thái mở xác định; góc mở, khoảng nâng vào lắp, khoảng trống thao tác và tháo bảo trì.
- Thể hiện hệ 3D toàn pod bằng X/Y/Z và quy ước trái/phải/trước/sau. Các view/bảng tọa độ 2D chỉ dùng X/Y, có mapping về hệ 3D theo §3.3. Phân biệt hệ tọa độ với datum riêng của từng part.
- Mã vị trí L1…R2, C1…C3, FL/FR/BL/BR, balloon item khớp BOM và dẫn tới bản vẽ cụm.
- Kích thước và khe hở giao diện quan trọng: panel–post, ring–post, header–infill, kính–khung, gioăng, lining–trần. Ghi trạng thái sau sơn, sau dán hoặc sau nén khi liên quan.
- Một exploded view có thứ tự lắp và hướng đưa chi tiết vào; dùng thêm sheet nếu quá chật.

Không nhồi tất cả view lên một A3. Chọn A2/A1 hoặc chia sheet khi cần; hình và kích thước phải đọc được ở khổ in công bố. Sách lắp theo từng bước vẫn cần, nhưng phải tham chiếu bộ GA/cụm này và không thay thế chúng.

### 5.2 Bản vẽ từng cụm

Làm bản lắp BASE, WALL, FRONT/DOOR/GLAZING, CEILING và LINING trước các part tương ứng. Mỗi cụm có hình lắp, hình nổ khi cần, BOM item, mặt cắt mối nối, datum/giao diện, chuỗi dung sai, yêu cầu kiểm tra và trình tự siết/dán/lắp.

Cụm điện/air/packaging thể hiện ở mức tương xứng với độ hoàn thiện hiện tại; phần chưa thiết kế giữ trạng thái rõ. Không dùng hình vẽ minh họa để che phần chưa có geometry hay hardware thật.

## 6. Bản vẽ part: kéo kích thước đúng feature

### 6.1 Hình và bố cục

- Ưu tiên native drawing có liên kết với CAD. Nếu công cụ khác được dùng, phải sinh đúng cạnh/đường tròn, hidden line, section và annotation từ hình học có kiểm tra, cập nhật được theo nguồn; không dùng ảnh mesh/tessellation để giả bản vẽ chế tạo.
- Có đủ hình chiếu để định nghĩa hình dạng, mặt cắt và detail cho phần khuất/nhỏ; thêm isometric nhỏ để nhận diện khi hữu ích.
- Không lấy kích thước hộp bao thay cho kích thước chế tạo. Với tấm xoay/nghiêng, ghi chiều dài/rộng thật theo cạnh và góc; với tấm chấn, ghi chiều dày, bán kính trong, góc và kích thước cánh/offset.
- Dành diện tích cho hình và kích thước. Chuyển quy định chung sang sheet General Notes, giữ ghi chú riêng ngắn và gần feature liên quan. Không thu nhỏ font để nhét một trang; thêm sheet khi cần.
- Vẽ đúng đường tròn/cung cho lỗ tròn, center mark, centerline, hidden line, đường cắt và hatch đúng chức năng. Nếu PDF cho lỗ thành đa giác thì sửa bộ xuất bản vẽ, không suy ngược rằng lỗ CAD đã đúng hoặc sai chỉ từ ảnh.

### 6.2 Định vị tâm lỗ

Mỗi lỗ/pattern/slot phải xác định duy nhất được: nằm trên mặt nào, gia công từ phía nào, loại gì, kích thước gì, tâm/trục ở đâu, sâu bao nhiêu, dung sai gì và ghép với linh kiện nào.

- Đường gióng kích thước vị trí phải bám center mark/trục thật của lỗ, không bám mép lỗ, đường silhouette, mép hộp bao hoặc điểm ước lượng bằng mắt.
- Mỗi lỗ có mã H01/H02… hoặc mã pattern trên view. Ghi baseline/ordinate từ các datum được chọn theo chức năng và đồ gá. Tránh chuỗi kích thước nối tiếp gây cộng dồn sai số.
- Các lỗ ghép quan trọng phải có kích thước tới tâm và quan hệ pitch trực tiếp trên hình. Bảng lỗ dùng cho nhóm lặp hoặc số lượng lớn vẫn phải có tag tương ứng trên view, cột X (mm), Y (mm), gốc/chiều dương, mặt vào và datum rõ ràng theo §3.3; không chấp nhận một đoạn liệt kê cặp tọa độ thay toàn bộ annotation.
- Lỗ cùng trục ở hai vách ống cần hình cắt hoặc view đối diện để phân biệt lỗ luồn vít, lỗ truy cập dụng cụ và lỗ làm việc. Ghi yêu cầu đồng trục/vị trí khi chức năng cần.
- Tách lỗ THRU, lỗ mù, lỗ taro, counterbore, countersink, reamed hole, lỗ rivnut/clinch nut và lỗ mồi gỗ. Lỗ mù phải phân biệt chiều sâu khoan và chiều sâu làm việc/ren hữu dụng.
- Slot phải ghi width, overall length, bán kính đầu, hướng và vị trí; định nghĩa length có tính hai đầu bo hay không. Hole Register phải bao gồm slot/cutout, không chỉ lỗ tròn.
- Không bỏ đường kính/lỗ ra khỏi view rồi ghi ở đoạn văn xa bên cạnh. Không lặp cùng một kích thước làm hai yêu cầu kiểm soát; kích thước nhắc lại phải ghi tham chiếu.

### 6.3 Datum và dung sai

Chọn datum A/B/C từ các mặt/trục thực có thể gá và đo, theo cách part lắp và chịu tải. Không mặc định dùng góc min của bounding box làm chuẩn cho mọi part. Gốc tọa độ CAD hoặc ký hiệu D đơn lẻ không tự tạo ra hệ datum đầy đủ.

Mỗi kích thước kiểm soát có dung sai riêng hoặc thuộc một quy tắc chung có phạm vi rõ. Lỗ insert, chốt định vị, pattern ghép và vị trí kính/gioăng cần dung sai xuất phát từ lắp ghép, không tự dùng ±0.3 cho tất cả. Với đặc trưng hình học, dùng ISO GPS khi phù hợp và có phương pháp đo tương ứng. Không coi ± tọa độ là tương đương vùng dung sai vị trí hình trụ.

Ví dụ số chỉ để phân biệt cách ghi, chưa được phép dùng làm thiết kế: X = 40 ±0.2 và Y = 20 ±0.2 tạo hai giới hạn tọa độ; một callout vị trí Ø0.4 theo A/B/C là một yêu cầu khác. Nếu dùng kích thước lý thuyết chính xác (TED), chúng phải đi cùng đặc tả hình học thích hợp; không thêm dấu ± vào TED.

Với lỗ clinch nut hiện có, hồ sơ ghi Ø8.75 +0.08/0 và mục tiêu CAM 8.79. Agent phải kiểm tra lại datasheet đúng nut/vật liệu/chiều dày, ghi giới hạn chức năng trên drawing và giữ mục tiêu CAM ở dữ liệu quy trình; không biến Ø8.79 thành nominal rồi cộng dung sai chung gây mâu thuẫn.

Tính tolerance stack ở các giao diện quan trọng: vị trí lỗ hai part + đường kính vít/lỗ + lớp phủ + biến dạng/gioăng; cửa–khung; kính–stop/bead; header–infill; panel–post; nâng/tháo lining. Kiểm tra trường hợp biên, không chỉ nominal. Chỉ dùng RSS khi có giả thiết thống kê và dữ liệu quy trình phù hợp.

Chỉ định đo trước/sau sơn, trước/sau ép và trạng thái nén của vật liệu mềm. Chốt dụng cụ/phương pháp đo và năng lực xưởng trước khi coi dung sai là làm được; không siết mọi kích thước quá chặt để tạo cảm giác chính xác.

## 7. Mọi vị trí lỗ và khoảng cách phải có lý do

Lập Feature Rationale Register, được phép nhóm các feature giống hệt về chức năng. Các trường tối thiểu:

    Feature ID | Part + Rev | Drawing/view | Chức năng | Part ghép/SKU
    Kích thước/offset/pitch | Nguồn ràng buộc hoặc bản tính
    Khoảng mép/khoảng chấn/không gian dụng cụ | Tolerance stack
    Phương pháp chế tạo và kiểm tra | Trạng thái bằng chứng

Lý do hợp lệ có thể là pattern chuẩn của hardware thật; truyền lực/khống chế biến dạng; lực kẹp và độ kín gioăng; chống xoay; khoảng mép/tách nứt; khả năng chấn/gia công; đường dụng cụ; hành trình tháo; hoặc điều chỉnh sai số có chủ ý. “Cho đều”, “trông cân”, “theo model cũ” hoặc “AI đề xuất” không đủ để biện minh lỗ chịu lực/lỗ ghép.

Ví dụ 110006 hiện có pitch 40 và 60 mm, tâm một số lỗ cách mép 10 mm. Hãy truy từng lỗ sang lỗ ghép của rail, nut 830005, không gian đầu vít/dụng cụ, khoảng mép theo datasheet và tải. Không tự bịa rằng 40/60 là tối ưu. Nếu thiết kế cũ thiếu căn cứ, ghi UNJUSTIFIED rồi tính/so sánh phương án và thử trước khi chốt.

Không dùng một hệ số e/d hay khoảng cách vít cố định cho mọi vật liệu. Phải phân biệt khoảng cách tâm–mép, phần vật liệu còn lại từ mép lỗ đến mép part và khoảng cách giữa hai feature. Gỗ/LVL, nhôm mỏng và clinch nut có điều kiện khác nhau. Không coi câu “mọi ≤300 mm” là đủ nếu chưa tính điểm đầu/cuối, góc, nhịp, độ cứng và khả năng lắp.

Khoảng hở giữa part cũng phải có vai trò: khe thẩm mỹ, bù sơn, giãn nở, nén seal, dung sai lắp hoặc tháo bảo trì. Ghi mức nhỏ nhất/lớn nhất được chấp nhận và cách kiểm tra.

## 8. Mỗi mối nối phải có một quyết định kỹ thuật

Lập Joint Register theo J-BASE-01, J-WALL-01…; link tới drawing detail và feature IDs. Với mỗi loại mối nối, ghi:

    Joint ID | Hai part/cụm | Chức năng + đường truyền tải
    Tải/điều kiện sử dụng + nguồn | Yêu cầu tháo/bảo trì
    Phương án so sánh | Phương án chọn + lý do
    SKU/vật liệu/quy trình | Bản tính + tolerance stack
    Hướng lắp/dụng cụ/trình tự | Hỏng có thể xảy ra
    Cách xác minh + tiêu chí đạt | Trạng thái

So sánh keo, vít/insert, rivnut/clinch nut, rivet, hàn hoặc giải pháp kết hợp tùy mối nối thực. Không ép mọi joint phải thử hết các công nghệ. Quyết định quan trọng phải nêu ảnh hưởng tới công năng, độ cứng, khối lượng, chi phí, thời gian làm/lắp, khả năng chế tạo, độ tin cậy, sửa chữa và rủi ro.

### 8.1 Khi dùng vít/bu lông/insert

- Chốt chuẩn, exact size/pitch/length/head, cấp bền, vật liệu và lớp phủ; xác định con nào là vật tư mua sẵn và con nào là chi tiết gia công.
- Vẽ mặt cắt stack thực: chiều dày các lớp, washer, spacer, khoảng hở, ren ăn thực, đáy lỗ và phần vít nhô. Tính ở cả hai biên dung sai. Không được chạm đáy trước khi kẹp chặt, thiếu ren ăn hoặc đâm ra bề mặt sử dụng.
- Vít phải neo vào nền phù hợp: LVL/batten/block được thiết kế, insert/rivnut/nut/tapped boss có định nghĩa. Không mặc định PET/felt, MLV, MDF mỏng hoặc lớp HPL là nền giữ vít chịu lực.
- Vít vào gỗ phải có lỗ mồi, hướng thớ, độ ẩm, khoảng mép, chiều sâu ăn và thử rút/tuột ren theo vật liệu thật. Không lấy tải quảng cáo của insert áp cho LVL đang dùng nếu chưa có bằng chứng tương ứng.
- Với rivnut/clinch nut, kiểm tra đúng hole, grip/thickness range, độ cứng vật liệu nền, tâm–mép, chiều ép/tán, khả năng chống xoay, tải kéo/đẩy và trình tự sơn. Không suy “M6” là tương thích với mọi lỗ M6.
- Torque phải dựa trên joint, nền yếu nhất, điều kiện khô/bôi trơn/lớp phủ và thử thực tế. Một giá trị trần “≤5 N·m” hoặc “≤10 N·m” chưa phải dải siết được xác nhận. Không lấy bảng torque bu lông thép rồi áp thẳng cho insert gỗ hoặc rivnut nhôm.
- Chỉ định chống lỏng khi cần và đánh giá khả năng tháo lại; nếu dùng threadlocker, chốt loại, nền tương thích và quy trình.
- Chứng minh đường đưa vít, chiều vào khóa, khoảng quay dụng cụ, khả năng giữ nut và thao tác tay theo đúng thứ tự lắp. Không dùng một rigid joint trong CAD làm bằng chứng bắt vít được ngoài thực tế.
- Xét rung, tải lệch tâm, ép lún, creep, ăn mòn tiếp xúc và số lần tháo/lắp khi liên quan. Không tự cộng sức chịu tải của các vít nếu phân phối tải chưa được chứng minh.

### 8.2 Khi dùng keo/băng dính/sealant

Phân biệt keo kết cấu, keo ép lớp, keo giữ vật liệu mềm, băng keo giữ gioăng và sealant bịt kín. Một sản phẩm không tự thay được các vai trò còn lại.

Mỗi bond có specification tối thiểu:

- Mã hãng/SKU và revision TDS/SDS; hai bề mặt cụ thể, lớp sơn/phim/bề mặt có xử lý hay không.
- Chuẩn bị bề mặt: làm sạch, chà nhám, primer, độ ẩm gỗ hoặc điều kiện khác theo TDS.
- Vùng dán, overlap, chiều dày bondline hoặc lượng phủ theo g/m²; cách chống thiếu keo/tràn keo và kiểm tra độ phủ.
- Tỷ lệ pha nếu có, pot life/open time, áp lực ép, nhiệt độ, thời gian giữ gá và cure, điều kiện đủ để tháo gá/đóng gói/chịu tải.
- Tải shear/peel/cleavage, tải lâu dài/creep, rung và môi trường thực. Không suy sức bền từ một con số lap-shear catalog.
- Tương thích với HPL, keo nền ván, MLV có plasticizer, PET/felt và powder coat. Làm coupon trên đúng stack và quy trình sản xuất dự kiến.
- Tiêu chí mẫu đạt, số mẫu/điều kiện thử được phê duyệt, dấu hiệu hỏng, sửa chữa và truy vết lô.

“PUR/PVAc/EVA” và “no-added-formaldehyde” chỉ là mô tả họ keo/yêu cầu phát thải, không phải bằng chứng keo dán được mọi cặp HPL–MLV–gỗ–PET. Chọn hệ keo cho từng giao diện. Mối dán làm panel tham gia chịu lực cần chứng minh độ bền liên kết và creep của cụm thật.

Không mặc định dùng keo vĩnh viễn ở giao diện cần tháo bảo trì. Không thay liên kết giữ kính, trần hoặc cửa bằng keo/băng keo chỉ vì nhìn sạch hơn. Đối với các cụm này, phải có đường truyền tải và cơ cấu giữ phù hợp được kiểm tra.

## 9. Quy trình gia công phải bám vật liệu và xưởng thật

- Sheet metal: thickness/grade/temper, bán kính và góc chấn, bend relief, hướng chấn, datum sau chấn, chiều dài cánh, giới hạn công cụ, bù sơn. K-factor/bend allowance phải được hiệu chuẩn bằng coupon với vật liệu và bộ dao thật.
- Flat pattern DXF phải 1:1, khai báo mm, outline kín, không trùng cạnh, layer CUT/BEND/MARK rõ; circle/arc đúng. Kiểm tra các lỗ gần đường chấn và đối chiếu sau chấn với STEP/drawing. Không coi DXF nominal là file cắt đã được xưởng chứng minh.
- Profile/tube: tiêu chuẩn profile, độ dày thực, mặt chuẩn, miter, plug/cap, lỗ hai vách và khả năng khoan/gá. Nếu hàn, chỉ định joint, vật liệu phụ/quy trình phù hợp và kiểm tra biến dạng, mặt thẩm mỹ sau hoàn thiện.
- Wood/sandwich: loại ván/LVL, hướng thớ, cut list, vị trí rail/block, CNC program/jig, chống nứt/vỡ mép, trình tự dán/ép và đo chiều dày/độ phẳng theo điều kiện đo đã định.
- Kính: bản vẽ kính riêng với kích thước/góc/cạnh, hướng mặt và dung sai do nhà cung cấp xác nhận; bản lắp xác định đệm, bite, edge clearance, seal compression và cơ cấu giữ/tháo. Giữ HOLD nếu hardware/glazing chưa chốt.
- Không để hai tuyến chế tạo như “5052 chấn hoặc 6063 phay” trong một file phát hành mà không có biến thể/spec tương đương được duyệt. So sánh và chốt tuyến; nếu giữ cả hai, quản lý option và bản vẽ tương ứng.

## 10. Kiểm chứng và trạng thái bằng chứng

Tách ít nhất: yêu cầu đã được anh chốt; số đo thực; dữ liệu hãng; tính toán; kết quả kiểm tra CAD; giả định; chưa xác minh. Không viết PASS nếu không có phương pháp, điều kiện, file nguồn/revision, kết quả và người/ngày thực hiện.

Kiểm tra số hóa gồm: model rebuild, assembly/BOM reconciliation, đơn vị/round-trip, feature-to-mating-feature, clearance khi lắp/tháo, tool access, stack dung sai, drawing-to-CAD và PDF visual QA. Ngưỡng clash >1 mm³ có thể lọt va chạm nhỏ nhưng quan trọng; phải bổ sung kiểm tra clearance tối thiểu và chuyển động theo chức năng.

Kiểm tra vật lý giữ ở trạng thái PLANNED/NOT TESTED cho đến khi có dữ liệu thật. Dùng các thử đã được đề xuất trong dự án làm đầu vào để rà lại phương pháp, fixture, mức tải, thời gian, số chu kỳ/mẫu và tiêu chí đạt; không gọi chúng là yêu cầu đã được chứng nhận chỉ vì xuất hiện trong SPEC.

Ưu tiên mẫu mối nối đế–ke, post–panel/insert, panel dán, góc fascia, retention trần, cụm kính và thao tác lắp/tháo. Các mức tải/torque/hiệu năng chưa có cơ sở phải được đóng bằng tính toán, dữ liệu hãng hoặc thử; không tự tạo con số để điền đủ bảng. Các kết luận về tải, kín âm và khả năng sản xuất vẫn cần prototype/measurement phù hợp.

FAI phải truy tới mã đặc tính trên drawing: Part/Rev, feature/characteristic ID, nominal, upper/lower limit, unit, datum, phương pháp/dụng cụ, kết quả từng mẫu, kết luận và evidence. File có 155 dòng nhưng cột kết quả trống là kế hoạch đo, chưa phải kết quả đạt.

## 11. Trình tự làm lại và các mốc duyệt

### Mốc 1 - Kiến trúc và danh sách vấn đề

Nộp bản tóm tắt sản phẩm, cây cụm, document/part register, bảng sai khác và đề xuất chuẩn hóa đơn vị/tên/trục tọa độ. Tra cứu và lập bảng lựa chọn phụ kiện giữ kính/hardware cùng dữ liệu giao diện theo §4.3 trước khi cập nhật các chi tiết và pattern liên quan vào bản vẽ. Chỉ hỏi anh những lựa chọn ảnh hưởng yêu cầu/kiểu dáng/chi phí hoặc nguồn dữ liệu thật sự còn thiếu; tự xử lý các việc trình bày và đối chiếu thông thường.

### Mốc 2 - Bộ mẫu trước khi nhân rộng

Làm một bộ nhỏ, có thể review trực tiếp:

1. GA đủ các hướng nhìn và mặt cắt chính.
2. Bản lắp BASE có exploded view, BOM và detail ke–rail–chân.
3. Bản part 110006 và 110002: đúng tâm lỗ, datum, pitch, dung sai, section/bend.
4. Bản cụm WALL và chi tiết 211000: stack vật liệu, cut list/quy trình dán, biến thể hardware, insert/latch và các HOLD còn lại.
5. Một detail 350011 thể hiện đủ 2 lỗ tròn + 2 slot, quan hệ với stud và khe fascia.
6. Một Joint Register mẫu cho mối nối vít và một bond specification mẫu; ghi TBD/HOLD có kiểm soát khi thiếu SKU/dữ liệu.
7. Bảng nghiên cứu/lựa chọn phụ kiện giữ kính và hardware ảnh hưởng tới bộ mẫu, có nguồn hãng/SKU/variant và kiểm tra tương thích; chỉ cập nhật geometry/pattern khi đủ dữ liệu giao diện theo §4.3. Bản mẫu thể hiện rõ 3D X/Y/Z và 2D X/Y.
8. File native của các part mẫu, có body được tạo/điều khiển bằng sketch, constraints, kích thước và feature theo §4.4; kèm mapping nguồn và minh chứng sửa parameter → rebuild → body cập nhật. Giao STEP cùng revision để đối chiếu, không dùng STEP thay native.

Nộp bản PDF đã mở kiểm tra ở khổ in dự kiến và checklist chất lượng. Chờ anh duyệt cách trình bày, logic lắp và quyết định kỹ thuật cần duyệt trước khi nhân rộng toàn bộ bộ drawing. Đây là mốc review thiết kế, không phải yêu cầu xin phép cho từng thao tác sửa file.

### Mốc 3 - Hoàn thiện đồng bộ

Áp template đã duyệt cho các cụm/part còn lại; cập nhật CAD native, drawing, STEP, DXF, BOM, joint/feature registers, FAI, sách lắp và packaging cùng revision. Dữ liệu cũ trở thành nguồn tham chiếu, không còn là bộ phát hành song song.

### Mốc 4 - Prototype và phát hành

Liệt kê rõ phần đã đủ hồ sơ, phần cần supplier confirmation và phần cần mẫu thử. Chỉ đổi trạng thái từng phạm vi sau khi đúng người duyệt và có evidence tương ứng. Không tự đặt mua, gửi xưởng hoặc phát hành sản xuất.

## 12. Cấu trúc thư mục đề xuất

    Indoor-Pod-V5-Rework/
      00-Control/             README, manifest, requirements, issues, change log
      01-CAD-Native/          assembly/part có sketch, constraints, parameters và feature tree; đủ dependencies
      02-Drawings/
        00-General-Assembly/
        10-Subassemblies/
        20-Parts/
        30-Assembly-Instructions/
      03-Manufacturing/       STEP, DXF, cut lists, process specifications
      04-BOM/                 master BOM và các view lọc có truy vết
      05-Engineering/         joints, feature rationale, calculations, supplier data
      06-Verification/        CAD reports, FAI plan/results, prototype evidence
      07-Packaging/           bản lắp kiện, BOM đóng gói, logistics appendix
      90-Archive/             chỉ tham chiếu hoặc lưu theo quy tắc được duyệt

Đây là cấu trúc đích cho bộ làm lại, không phải lệnh di chuyển/xóa bộ gốc. Chỉ tạo file có người dùng và mục đích rõ. README phải chỉ ra nên đọc file nào trước và trạng thái của từng phạm vi. Một master BOM có thể xuất nhiều view, nhưng không duy trì các bản BOM độc lập dễ lệch nhau.

## 13. Checklist nghiệm thu bộ hồ sơ agent

- [ ] Có GA nhiều view/mặt cắt và bản lắp cụm đứng trước bản part trong drawing index.
- [ ] Đơn vị metric nhất quán; chỗ giữ tên catalog/imperial đã được phân biệt rõ; CAD/DXF không bị scale nhầm.
- [ ] 3D chỉ dùng X/Y/Z; 2D/bảng lỗ chỉ dùng X/Y, có gốc/chiều dương, đơn vị và mapping view rõ; không còn u/v/c hoặc u/v/w làm tên trục.
- [ ] Phụ kiện giữ/bắt kính và hardware đã được tìm hiểu, chọn SKU/variant hoặc định nghĩa thiết kế riêng dựa trên giao diện thật trước khi cập nhật vào CAD/drawing; có nguồn và trạng thái xác minh, không có pattern phỏng đoán.
- [ ] Mã, tên, orientation, variant, revision và trạng thái khớp ở CAD/BOM/drawing/export.
- [ ] Từng body tự thiết kế có sketch/feature điều khiển thực, kích thước/constraints/parameter chỉnh sửa được và mapping theo §4.4–4.5; không chỉ imported solid hoặc sketch minh họa.
- [ ] Đã giao CAD native đủ dependencies cùng STEP xuất cùng revision; có minh chứng sửa parameter và rebuild trên bản sao, sau đó hoàn nguyên đúng giá trị thiết kế trước khi xuất.
- [ ] Hình chiếu/section rõ, font đọc được, không chồng chữ, không nhét ghi chú làm mất chỗ hình.
- [ ] Các lỗ có center mark/tag, kích thước đúng tâm, mặt vào, chiều sâu, dung sai và datum; bảng lỗ truy được từng feature.
- [ ] Slot, bend, miter, pocket và feature khác có định nghĩa chế tạo, không chỉ kích thước bao.
- [ ] Feature Rationale Register giải thích được vị trí/pitch/offset và các khe quan trọng.
- [ ] Joint Register cho biết vì sao dùng vít/keo/cách khác và chứng minh được đường truyền tải, lắp và tháo.
- [ ] Vít/insert có SKU, stack, ren ăn, lỗ đúng nền, torque có cơ sở và đường dụng cụ.
- [ ] Mối dán có substrate, SKU keo, quy trình và kế hoạch thử trên vật liệu thật; không dùng mô tả họ keo thay specification.
- [ ] Các giao diện quan trọng có tolerance stack và phương pháp kiểm tra khả thi.
- [ ] BOM–assembly–drawing đã đối chiếu theo mã; quantities/dự phòng/cụm mua sẵn không bị đếm lẫn.
- [ ] Mỗi HOLD có chủ thể, phạm vi và điều kiện gỡ; không lẫn vào file được phép gia công bằng một ghi chú khó thấy.
- [ ] PASS/VALIDATED có dữ liệu chứng minh; tính toán, kiểm tra CAD và thử vật lý được phân biệt.
- [ ] Bộ mẫu đã được anh review trước khi nhân rộng; hồ sơ cuối có danh sách thay đổi và việc còn mở.

Nếu thiếu điều kiện bắt buộc, ghi rõ hạng mục CHƯA ĐẠT và cách đóng. Không tự đánh giá “production-ready” chỉ vì đủ file hoặc mọi check script trả PASS.

## 14. Cách báo cáo lại

Báo cáo ngắn, bắt đầu bằng kết quả và link file: đã sửa gì; quyết định nào có cơ sở; điều gì còn HOLD; anh cần duyệt đúng lựa chọn nào. Sau đó mới đến tính toán và bằng chứng. Không viết các tuyên bố hoàn thành chung chung.

Agents cần:

> Đọc và tuân thủ toàn bộ guideline này. Bắt đầu ở Mốc 1 rồi làm bộ mẫu Mốc 2. Giữ nguyên bộ gốc. Chưa xuất lại hàng loạt part, chưa gỡ HOLD và chưa gửi sản xuất. Kết quả phải là file/bản vẽ có thể review, không chỉ một kế hoạch bằng chữ. Mỗi kích thước và mối nối phải có căn cứ chức năng, chế tạo, lắp ráp và kiểm tra; điều chưa xác minh phải được nói rõ. Dùng X/Y/Z trong 3D và chỉ X/Y trong 2D. Tìm hiểu, kiểm tra phụ kiện giữ kính và các hardware theo §4.3 trước khi cập nhật chúng hoặc pattern lắp vào model/bản vẽ. Mỗi body tự thiết kế phải sửa được bằng sketch có kích thước/constraints và feature trong CAD native theo §4.4–4.5; bàn giao native cùng STEP xuất cùng revision, không chỉ STEP/imported solid.

