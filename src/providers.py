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
        intent_text = prompt_lower.split("câu hỏi mới của người dùng:", 1)[-1]
        date_match = re.search(r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b", prompt_lower)
        requested_date = (
            f"{int(date_match.group(1)):02d}/{int(date_match.group(2)):02d}/{date_match.group(3)}"
            if date_match else "20/09/2026"
        )
        is_search_request = any(term in intent_text for term in (
            "tra cứu", "lịch làm việc", "tìm bác sĩ", "chọn bác sĩ", "chọn một bác sĩ", "kiểm tra"
        ))
        if (
            not is_search_request
            and not any(term in intent_text for term in ("đặt lịch", "book lịch", "đăng ký khám"))
            and date_match
            and any(term in intent_text for term in ("muốn khám", "khám", "lịch"))
        ):
            is_search_request = True
        has_patient_details = (
            bool(re.search(r"\b0\d{8,10}\b", prompt_lower))
            or any(name in prompt_lower for name in ("nguyễn minh anh", "trần hoàng nam"))
        )
        is_appointment_request = any(term in intent_text for term in (
            "đặt lịch", "book lịch", "đăng ký khám"
        ))

        if is_search_request and "kết quả tra cứu từ tool" not in prompt_lower:
            specialty = (
                "Nhi" if "nhi" in prompt_lower
                else (
                    "Tim mạch" if "tim mạch" in prompt_lower
                    else ("Răng hàm mặt" if "răng" in prompt_lower else "Nội tiết")
                )
            )
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

        if is_appointment_request and not has_patient_details:
            return {
                "type": "text",
                "content": "Để đặt lịch khám, vui lòng cung cấp họ tên và số điện thoại của bệnh nhân.",
                "thought": "Chưa đủ thông tin bệnh nhân để gọi schedule_appointment."
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
                    "patient_name": "Trần Hoàng Nam" if "nội tiết" in prompt_lower else "Nguyễn Minh Anh",
                    "phone_number": "0901234567",
                    "specialty": (
                        "Nội tiết" if "nội tiết" in prompt_lower
                        else ("Răng hàm mặt" if "răng" in prompt_lower else "Da liễu")
                    ),
                    "facility": "Vinmec Times City" if "times city" in prompt_lower else "Vinmec Central Park",
                    "datetime_str": (
                        "15:00 22/09/2026" if "nội tiết" in prompt_lower
                        else (f"09:00 {requested_date}" if "răng" in prompt_lower else f"09:00 {requested_date}")
                    ),
                    "doctor_name": (
                        "BS.CKII Trần Hoàng Nam" if "nội tiết" in prompt_lower
                        else ("BS.CKII Phạm Minh Đức" if "răng" in prompt_lower else "TS.BS Lê Thu Hà")
                    )
                },
                "thought": "Người dùng yêu cầu đặt lịch khám tại Vinmec. Tôi sẽ gọi tool schedule_appointment."
            }
        elif "tra cứu" in prompt_lower or "lịch làm việc" in prompt_lower or "kiểm tra" in prompt_lower:
            date = requested_date
            specialty = (
                "Nhi" if "nhi" in prompt_lower
                else (
                    "Tim mạch" if "tim mạch" in prompt_lower
                    else ("Răng hàm mặt" if "răng" in prompt_lower else "Nội tiết")
                )
            )
            return {
                "type": "tool_call",
                "tool_name": "academic_query",
                "arguments": {
                    "specialty": specialty,
                    "facility": "Vinmec Đà Nẵng" if "đà nẵng" in prompt_lower else "Vinmec Times City",
                    "date": date
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
