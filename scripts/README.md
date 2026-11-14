# Gemini qua Trạm Mây

Client local phục vụ công cụ/agent trong workspace, dùng Python 3 và `curl`, không
cần cài SDK. Cấu hình theo hướng dẫn người dùng cung cấp ngày 14/11/2026.
URL gateway được giữ riêng trong `.env`, không đặt mặc định trong client hoặc tài liệu chia sẻ.

## Thiết lập

Tạo `.env` từ [mẫu](../.env.example), điền platform key riêng vào `GEMINI_API_KEY`
và HTTPS URL gateway riêng vào `GEMINI_BASE_URL`.
Không dùng dashboard key của 9Router. `.env` được ignore; không ghi key vào Git,
prompt, log hay tài liệu. Biến `gemini_api_key` cũ vẫn được hỗ trợ.
Các biến OS ưu tiên hơn `.env`; file được tìm theo gốc workspace, không theo cwd.

Chạy từ gốc workspace:

```bash
python3 scripts/dung_gemini_api.py --list-models
python3 scripts/dung_gemini_api.py --prompt 'Chỉ trả lời OK'
```

Lệnh prompt dùng quota. Model mặc định `ag/gemini-3.8-flash-low` là ID của gateway;
kiểm tra `/models` trước khi đổi model. `--model` chỉ đổi model, effort vẫn lấy
từ cấu hình. Client không tự retry hoặc theo redirect; key truyền qua stdin của
curl, không nằm trong argv; cấu hình curl cá nhân không được nạp.

## Dùng từ Python hoặc agent khác

```python
from scripts.dung_gemini_api import GeminiProxyClient, load_settings

settings = load_settings()
settings.update(GEMINI_MODEL="ag/gemini-3.8-flash-low", GEMINI_REASONING_EFFORT="low")
client = GeminiProxyClient(settings, timeout=180)
response = client.chat([{"role": "user", "content": "Chỉ trả lời OK"}], max_tokens=128)
text = response["choices"][0]["message"]["content"]
```

`chat` nhận content text hoặc danh sách text/image_url (data URL PNG) theo định dạng
OpenAI-compatible. Chỉ gửi ảnh/nội dung thuộc phạm vi người dùng giao; giữ model
yêu cầu và `response['model']` khi ghi provenance. OCR thô chưa phải bản hiệu đính.

401: kiểm tra platform key; 403: kiểm tra quyền/WAF; 429: dừng gửi thêm, kiểm tra quota
và thời điểm retry. DNS, timeout và 5xx không chứng minh key sai. Không tự retry
inference vì có thể đã dùng quota. Không in raw lỗi gateway có thể chứa dữ liệu request.

Các script batch/checkpoint và corpus OCR nhắc trong tài liệu đính kèm thuộc project
khác, chưa được chuyển vào workspace này. Client này cung cấp kết nối và payload
chat/ảnh; không tự chạy batch 8 luồng hoặc gửi dữ liệu HireUS.

Kiểm thử offline: `python3 -m unittest discover -s scripts/tests -v`.
