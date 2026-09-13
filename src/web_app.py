"""Web UI độc lập cho Vinmec ReAct Agent.

Lịch sử và trace được giữ ở phía trình duyệt trong đúng phiên đang mở.
Server không lưu session, vì vậy reload trang luôn bắt đầu rỗng.
"""

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import run_react_agent
from mcp_server import MCPAcademicServer
from providers import get_llm_provider


PROVIDER = get_llm_provider()
MCP_SERVER = MCPAcademicServer()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRACE_PATH = os.path.join(BASE_DIR, "docs", "trace_waterfall.json")


def overwrite_trace_log(trace):
    """Ghi đè trace của đúng loop hiện tại; không cộng dồn các phiên cũ."""
    os.makedirs(os.path.dirname(TRACE_PATH), exist_ok=True)
    with open(TRACE_PATH, "w", encoding="utf-8") as trace_file:
        json.dump(trace, trace_file, ensure_ascii=False, indent=2)


HTML = r"""<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="Cache-Control" content="no-store">
  <title>Vinmec Care Agent</title>
  <style>
    :root { --ink:#172033; --muted:#667085; --line:#e5e9ef; --brand:#087f6e; --soft:#effaf7; --bg:#f5f7fa; }
    * { box-sizing:border-box; }
    body { margin:0; background:var(--bg); color:var(--ink); font:15px/1.55 Segoe UI,Arial,sans-serif; }
    .page { max-width:1260px; margin:auto; padding:24px 18px 38px; }
    .top { display:flex; justify-content:space-between; align-items:center; gap:16px; margin-bottom:18px; }
    .brand { display:flex; align-items:center; gap:12px; }
    .logo { width:45px; height:45px; display:grid; place-items:center; border-radius:15px; color:white; background:linear-gradient(135deg,#087f6e,#10a58e); font-size:24px; }
    h1 { margin:0; font-size:24px; letter-spacing:-.4px; }
    .subtitle { color:var(--muted); font-size:13px; }
    .status { padding:7px 12px; border-radius:99px; color:#08705f; background:#effcf9; border:1px solid #c8e9e1; font-size:12px; }
    .columns { display:grid; grid-template-columns:minmax(0,1fr) minmax(350px,.82fr); gap:18px; }
    .card { overflow:hidden; background:#fff; border:1px solid var(--line); border-radius:17px; box-shadow:0 7px 24px #1720330a; }
    .card-title { height:56px; padding:0 17px; display:flex; align-items:center; justify-content:space-between; border-bottom:1px solid var(--line); }
    .card-title h2 { margin:0; font-size:15px; }
    .card-title span { color:var(--muted); font-size:12px; }
    #chat { height:540px; overflow:auto; padding:18px; }
    .empty { height:100%; display:grid; place-content:center; padding:20px; color:var(--muted); text-align:center; }
    .empty b { display:block; margin-bottom:6px; color:var(--ink); }
    .bubble { max-width:88%; margin:0 0 13px; padding:11px 14px; border-radius:15px; white-space:pre-wrap; }
    .bubble.user { margin-left:auto; color:#fff; background:var(--brand); border-bottom-right-radius:4px; }
    .bubble.agent { background:var(--soft); border-bottom-left-radius:4px; }
    .label { display:block; margin-bottom:3px; font-size:10px; font-weight:700; letter-spacing:.08em; text-transform:uppercase; opacity:.65; }
    .composer { display:flex; gap:9px; padding:13px; border-top:1px solid var(--line); background:#fbfcfd; }
    textarea { width:100%; min-height:52px; max-height:130px; resize:vertical; padding:11px 12px; border:1px solid #d8e0e8; border-radius:11px; outline:none; font:inherit; }
    textarea:focus { border-color:#56b9a8; box-shadow:0 0 0 3px #56b9a822; }
    button { border:0; border-radius:10px; padding:0 17px; color:#fff; background:var(--brand); font-weight:700; cursor:pointer; }
    button:hover { background:#066d5d; } button:disabled { opacity:.55; cursor:wait; }
    button.secondary { padding:6px 10px; color:var(--muted); background:#fff; border:1px solid var(--line); font-size:12px; }
    .stats { display:flex; gap:7px; padding:10px 13px; border-bottom:1px solid var(--line); }
    .stat { padding:5px 8px; border-radius:8px; color:var(--muted); background:#f5f7f9; font-size:11px; }
    .stat b { color:var(--ink); }
    #trace { height:602px; overflow:auto; padding:12px; }
    .event { overflow:hidden; margin-bottom:10px; border:1px solid var(--line); border-radius:11px; }
    .event-head { display:flex; justify-content:space-between; gap:8px; padding:9px 10px; background:#fafbfc; font-size:12px; font-weight:700; }
    .kind { color:var(--brand); font-size:10px; letter-spacing:.06em; }
    pre { margin:0; padding:10px; overflow:auto; background:#fcfdff; color:#344054; font:11px/1.5 Consolas,monospace; }
    @media (max-width:850px) { .top { align-items:flex-start; flex-direction:column; } .columns { grid-template-columns:1fr; } #chat { height:440px; } #trace { height:430px; } }
  </style>
</head>
<body>
  <main class="page">
    <header class="top">
      <div class="brand"><div class="logo">✚</div><div><h1>Vinmec Care Agent</h1><div class="subtitle">Tra cứu lịch bác sĩ · Đặt lịch khám · ReAct waterfall trace</div></div></div>
      <div class="status" id="status">Phiên mới · chưa có câu hỏi</div>
    </header>
    <section class="columns">
      <article class="card">
        <div class="card-title"><h2>Cuộc trò chuyện</h2><span>Lịch sử chỉ tồn tại trong trang này</span></div>
        <div id="chat"><div class="empty"><div><b>Bắt đầu phiên tư vấn</b>Ví dụ: “Tra cứu lịch Tim mạch tại Times City ngày 20/09/2026.”</div></div></div>
        <form class="composer" id="form"><textarea id="input" required placeholder="Nhập câu hỏi của bạn..."></textarea><button id="send">Gửi</button></form>
      </article>
      <article class="card">
        <div class="card-title"><h2>Waterfall Trace</h2><button class="secondary" id="clear">Xóa phiên</button></div>
        <div class="stats"><span class="stat">Tool calls: <b id="calls">0</b></span><span class="stat">Events: <b id="events">0</b></span><span class="stat">Provider: <b id="provider">—</b></span></div>
        <div id="trace"><div class="empty"><div><b>Chưa có trace</b>Trace sẽ hiện sau khi agent xử lý.</div></div></div>
      </article>
    </section>
  </main>
  <script>
    let history = [], trace = [];
    const $ = s => document.querySelector(s), chat = $('#chat'), traceBox = $('#trace'), input = $('#input'), send = $('#send'), status = $('#status');
    const escapeHtml = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]));
    function render(provider = '—') {
      chat.innerHTML = history.length ? history.map(x => `<div class="bubble ${x.role === 'user' ? 'user' : 'agent'}"><span class="label">${x.role === 'user' ? 'Bạn' : 'Agent'}</span>${escapeHtml(x.content)}</div>`).join('') : '<div class="empty"><div><b>Bắt đầu phiên tư vấn</b>Ví dụ: “Tra cứu lịch Tim mạch tại Times City ngày 20/09/2026.”</div></div>';
      traceBox.innerHTML = trace.length ? trace.map(x => `<div class="event"><div class="event-head"><span>Step ${escapeHtml(x.step)} · ${escapeHtml(x.tool_name || 'FINAL_ANSWER')}</span><span class="kind">${escapeHtml(x.action_type)}</span></div><pre>${escapeHtml(JSON.stringify(x, null, 2))}</pre></div>`).join('') : '<div class="empty"><div><b>Chưa có trace</b>Trace sẽ hiện sau khi agent xử lý.</div></div>';
      $('#calls').textContent = trace.filter(x => x.action_type === 'TOOL_EXECUTION').length;
      $('#events').textContent = trace.length;
      $('#provider').textContent = provider;
      chat.scrollTop = chat.scrollHeight;
    }
    $('#clear').onclick = async () => { await fetch('/api/reset', {method:'POST'}); history = []; trace = []; render(); status.textContent = 'Phiên mới · chưa có câu hỏi'; input.focus(); };
    $('#form').onsubmit = async event => {
      event.preventDefault(); const message = input.value.trim(); if (!message) return;
      send.disabled = true; status.textContent = 'Agent đang xử lý...';
      try {
        const response = await fetch('/api/chat', { method:'POST', headers:{'Content-Type':'application/json; charset=utf-8'}, body:JSON.stringify({message, history}) });
        const data = await response.json(); if (!response.ok) throw Error(data.error || 'Agent gặp lỗi.');
      history.push({role:'user', content:message}, {role:'assistant', content:data.answer}); trace=data.trace; input.value=''; render(data.provider); status.textContent='Sẵn sàng';
      } catch (error) { status.textContent='Có lỗi'; alert(error.message); } finally { send.disabled=false; input.focus(); }
    };
    input.onkeydown = e => { if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) $('#form').requestSubmit(); };
    render();
  </script>
</body>
</html>"""


def json_response(handler, payload, status=200):
    raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("Content-Length", str(len(raw)))
    handler.end_headers()
    handler.wfile.write(raw)


class UIHandler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def do_GET(self):
        if urlparse(self.path).path != "/":
            json_response(self, {"error": "Not found"}, 404)
            return
        overwrite_trace_log([])
        raw = HTML.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/api/reset":
            overwrite_trace_log([])
            json_response(self, {"answer": "", "trace": [], "provider": PROVIDER.__class__.__name__})
            return
        if path != "/api/chat":
            json_response(self, {"error": "Not found"}, 404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length)
            try:
                body = json.loads(raw.decode("utf-8"))
            except UnicodeDecodeError:
                body = json.loads(raw.decode("cp1252"))
            message = str(body.get("message", "")).strip()
            history = body.get("history", [])
            if not message:
                json_response(self, {"error": "Vui lòng nhập câu hỏi."}, 400)
                return
            if not isinstance(history, list):
                history = []
            logs = run_react_agent(message, PROVIDER, MCP_SERVER, history[-20:])
            answer = next((x.get("output", "") for x in reversed(logs) if x.get("action_type") == "FINAL_ANSWER"), "Agent chưa tạo câu trả lời cuối.")
            overwrite_trace_log(logs)
            json_response(self, {"answer": answer, "trace": logs, "provider": PROVIDER.__class__.__name__})
        except (json.JSONDecodeError, UnicodeDecodeError):
            json_response(self, {"error": "Request JSON không hợp lệ."}, 400)
        except Exception as exc:
            json_response(self, {"error": f"Agent gặp lỗi: {exc}"}, 500)


class SingleInstanceHTTPServer(ThreadingHTTPServer):
    # Không cho phép nhiều phiên bản web_app cùng bind một cổng. Nếu không,
    # trình duyệt có thể nhận ngẫu nhiên response từ một tiến trình cũ.
    allow_reuse_address = False


def start_server(requested_port: int):
    """Mở cổng sạch; nếu cổng cũ còn bị chiếm thì chọn cổng kế tiếp."""
    for port in range(requested_port, requested_port + 20):
        try:
            return SingleInstanceHTTPServer(("127.0.0.1", port), UIHandler), port
        except OSError:
            continue
    raise OSError(f"Không tìm được cổng trống từ {requested_port} đến {requested_port + 19}.")


if __name__ == "__main__":
    requested_port = int(os.getenv("UI_PORT", "8501"))
    overwrite_trace_log([])
    server, port = start_server(requested_port)
    print(f"Vinmec UI: http://127.0.0.1:{port}")
    if port != requested_port:
        print(f"⚠️ Cổng {requested_port} đang được tiến trình cũ sử dụng; đã chuyển sang cổng sạch {port}.")
    print(f"Provider: {PROVIDER.__class__.__name__}")
    print("Lịch sử và trace chỉ tồn tại trong tab hiện tại; reload sẽ xóa phiên.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
