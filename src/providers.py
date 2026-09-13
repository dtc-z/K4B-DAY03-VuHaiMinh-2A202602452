"""
🔌 MULTI-PROVIDER LLM ADAPTER (Google Gemini, OpenAI & Offline Mock)
Hỗ trợ Native Tool Calling và chuyển đổi linh hoạt qua biến môi trường LLM_PROVIDER.
"""

import os
import re
import sys
import json
from typing import Dict, Any, List
from dotenv import load_dotenv

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

load_dotenv()

class BaseLLMProvider:
    """Interface cơ sở cho các LLM Provider hỗ trợ Native Tool Calling"""
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        raise NotImplementedError

    def generate_with_tools(self, prompt: str, tools_schema: List[Dict[str, Any]], system_prompt: str = "") -> Dict[str, Any]:
        raise NotImplementedError


class MockOfflineProvider(BaseLLMProvider):
    """Offline Mock Provider dùng để chạy thử mà không tốn API Key"""
    def __init__(self):
        self.model_name = "Offline-Mock-Model-2026"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        return f"[Mock Chatbot Response]: Tôi đã nhận được câu hỏi '{prompt}'. (Chế độ Chatbot không có Tool tra cứu lịch bác sĩ hoặc đặt lịch khám)."

    def generate_with_tools(self, prompt: str, tools_schema: List[Dict[str, Any]], system_prompt: str = "") -> Dict[str, Any]:
        prompt_lower = prompt.lower()
        history_marker = "câu hỏi mới của người dùng:"
        has_conversation_history = history_marker in prompt_lower
        history_text, intent_text = (
            prompt_lower.split(history_marker, 1)
            if has_conversation_history
            else ("", prompt_lower)
        )
        explicit_booking = any(term in intent_text for term in (
            "đặt lịch", "book lịch", "đăng ký khám", "đặt hẹn"
        ))
        date_match = re.search(r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b", prompt_lower)
        requested_date = (
            f"{int(date_match.group(1)):02d}/{int(date_match.group(2)):02d}/{date_match.group(3)}"
            if date_match else "20/09/2026"
        )
        current_date_match = re.search(
            r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b",
            intent_text
        )
        if current_date_match:
            requested_date = (
                f"{int(current_date_match.group(1)):02d}/"
                f"{int(current_date_match.group(2)):02d}/"
                f"{current_date_match.group(3)}"
            )
        has_explicit_date = bool(current_date_match)

        def contains_word(word: str) -> bool:
            return re.search(rf"\b{re.escape(word)}\b", intent_text) is not None

        time_match = re.search(r"\b([01]?\d|2[0-3]):[0-5]\d\b", intent_text)
        if time_match:
            requested_time = time_match.group(0)
        else:
            hour_match = re.search(r"\b(\d{1,2})\s*giờ\s*(sáng|chiều|tối)?", intent_text)
            if hour_match:
                hour = int(hour_match.group(1))
                period = hour_match.group(2)
                if period in ("chiều", "tối") and hour < 12:
                    hour += 12
                requested_time = f"{hour:02d}:00"
            else:
                requested_time = ""
        phone_match = re.search(r"\b0\d{8,10}\b", intent_text)
        name_match = re.search(r"\btên(?: tôi)?\s*(?:là)?\s*([^,;.\n]+)", intent_text)
        patient_name = name_match.group(1).strip() if name_match else ""
        if not patient_name:
            patient_name = next(
                (name for name in ("Nguyễn Minh Anh", "Trần Hoàng Nam") if name.casefold() in prompt_lower),
                ""
            )
        has_patient_details = bool(phone_match or patient_name)

        # Một lượt trả lời tiếp theo thường chỉ chứa tên, số điện thoại và giờ.
        # Không bắt buộc người dùng phải lặp lại cụm "đặt lịch" ở lượt này:
        # nếu lịch sử đã có kết quả lịch/chọn bác sĩ thì tiếp tục đúng luồng booking.
        history_booking_context = any(term in history_text for term in (
            "đặt lịch", "book lịch", "đăng ký khám", "đặt hẹn",
            "lịch bác sĩ", "lịch làm việc", "chọn bác sĩ", "chọn một bác sĩ"
        ))
        pending_booking = explicit_booking or (
            has_conversation_history
            and history_booking_context
            and (has_patient_details or bool(requested_time))
        )
        field_text = prompt_lower if pending_booking else intent_text
        specialty = (
            "Tim mạch" if "tim mạch" in field_text
            else (
                "Răng hàm mặt" if "răng" in field_text
                else (
                    "Da liễu" if "da liễu" in field_text
                    else (
                        "Nội tiết" if "nội tiết" in field_text
                        else ("Nhi" if re.search(r"\bnhi(?: khoa)?\b", field_text) else "")
                    )
                )
            )
        )
        facility = (
            "Vinmec Đà Nẵng" if "đà nẵng" in field_text
            else (
                "Vinmec Central Park" if "central park" in field_text
                else ("Vinmec Times City" if "times city" in field_text else "")
            )
        )
        is_search_request = any(term in intent_text for term in (
            "tra cứu", "lịch làm việc", "tìm bác sĩ", "chọn bác sĩ", "chọn một bác sĩ", "kiểm tra"
        ))
        if (
            not is_search_request
            and not pending_booking
            and not any(term in intent_text for term in ("đặt lịch", "book lịch", "đăng ký khám"))
            and (current_date_match or "ngày mai" not in intent_text)
            and any(term in intent_text for term in ("muốn khám", "khám", "lịch"))
        ):
            is_search_request = True
        is_appointment_request = any(term in intent_text for term in (
            "đặt lịch", "book lịch", "đăng ký khám"
        )) or (pending_booking and has_patient_details and bool(requested_time))

        if any(term in intent_text for term in (
            "có thể khám gì", "khám gì", "chuyên khoa nào", "những chuyên khoa"
        )) and not is_appointment_request:
            return {
                "type": "text",
                "content": (
                    "Vinmec có thể hỗ trợ khám Tim mạch, Nhi khoa, Da liễu, "
                    "Răng hàm mặt, Nội tiết, Sản phụ khoa, Cơ xương khớp, "
                    "Nhãn khoa, Tai mũi họng, Tiêu hóa và Hô hấp."
                ),
                "thought": "Người dùng hỏi thông tin tổng quan, không cần gọi Tool."
            }

        if (
            any(term in intent_text for term in ("lịch", "bác sĩ", "khám"))
            and not specialty
            and not is_appointment_request
        ):
            return {
                "type": "text",
                "content": "Bạn vui lòng cho biết chuyên khoa, cơ sở Vinmec và ngày muốn tra cứu.",
                "thought": "Thiếu chuyên khoa, cơ sở hoặc ngày nên cần hỏi lại người dùng."
            }

        if is_search_request and "kết quả tra cứu từ tool" not in prompt_lower:
            if not specialty or not facility or not has_explicit_date:
                return {
                    "type": "text",
                    "content": "Bạn vui lòng cho biết chuyên khoa, cơ sở Vinmec và ngày muốn tra cứu.",
                    "thought": "Thiếu tham số tra cứu lịch bác sĩ nên cần hỏi lại người dùng."
                }
            return {
                "type": "tool_call",
                "tool_name": "academic_query",
                "arguments": {
                    "specialty": specialty,
                    "facility": facility,
                    "date": requested_date
                },
                "thought": "Người dùng muốn tra cứu lịch bác sĩ Vinmec. Tôi sẽ gọi tool academic_query."
            }

        if is_appointment_request and not has_patient_details:
            return {
                "type": "text",
                "content": "Để đặt lịch khám, vui lòng cung cấp họ tên và số điện thoại của bệnh nhân.",
                "thought": "Chưa đủ thông tin bệnh nhân để gọi schedule_appointment."
            }

        if is_appointment_request and (not specialty or not facility or not requested_time):
            return {
                "type": "text",
                "content": "Để đặt lịch, vui lòng cung cấp chuyên khoa, cơ sở Vinmec và giờ khám cụ thể.",
                "thought": "Chưa đủ thông tin lịch khám để gọi schedule_appointment."
            }

        # Mô phỏng nhận diện intent gọi Tool cho chủ đề Vinmec.
        # Với yêu cầu nhiều bước, tra cứu lịch trước; app.py sẽ gửi observation
        # vào vòng lặp tiếp theo để Mock thực hiện bước đặt lịch.
        if "tìm bác sĩ" in prompt_lower and "kết quả tra cứu từ tool" not in prompt_lower:
            return {
                "type": "tool_call",
                "tool_name": "academic_query",
                "arguments": {
                    "specialty": "Nội tiết",
                    "facility": "Vinmec Times City",
                    "date": "22/09/2026"
                },
                "thought": "Trước khi đặt lịch, tôi sẽ tra cứu bác sĩ Nội tiết còn lịch tại Vinmec Times City."
            }
        elif is_appointment_request:
            return {
                "type": "tool_call",
                "tool_name": "schedule_appointment",
                "arguments": {
                    "patient_name": patient_name or ("Trần Hoàng Nam" if "nội tiết" in field_text else "Nguyễn Minh Anh"),
                    "phone_number": phone_match.group(0) if phone_match else "0901234567",
                    "specialty": specialty,
                    "facility": facility,
                    "datetime_str": f"{requested_time} {requested_date}",
                    "doctor_name": (
                        "BS.CKII Trần Hoàng Nam" if "nội tiết" in prompt_lower
                        else ("BS.CKII Phạm Minh Đức" if "răng" in prompt_lower else "TS.BS Lê Thu Hà")
                    )
                },
                "thought": "Người dùng yêu cầu đặt lịch khám tại Vinmec. Tôi sẽ gọi tool schedule_appointment."
            }
        elif "tra cứu" in prompt_lower or "lịch làm việc" in prompt_lower or "kiểm tra" in prompt_lower:
            return {
                "type": "tool_call",
                "tool_name": "academic_query",
                "arguments": {
                    "specialty": specialty,
                    "facility": "Vinmec Đà Nẵng" if "đà nẵng" in prompt_lower else "Vinmec Times City",
                    "date": requested_date
                },
                "thought": "Người dùng muốn tra cứu lịch bác sĩ Vinmec. Tôi sẽ gọi tool academic_query."
            }
        else:
            return {
                "type": "text",
                "content": "[Mock Agent Response]: Vinmec cung cấp dịch vụ khám tại nhiều chuyên khoa. Với lịch bác sĩ hoặc đặt lịch khám cụ thể, vui lòng cung cấp cơ sở, chuyên khoa và thời gian mong muốn.",
                "thought": "Câu hỏi chung về dịch vụ Vinmec, trả lời trực tiếp không cần gọi Tool."
            }


class GeminiProvider(BaseLLMProvider):
    """Google Gemini Provider (Native Tool Calling với Google GenAI SDK)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "gemini-2.5-flash"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            return "[Gemini Error]: Chưa cấu hình GEMINI_API_KEY trong file .env! Đang sử dụng chế độ Mock."
        try:
            from google import genai
            client = genai.Client(api_key=self.api_key)
            contents = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = client.models.generate_content(model=self.model_name, contents=contents)
            return response.text
        except Exception as e:
            return f"[Gemini Exception]: {str(e)}"

    def generate_with_tools(self, prompt: str, tools_schema: List[Dict[str, Any]], system_prompt: str = "") -> Dict[str, Any]:
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            print("ℹ️ [Gemini Provider]: Chưa tìm thấy GEMINI_API_KEY hợp lệ. Tự động chuyển sang Mock Offline.")
            return MockOfflineProvider().generate_with_tools(prompt, tools_schema, system_prompt)
        
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)
            
            # Chuẩn hóa function declarations cho Gemini SDK
            function_declarations = []
            for tool in tools_schema:
                # Bỏ qua các tool schema chưa được định nghĩa hoàn chỉnh
                if not tool.get("name") or not tool.get("parameters"):
                    continue
                function_declarations.append({
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": tool.get("parameters", {})
                })

            config = types.GenerateContentConfig(
                system_instruction=system_prompt if system_prompt else None,
                tools=[{"function_declarations": function_declarations}] if function_declarations else None,
                temperature=0.2
            )

            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )

            # Kiểm tra xem Gemini có trả về Tool Call không
            if response.function_calls:
                call = response.function_calls[0]
                args = dict(call.args) if hasattr(call, 'args') and call.args else {}
                return {
                    "type": "tool_call",
                    "tool_name": call.name,
                    "arguments": args,
                    "thought": f"Gemini quyết định gọi công cụ '{call.name}' với tham số: {json.dumps(args, ensure_ascii=False)}"
                }
            else:
                return {
                    "type": "text",
                    "content": response.text or "",
                    "thought": "Gemini phản hồi trực tiếp bằng văn bản (không cần gọi công cụ)."
                }

        except Exception as e:
            print(f"⚠️ [Gemini API Warning]: Không thể kết nối live API ({str(e)}). Tự động fallback về Mock.")
            return MockOfflineProvider().generate_with_tools(prompt, tools_schema, system_prompt)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI Provider (Native Tool Calling với OpenAI SDK)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "gpt-4o-mini"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_openai_api_key_here":
            return "[OpenAI Error]: Chưa cấu hình OPENAI_API_KEY trong file .env! Đang sử dụng chế độ Mock."
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            response = client.chat.completions.create(model=self.model_name, messages=messages)
            return response.choices[0].message.content or ""
        except Exception as e:
            return f"[OpenAI Exception]: {str(e)}"

    def generate_with_tools(self, prompt: str, tools_schema: List[Dict[str, Any]], system_prompt: str = "") -> Dict[str, Any]:
        if not self.api_key or self.api_key == "your_openai_api_key_here":
            print("ℹ️ [OpenAI Provider]: Chưa tìm thấy OPENAI_API_KEY hợp lệ. Tự động chuyển sang Mock Offline.")
            return MockOfflineProvider().generate_with_tools(prompt, tools_schema, system_prompt)

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)

            tools = []
            for tool in tools_schema:
                if not tool.get("name"):
                    continue
                tools.append({
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": tool.get("description", ""),
                        "parameters": tool.get("parameters", {})
                    }
                })

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=tools if tools else None,
                tool_choice="auto" if tools else None
            )

            msg = response.choices[0].message
            if msg.tool_calls:
                call = msg.tool_calls[0]
                args = json.loads(call.function.arguments) if call.function.arguments else {}
                return {
                    "type": "tool_call",
                    "tool_name": call.function.name,
                    "arguments": args,
                    "thought": f"OpenAI quyết định gọi công cụ '{call.function.name}' với tham số: {json.dumps(args, ensure_ascii=False)}"
                }
            else:
                return {
                    "type": "text",
                    "content": msg.content or "",
                    "thought": "OpenAI phản hồi trực tiếp bằng văn bản (không cần gọi công cụ)."
                }
        except Exception as e:
            print(f"⚠️ [OpenAI API Warning]: Không thể kết nối live API ({str(e)}). Tự động fallback về Mock.")
            return MockOfflineProvider().generate_with_tools(prompt, tools_schema, system_prompt)


def get_llm_provider() -> BaseLLMProvider:
    """Factory function khởi tạo Provider theo LLM_PROVIDER env variable"""
    provider_type = os.getenv("LLM_PROVIDER", "gemini").lower()
    
    if provider_type == "gemini":
        key = os.getenv("GEMINI_API_KEY")
        if key and key != "your_gemini_api_key_here":
            return GeminiProvider()
        else:
            return MockOfflineProvider()
    elif provider_type == "openai":
        key = os.getenv("OPENAI_API_KEY")
        if key and key != "your_openai_api_key_here":
            return OpenAIProvider()
        else:
            return MockOfflineProvider()
    elif provider_type == "mock":
        return MockOfflineProvider()
    else:
        return MockOfflineProvider()
