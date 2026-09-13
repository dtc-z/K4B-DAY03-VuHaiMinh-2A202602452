# 📊 BÁO CÁO THU HOẠCH NGHIỆM THU BÀI LAB 3 (BƯỚC 3 — SUBMISSION ARTIFACT)

> **Họ và Tên Học viên:**  Vũ Hải Minh
> **Mã Sinh Viên / Mã Học viên:** 2A202602452
> **Chủ đề Lựa chọn:** *Trợ lý Tư vấn Sức khỏe Vinmec:* Tra cứu lịch làm việc bác sĩ chuyên khoa và đặt lịch khám bệnh.

---

## 1. BẢNG CHẤM ĐIỂM AGENTIC FIT SCORING MATRIX (ĐÁNH GIÁ CHỦ ĐỀ)

| Tiêu chí Đánh giá | Mức độ (1 - 5) | Giải trình chi tiết lý do chọn điểm |
| :--- | :---: | :--- |
| **1. Multi-step Reasoning** | 4 / 5 | Bài toán có yêu cầu chia nhỏ nhiều bước suy luận nối tiếp nhau không? |
| **2. Tool Interaction** | 3 / 5 | Hệ thống có cần kết nối với MCP Server / Cơ sở dữ liệu bên ngoài không? |
| **3. Dynamic Decision** | 4 / 5 | Bước tiếp theo có phụ thuộc vào kết quả quan sát bước trước không? |
| **4. Long Horizon Goal** | 5 / 5 | Hệ thống có phải giữ mục tiêu xuyên suốt qua nhiều lượt xử lý không? |
| **TỔNG ĐIỂM AGENTIC FIT** | **16 / 20** | *Nếu tổng điểm > 12/20: Bài toán rất phù hợp triển khai Agentic System.* |

---

## 2. TRÍCH XUẤT KẾT QUẢ WATERFALL TRACE LOG (SAU KHI CHẠY TEST SUITE)

> ⚠️ **YÊU CẦU CHẠY:** `python src/app.py --all` được phép chạy bằng Mock Offline Provider và không cần API key. Chỉ chế độ `python src/app.py --interactive` mới yêu cầu provider/API key thật trong `.env`.

Dán 1 đoạn trích xuất log tiêu biểu từ file `docs/trace_waterfall.json` sinh ra sau khi chạy test suite:

```json
[
  {
    "step": 1,
    "query": "Tôi muốn khám bác sĩ Nội tiết tại Vinmec Times City vào chiều 22/09/2026. Hãy tìm bác sĩ còn lịch phù hợp rồi đặt lịch khám cho bệnh nhân Trần Hoàng Nam, số điện thoại 0901234567.",
    "action_type": "TOOL_EXECUTION",
    "tool_name": "academic_query",
    "arguments": {
      "specialty": "Nội tiết",
      "facility": "Vinmec Times City",
      "date": "22/09/2026"
    },
    "observation": {
      "status": "SUCCESS",
      "specialty": "Nội tiết",
      "facility": "Vinmec Times City",
      "date": "22/09/2026",
      "data": [
        {
          "doctor_name": "BS.CKII Trần Hoàng Nam",
          "specialty": "Nội tiết",
          "facility": "Vinmec Times City",
          "date": "22/09/2026",
          "available_slots": [
            "13:30",
            "15:00",
            "16:30"
          ]
        }
      ]
    },
    "latency_ms": 545.5
  },
  {
    "step": 2,
    "query": "Tôi muốn khám bác sĩ Nội tiết tại Vinmec Times City vào chiều 22/09/2026. Hãy tìm bác sĩ còn lịch phù hợp rồi đặt lịch khám cho bệnh nhân Trần Hoàng Nam, số điện thoại 0901234567.",
    "action_type": "TOOL_EXECUTION",
    "tool_name": "schedule_appointment",
    "arguments": {
      "patient_name": "Trần Hoàng Nam",
      "phone_number": "0901234567",
      "specialty": "Nội tiết",
      "facility": "Vinmec Times City",
      "datetime_str": "15:00 22/09/2026"
    },
    "observation": {
      "status": "SUCCESS",
      "booking_id": "VM-4567-99",
      "patient_name": "Trần Hoàng Nam",
      "phone_number": "0901234567",
      "specialty": "Nội tiết",
      "facility": "Vinmec Times City",
      "datetime": "15:00 22/09/2026",
      "doctor_name": "Bác sĩ phù hợp theo lịch Vinmec",
      "message": "Đặt lịch khám thành công cho bệnh nhân Trần Hoàng Nam tại Vinmec Times City vào lúc 15:00 22/09/2026."
    },
    "latency_ms": 1035.96
  }
]
```

---

## 3. TỔNG KẾT KẾT QUẢ NGHIỆM THU & NỘP BÀI

- [x] Đã chạy thành công chế độ interactive trên LLM API thật bằng provider đã cấu hình trong `.env`.
- **Tổng số Test Cases đã chạy thành công:** 5 / 5 test cases.
- **Số lượt gọi Tool qua MCP Server chính xác:** 5 lượt.
- **Kết quả đẩy Repo nộp bài:** [X] Đã Commit và Push mã nguồn thành công lên GitHub cá nhân.

---

> ✅ **HOÀN TẤT NỘP BÀI:** Sao chép đường link GitHub Repository cá nhân của bạn và dán vào ô nộp bài trên hệ thống LMS VLearn để hoàn tất Bài Lab 3!
