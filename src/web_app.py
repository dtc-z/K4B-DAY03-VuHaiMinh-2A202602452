"""UI demo cho Vinmec ReAct Agent, không cần thêm dependency."""

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import run_react_agent
from mcp_server import MCPAcademicServer
from providers import get_llm_provider


conversation_history = []
trace_history = []
provider = get_llm_provider()
mcp_server = MCPAcademicServer()


PAGE = r"""<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Vinmec ReAct Agent</title>
  <style>
    :root { --ink:#172033; --muted:#6b7280; --line:#e8eaf0; --brand:#0b806e; --soft:#eef9f6; --bg:#f6f8fb; }
    * { box-sizing:border-box; }
    body { margin:0; color:var(--ink); background:var(--bg); font:15px/1.55 Inter,Segoe UI,Arial,sans-serif; }
    .shell { max-width:1240px; margin:0 auto; padding:28px 20px 40px; }
    header { display:flex; align-items:center; justify-content:space-between; gap:20px; margin-bottom:22px; }
    .brand { display:flex; align-items:center; gap:13px; }
    .logo { display:grid; place-items:center; width:46px; height:46px; border-radius:15px; color:white; background:linear-gradient(135deg,#0b806e,#1aa58d); font-size:24px; box-shadow:0 9px 22px #0b806e33; }
    h1 { margin:0; font-size:25px; letter-spacing:-.5px; }
    .subtitle { color:var(--muted); margin-top:2px; }
    .status { padding:8px 12px; border:1px solid #cdebe4; border-radius:999px; background:#f2fcfa; color:#086b5c; font-size:13px; white-space:nowrap; }
    .grid { display:grid; grid-template-columns:minmax(0,1.05fr) minmax(360px,.95fr); gap:20px; }
    .card { background:white; border:1px solid var(--line); border-radius:18px; box-shadow:0 10px 28px #1720330b; overflow:hidden; }
    .card-head { display:flex; justify-content:space-between; align-items:center; padding:17px 19px; border-bottom:1px solid var(--line); }
    .card-head h2 { margin:0; font-size:16px; }
    .hint { color:var(--muted); font-size:12px; }
    #conversation { min-height:510px; max-height:610px; overflow:auto; padding:18px; }
    .empty { display:grid; place-items:center; min-height:450px; text-align:center; color:var(--muted); }
    .bubble { max-width:88%; padding:11px 14px; border-radius:15px; margin:0 0 13px; white-space:pre-wrap; }
    .user { margin-left:auto; color:white; background:var(--brand); border-bottom-right-radius:4px; }
    .assistant { background:var(--soft); border-bottom-left-radius:4px; }
    .role { display:block; margin-bottom:3px; font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:.08em; opacity:.68; }
    .composer { display:flex; gap:10px; padding:14px; border-top:1px solid var(--line); background:#fcfdfd; }
    textarea { flex:1; min-height:52px; max-height:130px; resize:vertical; padding:12px 13px; border:1px solid #dfe4eb; border-radius:12px; font:inherit; outline:none; }
    textarea:focus { border-color:#5bb9aa; box-shadow:0 0 0 3px #5bb9aa22; }
    button { border:0; border-radius:11px; padding:0 17px; color:white; background:var(--brand); font-weight:700; cursor:pointer; }
    button:hover { background:#096e60; } button:disabled { opacity:.55; cursor:wait; }
    .trace { max-height:678px; overflow:auto; padding:14px; }
    .event { border:1px solid var(--line); border-radius:13px; margin-bottom:11px; overflow:hidden; }
    .event-title { display:flex; justify-content:space-between; gap:12px; padding:10px 12px; background:#fafbfc; font-weight:700; }
    .badge { color:#087664; font-size:11px; letter-spacing:.05em; }
    pre { margin:0; padding:12px; overflow:auto; color:#334155; background:#fbfcfe; font:12px/1.5 Consolas,monospace; }
    .clear { color:var(--muted); background:white; border:1px solid var(--line); padding:6px 10px; font-size:12px; }
    @media (max-width:850px) { .grid { grid-template-columns:1fr; } header { align-items:flex-start; flex-direction:column; } .status { align-self:flex-start; } }
  </style>
</head>
<body>
  <main class="shell">
    <header>
      <div class="brand"><div class="logo">✚</div><div><h1>Vinmec ReAct Agent</h1><div class="subtitle">Tra cứu lịch bác sĩ · Đặt lịch khám · Theo dõi waterfall trace</div></div></div>
      <div class="status" id="status">Sẵn sàng</div>
    </header>
    <section class="grid">
      <div class="card">
        <div class="card-head"><h2>Cuộc trò chuyện</h2><span class="hint">Agent nhớ 10 lượt gần nhất</span></div>
        <div id="conversation"><div class="empty">Hãy hỏi về lịch bác sĩ hoặc yêu cầu đặt lịch khám.<br/>Ví dụ: “Tôi muốn khám Răng hàm mặt tại Times City ngày 17/09/2026.”</div></div>
        <form class="composer" id="form"><textarea id="message" placeholder="Nhập câu hỏi của bạn..." required></textarea><button id="send">Gửi</button></form>
      </div>
      <div class="card">
        <div class="card-head"><h2>Waterfall Trace</h2><button class="clear" id="clear">Xóa phiên</button></div>
        <div class="trace" id="trace"><div class="empty" style="min-height:220px">Trace sẽ xuất hiện sau lượt gọi đầu tiên.</div></div>
      </div>
    </section>
  </main>
  <script>
    const $ = (s) => document.querySelector(s);
    const conversation = $('#conversation'), trace = $('#trace'), status = $('#status');
    function esc(value) { return String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c])); }
    function render(state) {
      conversation.innerHTML = state.history.length ? state.history.map(x => `<div class="bubble ${x.role === 'user' ? 'user' : 'assistant'}"><span class="role">${x.role === 'user' ? 'Bạn' : 'Agent'}</span>${esc(x.content)}</div>`).join('') : '<div class="empty">Hãy hỏi về lịch bác sĩ hoặc yêu cầu đặt lịch khám.<br/>Ví dụ: “Tôi muốn khám Răng hàm mặt tại Times City ngày 17/09/2026.”</div>';
      trace.innerHTML = state.trace.length ? state.trace.map((x, i) => `<div class="event"><div class="event-title"><span>Step ${esc(x.step)} · ${esc(x.tool_name || 'FINAL_ANSWER')}</span><span class="badge">${esc(x.action_type)}</span></div><pre>${esc(JSON.stringify(x, null, 2))}</pre></div>`).join('') : '<div class="empty" style="min-height:220px">Trace sẽ xuất hiện sau lượt gọi đầu tiên.</div>';
      conversation.scrollTop = conversation.scrollHeight;
    }
    async function refresh() { const r = await fetch('/api/state'); render(await r.json()); }
    $('#form').addEventListener('submit', async (e) => {
      e.preventDefault(); const input = $('#message'), send = $('#send'); const message = input.value.trim(); if (!message) return;
      send.disabled = true; status.textContent = 'Agent đang xử lý...'; input.value = '';
      try { const r = await fetch('/api/chat', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({message})}); const data = await r.json(); if (!r.ok) throw new Error(data.error || 'Request failed'); render(data); status.textContent = 'Sẵn sàng'; }
      catch (err) { status.textContent = 'Có lỗi'; alert(err.message); }
      finally { send.disabled = false; input.focus(); }
    });
    $('#clear').addEventListener('click', async () => { await fetch('/api/reset', {method:'POST'}); await refresh(); status.textContent = 'Đã xóa phiên'; });
    refresh();
  </script>
</body>
</html>"""


def state_payload():
    return {
        "history": conversation_history,
        "trace": trace_history
    }


class UIHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def send_json(self, payload, status=200):
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/":
            data = PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        elif self.path == "/api/state":
            self.send_json(state_payload())
        else:
            self.send_json({"error": "Not found"}, 404)

    def do_POST(self):
        global conversation_history, trace_history
        length = int(self.headers.get("Content-Length", "0"))
        body = json.loads(self.rfile.read(length) or b"{}")

        if self.path == "/api/reset":
            conversation_history = []
            trace_history = []
            self.send_json(state_payload())
            return

        if self.path != "/api/chat":
            self.send_json({"error": "Not found"}, 404)
            return

        message = str(body.get("message", "")).strip()
        if not message:
            self.send_json({"error": "Vui lòng nhập câu hỏi."}, 400)
            return

        logs = run_react_agent(message, provider, mcp_server, conversation_history)
        answer = next(
            (item.get("output", "") for item in reversed(logs) if item.get("action_type") == "FINAL_ANSWER"),
            "Agent chưa tạo câu trả lời cuối."
        )
        conversation_history.extend([
            {"role": "user", "content": message},
            {"role": "assistant", "content": answer}
        ])
        trace_history.extend(logs)
        self.send_json(state_payload())


if __name__ == "__main__":
    port = int(os.getenv("UI_PORT", "8501"))
    server = ThreadingHTTPServer(("127.0.0.1", port), UIHandler)
    print(f"Vinmec UI: http://127.0.0.1:{port}")
    print("Nhấn Ctrl+C để dừng.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
