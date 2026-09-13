"""
🛠️ TOOL DEFINITIONS & EXECUTION BACKEND
Mã nguồn chứa danh sách Tool Schemas (JSON Schema) và Execution Layer phục vụ cho MCP Server.
"""

import json
from datetime import datetime
from typing import Dict, Any

# ==============================================================================
# 1. KHAI BÁO TOOL SCHEMAS CHUẨN NATIVE JSON SCHEMA (TASK 1.2)
# ==============================================================================

TOOLS_SCHEMA = [
    {
        "name": "academic_query",
        "description": "Tra cứu lịch làm việc của bác sĩ chuyên khoa tại cơ sở Vinmec.",
        "parameters": {
            "type": "object",
            "properties": {
                "specialty": {
                    "type": "string",
                    "description": "Tên chuyên khoa cần tra cứu, ví dụ: 'Tim mạch'"
                },
                "facility": {
                    "type": "string",
                    "description": "Tên cơ sở Vinmec, ví dụ: 'Vinmec Times City'"
                },
                "date": {
                    "type": "string",
                    "description": "Ngày cần tra cứu theo định dạng DD/MM/YYYY"
                },
                "doctor_name": {
                    "type": "string",
                    "description": "Tên bác sĩ cần tra cứu (không bắt buộc)"
                }
            },
            "required": ["specialty", "facility", "date"]
        }
    },
    {
        "name": "schedule_appointment",
        "description": "Đặt lịch khám bệnh tại cơ sở Vinmec.",
        "parameters": {
            "type": "object",
            "properties": {
                "patient_name": {
                    "type": "string",
                    "description": "Họ và tên bệnh nhân"
                },
                "phone_number": {
                    "type": "string",
                    "description": "Số điện thoại liên hệ của bệnh nhân"
                },
                "specialty": {
                    "type": "string",
                    "description": "Chuyên khoa khám"
                },
                "facility": {
                    "type": "string",
                    "description": "Cơ sở Vinmec cần đặt lịch"
                },
                "datetime_str": {
                    "type": "string",
                    "description": "Thời gian khám, ví dụ: '09:00 20/09/2026'"
                },
                "doctor_name": {
                    "type": "string",
                    "description": "Tên bác sĩ muốn đăng ký (không bắt buộc)"
                }
            },
            "required": [
                "patient_name",
                "phone_number",
                "specialty",
                "facility",
                "datetime_str"
            ]
        }
    }
]

# ==============================================================================
# 2. MÔ PHỎNG DỮ LIỆU & HÀM THỰC THI TOOL (EXECUTION LAYER)
# ==============================================================================

MOCK_DATABASE = [
    {
        "doctor_name": "BS.CKII Nguyễn Minh Tuấn",
        "specialty": "Tim mạch",
        "facility": "Vinmec Times City",
        "date": "20/09/2026",
        "available_slots": ["08:00", "09:30", "14:00"]
    },
    {
        "doctor_name": "TS.BS Lê Thu Hà",
        "specialty": "Da liễu",
        "facility": "Vinmec Central Park",
        "date": "20/09/2026",
        "available_slots": ["09:00", "10:30", "15:00"]
    },
    {
        "doctor_name": "TS.BS Lê Thu Hà",
        "specialty": "Da liễu",
        "facility": "Vinmec Times City",
        "date": "20/09/2026",
        "available_slots": ["14:00", "16:00"]
    },
    {
        "doctor_name": "BS.CKII Trần Hoàng Nam",
        "specialty": "Nội tiết",
        "facility": "Vinmec Times City",
        "date": "22/09/2026",
        "available_slots": ["13:30", "15:00", "16:30"]
    },
    {
        "doctor_name": "BS.CKII Phạm Minh Đức",
        "specialty": "Răng hàm mặt",
        "facility": "Vinmec Times City",
        "date": "17/09/2026",
        "available_slots": ["09:00", "10:30", "15:00"]
    },
    {
        "doctor_name": "BS.CKII Phạm Minh Đức",
        "specialty": "Răng hàm mặt",
        "facility": "Vinmec Times City",
        "date": "18/09/2026",
        "available_slots": ["08:30", "11:00"]
    },
    {
        "doctor_name": "TS.BS Nguyễn Thu Trang",
        "specialty": "Nhi khoa",
        "facility": "Vinmec Times City",
        "date": "19/09/2026",
        "available_slots": ["08:00", "10:00", "14:30"]
    },
    {
        "doctor_name": "BS.CKII Lê Hoàng Phúc",
        "specialty": "Nhi khoa",
        "facility": "Vinmec Đà Nẵng",
        "date": "21/09/2026",
        "available_slots": ["09:00", "11:30", "16:00"]
    },
    {
        "doctor_name": "PGS.TS Vũ Minh Châu",
        "specialty": "Sản phụ khoa",
        "facility": "Vinmec Times City",
        "date": "21/09/2026",
        "available_slots": ["08:30", "10:00", "14:00"]
    },
    {
        "doctor_name": "BS.CKII Hoàng Thị Mai",
        "specialty": "Sản phụ khoa",
        "facility": "Vinmec Central Park",
        "date": "23/09/2026",
        "available_slots": ["09:00", "13:30", "15:30"]
    },
    {
        "doctor_name": "TS.BS Trần Quốc Huy",
        "specialty": "Cơ xương khớp",
        "facility": "Vinmec Times City",
        "date": "24/09/2026",
        "available_slots": ["08:00", "10:30", "15:00"]
    },
    {
        "doctor_name": "BS.CKII Nguyễn Hải Yến",
        "specialty": "Nhãn khoa",
        "facility": "Vinmec Central Park",
        "date": "24/09/2026",
        "available_slots": ["08:30", "11:00", "14:30"]
    },
    {
        "doctor_name": "PGS.TS Phạm Đức Long",
        "specialty": "Tai mũi họng",
        "facility": "Vinmec Đà Nẵng",
        "date": "25/09/2026",
        "available_slots": ["09:00", "10:30", "15:30"]
    },
    {
        "doctor_name": "BS.CKII Đặng Minh Khang",
        "specialty": "Ung bướu",
        "facility": "Vinmec Times City",
        "date": "25/09/2026",
        "available_slots": ["08:00", "13:30"]
    },
    {
        "doctor_name": "TS.BS Nguyễn Hoài Nam",
        "specialty": "Tiêu hóa",
        "facility": "Vinmec Central Park",
        "date": "26/09/2026",
        "available_slots": ["08:30", "10:00", "14:00"]
    },
    {
        "doctor_name": "BS.CKII Phan Ngọc Anh",
        "specialty": "Hô hấp",
        "facility": "Vinmec Times City",
        "date": "26/09/2026",
        "available_slots": ["09:00", "11:00", "16:00"]
    }
]


def normalize_text(value: str) -> str:
    """Chuẩn hóa chuỗi để so khớp không phân biệt hoa thường và khoảng trắng."""
    return " ".join(str(value).strip().casefold().split())


def text_matches(query: str, value: str) -> bool:
    """Cho phép người dùng viết tên rút gọn của chuyên khoa hoặc cơ sở."""
    normalized_query = normalize_text(query)
    normalized_value = normalize_text(value)
    return normalized_query == normalized_value or normalized_query in normalized_value


def parse_date(date_str: str) -> datetime:
    """Parse ngày theo định dạng DD/MM/YYYY."""
    return datetime.strptime(date_str.strip(), "%d/%m/%Y")


def execute_academic_query(
    specialty: str,
    facility: str,
    date: str,
    doctor_name: str = ""
) -> str:
    """Tra cứu lịch làm việc bác sĩ theo chuyên khoa, cơ sở và ngày."""
    try:
        parse_date(date)
    except ValueError:
        return json.dumps({
            "status": "INVALID_DATE",
            "message": f"Ngày '{date}' không hợp lệ. Vui lòng cung cấp ngày theo định dạng DD/MM/YYYY."
        }, ensure_ascii=False)

    matches = [
        item for item in MOCK_DATABASE
        if text_matches(specialty, item["specialty"])
        and text_matches(facility, item["facility"])
        and item["date"] == date.strip()
        and (
            not doctor_name.strip()
            or normalize_text(doctor_name) in normalize_text(item["doctor_name"])
        )
    ]

    if matches:
        return json.dumps({
            "status": "SUCCESS",
            "specialty": specialty,
            "facility": facility,
            "date": date,
            "data": matches
        }, ensure_ascii=False)

    alternatives = [
        item for item in MOCK_DATABASE
        if text_matches(specialty, item["specialty"])
        and text_matches(facility, item["facility"])
    ]
    if alternatives:
        return json.dumps({
            "status": "ALTERNATIVE_AVAILABLE",
            "message": (
                f"Không có lịch {specialty} tại {facility} vào ngày {date}, "
                "nhưng có lịch ở ngày khác."
            ),
            "data": alternatives
        }, ensure_ascii=False)

    return json.dumps({
        "status": "NOT_FOUND",
        "message": (
            f"Không tìm thấy lịch {specialty} tại {facility} vào ngày {date}. "
            "Vui lòng thử ngày hoặc cơ sở khác."
        )
    }, ensure_ascii=False)


def execute_schedule_appointment(
    patient_name: str,
    phone_number: str,
    specialty: str,
    facility: str,
    datetime_str: str,
    doctor_name: str = ""
) -> str:
    """Thực thi đặt lịch khám bệnh tại Vinmec."""
    try:
        time_part, date_part = datetime_str.strip().split(maxsplit=1)
        appointment_date = parse_date(date_part).strftime("%d/%m/%Y")
    except (ValueError, TypeError):
        return json.dumps({
            "status": "INVALID_DATETIME",
            "message": (
                f"Thời gian '{datetime_str}' không hợp lệ. "
                "Vui lòng dùng định dạng HH:MM DD/MM/YYYY."
            )
        }, ensure_ascii=False)

    matching_schedules = [
        item for item in MOCK_DATABASE
        if text_matches(specialty, item["specialty"])
        and text_matches(facility, item["facility"])
        and item["date"] == appointment_date
        and (
            not doctor_name.strip()
            or normalize_text(doctor_name) in normalize_text(item["doctor_name"])
        )
    ]
    available = [
        item for item in matching_schedules
        if time_part in item["available_slots"]
    ]
    if not available:
        return json.dumps({
            "status": "SLOT_UNAVAILABLE",
            "message": (
                f"Không có khung giờ {time_part} phù hợp cho {specialty} "
                f"tại {facility} vào ngày {appointment_date}."
            ),
            "available_slots": sorted({
                slot for item in matching_schedules
                for slot in item["available_slots"]
            })
        }, ensure_ascii=False)

    selected_doctor = available[0]["doctor_name"]
    booking_id = f"VM-{phone_number[-4:]}-99"
    return json.dumps({
        "status": "SUCCESS",
        "booking_id": booking_id,
        "patient_name": patient_name,
        "phone_number": phone_number,
        "specialty": specialty,
        "facility": facility,
        "datetime": datetime_str,
        "doctor_name": selected_doctor,
        "message": f"Đặt lịch khám thành công cho bệnh nhân {patient_name} tại {facility} vào lúc {datetime_str}."
    }, ensure_ascii=False)


# Router gọi tool thực tế
TOOL_ROUTER = {
    "academic_query": execute_academic_query,
    "schedule_appointment": execute_schedule_appointment
}


def dispatch_tool_call(tool_name: str, arguments: Dict[str, Any]) -> str:
    """Điều tuyến yêu cầu tool tới đúng hàm thực thi."""
    try:
        if tool_name in TOOL_ROUTER:
            return TOOL_ROUTER[tool_name](**arguments)
        return json.dumps({
            "status": "UNKNOWN_TOOL",
            "error": f"Tool '{tool_name}' không tồn tại!"
        }, ensure_ascii=False)
    except Exception as exc:
        return json.dumps({
            "status": "EXECUTION_ERROR",
            "error": str(exc)
        }, ensure_ascii=False)
