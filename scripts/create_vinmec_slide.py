from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
from xml.sax.saxutils import escape

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs"
PNG_PATH = OUT / "vinmec_react_agent_slide.png"
PPTX_PATH = OUT / "vinmec_react_agent_slide.pptx"

W, H = 1920, 1080
BG = (7, 20, 33)
PANEL = (14, 37, 52)
PANEL_ALT = (17, 46, 62)
LINE = (46, 78, 94)
WHITE = (243, 248, 251)
MUTED = (163, 184, 198)
TEAL = (37, 211, 174)
MINT = (151, 241, 218)
BLUE = (104, 178, 255)
ORANGE = (255, 197, 111)
CORAL = (255, 125, 116)


def font(size, bold=False):
    name = "segoeuib.ttf" if bold else "segoeui.ttf"
    return ImageFont.truetype(rf"C:\Windows\Fonts\{name}", size)


def text_width(draw, value, f):
    return draw.textbbox((0, 0), value, font=f)[2]


def wrap(draw, value, f, max_width):
    lines = []
    for paragraph in value.split("\n"):
        words = paragraph.split()
        current = ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if current and text_width(draw, candidate, f) > max_width:
                lines.append(current)
                current = word
            else:
                current = candidate
        if current:
            lines.append(current)
    return lines


def draw_text(draw, xy, value, f, fill=WHITE, max_width=None, spacing=5, anchor=None):
    x, y = xy
    if max_width:
        value = "\n".join(wrap(draw, value, f, max_width))
    draw.multiline_text((x, y), value, font=f, fill=fill, spacing=spacing, anchor=anchor)


def rounded(draw, box, radius=18, fill=PANEL, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def pill(draw, x, y, label, fill, text_fill=BG, pad_x=13, h=29, f=None):
    f = f or font(14, True)
    w = text_width(draw, label, f) + pad_x * 2
    rounded(draw, (x, y, x + w, y + h), h // 2, fill)
    draw_text(draw, (x + pad_x, y + 5), label, f, text_fill)
    return w


def arrow(draw, start, end, color=TEAL, width=4, head=12):
    draw.line((*start, *end), fill=color, width=width)
    import math
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    left = (end[0] - head * math.cos(angle - 0.55), end[1] - head * math.sin(angle - 0.55))
    right = (end[0] - head * math.cos(angle + 0.55), end[1] - head * math.sin(angle + 0.55))
    draw.polygon([end, left, right], fill=color)


def node(draw, box, title, subtitle, accent):
    rounded(draw, box, 16, PANEL_ALT, LINE, 2)
    x1, y1, x2, y2 = box
    draw.rounded_rectangle((x1, y1, x1 + 7, y2), radius=4, fill=accent)
    draw_text(draw, (x1 + 18, y1 + 17), title, font(17, True), WHITE, x2 - x1 - 30)
    draw_text(draw, (x1 + 18, y1 + 48), subtitle, font(12), MUTED, x2 - x1 - 28, spacing=3)


def build_png():
    OUT.mkdir(parents=True, exist_ok=True)
    im = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(im)

    # Subtle technical grid and glow accents.
    for x in range(0, W, 80):
        draw.line((x, 0, x, H), fill=(10, 30, 45), width=1)
    for y in range(0, H, 80):
        draw.line((0, y, W, y), fill=(10, 30, 45), width=1)
    draw.ellipse((1540, -230, 2020, 250), fill=(12, 55, 68))
    draw.ellipse((-180, 820, 260, 1260), fill=(10, 49, 59))

    # Header.
    draw.rounded_rectangle((60, 48, 112, 100), radius=16, fill=TEAL)
    draw.rectangle((81, 58, 91, 90), fill=BG)
    draw.rectangle((71, 68, 101, 80), fill=BG)
    draw_text(draw, (136, 48), "VINMEC CARE AGENT", font(29, True), WHITE)
    draw_text(draw, (138, 88), "ReAct + MCP cho tra cứu lịch bác sĩ & đặt lịch khám", font(17), MUTED)
    pill(draw, 1505, 51, "DAY 03  •  2A202602452", PANEL_ALT, MINT, 16, 34, font(13, True))
    draw_text(draw, (60, 130), "TỪ CÂU HỎI TỰ NHIÊN ĐẾN QUYẾT ĐỊNH CÓ BẰNG CHỨNG", font(13, True), TEAL)

    # Column geometry.
    lx, lw = 60, 425
    cx, cw = 515, 875
    rx, rw = 1420, 440

    # 01 Topic card.
    rounded(draw, (lx, 160, lx + lw, 490), 22, PANEL, LINE, 2)
    draw_text(draw, (lx + 25, 185), "01  /  ĐỀ TÀI", font(13, True), TEAL)
    draw_text(draw, (lx + 25, 222), "Trợ lý Tư vấn\nSức khỏe Vinmec", font(29, True), WHITE, lw - 50, spacing=2)
    draw.line((lx + 25, 314, lx + lw - 25, 314), fill=LINE, width=2)
    draw_text(draw, (lx + 25, 334), "Vì sao chọn?", font(15, True), ORANGE)
    reasons = [
        "Lịch bác sĩ là dữ liệu động, không nên bịa từ kiến thức tĩnh.",
        "Một mục tiêu thực tế: tra cứu → chọn slot → đặt lịch.",
        "Kết quả cần chính xác, có thể kiểm chứng qua Tool và trace.",
    ]
    y = 366
    for reason in reasons:
        draw.ellipse((lx + 27, y + 4, lx + 38, y + 15), fill=TEAL)
        draw_text(draw, (lx + 51, y), reason, font(14), MUTED, lw - 83, spacing=3)
        y += 39 if len(wrap(draw, reason, font(14), lw - 83)) == 1 else 55

    # 02 Agent Fit card.
    rounded(draw, (lx, 515, lx + lw, 960), 22, PANEL, LINE, 2)
    draw_text(draw, (lx + 25, 540), "02  /  AGENT FIT", font(13, True), TEAL)
    draw_text(draw, (lx + 25, 575), "16 / 20", font(33, True), WHITE)
    draw_text(draw, (lx + 160, 588), "ReAct phù hợp", font(15, True), MINT)
    draw_text(draw, (lx + 25, 628), "Bốn tiêu chí trong trace_eval.md", font(13), MUTED)
    fit = [
        ("Multi-step reasoning", "Tra cứu rồi mới đặt lịch", "4", BLUE),
        ("Tool interaction", "MCP + dữ liệu lịch Vinmec", "3", TEAL),
        ("Dynamic decision", "Slot sau phụ thuộc Observation", "4", ORANGE),
        ("Long-horizon goal", "Giữ mục tiêu qua nhiều lượt chat", "5", CORAL),
    ]
    y = 672
    for name, why, score, color in fit:
        draw.ellipse((lx + 25, y + 2, lx + 61, y + 38), fill=color)
        draw_text(draw, (lx + 25, y + 8), score, font(16, True), BG, anchor="ma")
        draw_text(draw, (lx + 77, y), name, font(14, True), WHITE)
        draw_text(draw, (lx + 77, y + 23), why, font(12), MUTED, lw - 120)
        y += 67

    # 03 Architecture card.
    rounded(draw, (cx, 160, cx + cw, 960), 22, PANEL, LINE, 2)
    draw_text(draw, (cx + 28, 185), "03  /  KIẾN TRÚC AGENT ĐÃ XÂY", font(13, True), TEAL)
    draw_text(draw, (cx + 28, 218), "ReAct loop: suy luận có hành động, quan sát có bằng chứng", font(20, True), WHITE)
    draw_text(draw, (cx + 28, 258), "Thought  →  Action  →  Observation  →  Final Answer", font(14, True), MINT)

    # Main architecture nodes.
    node(draw, (cx + 30, 325, cx + 165, 410), "User / UI", "web_app.py", BLUE)
    node(draw, (cx + 205, 315, cx + 410, 420), "ReAct Agent Core", "app.py  •  LLM", TEAL)
    node(draw, (cx + 465, 325, cx + 635, 410), "MCP Server", "JSON-RPC 2.0", ORANGE)
    node(draw, (cx + 690, 325, cx + 835, 410), "Vinmec DB", "mock schedule", CORAL)
    arrow(draw, (cx + 165, 367), (cx + 202, 367), BLUE)
    arrow(draw, (cx + 410, 367), (cx + 462, 367), TEAL)
    arrow(draw, (cx + 635, 367), (cx + 687, 367), ORANGE)
    pill(draw, cx + 235, 280, "THOUGHT", TEAL, BG, 13, 28, font(12, True))
    pill(draw, cx + 470, 280, "ACTION / TOOL CALL", ORANGE, BG, 13, 28, font(12, True))
    pill(draw, cx + 685, 280, "OBSERVATION", CORAL, BG, 13, 28, font(12, True))

    # Tool registry branch.
    draw_text(draw, (cx + 32, 468), "MCP tool registry", font(14, True), MUTED)
    rounded(draw, (cx + 30, 500, cx + 405, 585), 16, (20, 55, 70), (37, 109, 112), 2)
    pill(draw, cx + 50, 518, "academic_query", BLUE, BG, 12, 27, font(13, True))
    draw_text(draw, (cx + 50, 552), "Tra cứu chuyên khoa · cơ sở · ngày · bác sĩ", font(13), WHITE, 330)
    rounded(draw, (cx + 435, 500, cx + 810, 585), 16, (20, 55, 70), (37, 109, 112), 2)
    pill(draw, cx + 455, 518, "schedule_appointment", TEAL, BG, 12, 27, font(13, True))
    draw_text(draw, (cx + 455, 552), "Đặt lịch: bệnh nhân · điện thoại · slot", font(13), WHITE, 330)
    arrow(draw, (cx + 550, 410), (cx + 345, 496), ORANGE, 3)
    arrow(draw, (cx + 550, 410), (cx + 620, 496), ORANGE, 3)
    arrow(draw, (cx + 810, 542), (cx + 840, 542), TEAL, 3)
    draw_text(draw, (cx + 842, 525), "result", font(12, True), MUTED)

    # Loop-back observation.
    draw.arc((cx + 90, 625, cx + 760, 800), 195, 345, fill=CORAL, width=4)
    arrow(draw, (cx + 100, 730), (cx + 200, 682), CORAL, 3)
    draw_text(draw, (cx + 260, 650), "Observation được nạp lại", font(15, True), CORAL)
    draw_text(draw, (cx + 260, 680), "Nếu còn mục tiêu đặt lịch → tiếp tục vòng lặp;\nnếu đủ dữ liệu → trả Final Answer.", font(13), MUTED, 435, spacing=4)

    # Implementation evidence chips.
    draw_text(draw, (cx + 30, 845), "ĐIỂM NỐI TRONG REPO", font(12, True), MUTED)
    chips = [("tools.py", BLUE), ("mcp_server.py", ORANGE), ("providers.py", TEAL), ("trace_waterfall.json", CORAL)]
    x = cx + 30
    for label, color in chips:
        w = pill(draw, x, 875, label, (23, 54, 70), color, 12, 30, font(12, True))
        x += w + 10

    # 04 Tools card.
    rounded(draw, (rx, 160, rx + rw, 685), 22, PANEL, LINE, 2)
    draw_text(draw, (rx + 25, 185), "04  /  TOOLS", font(13, True), TEAL)
    draw_text(draw, (rx + 25, 220), "Hai công cụ, hai vai trò rõ ràng", font(20, True), WHITE)

    rounded(draw, (rx + 25, 275, rx + rw - 25, 445), 17, PANEL_ALT, (44, 97, 117), 2)
    pill(draw, rx + 45, 296, "academic_query", BLUE, BG, 12, 29, font(13, True))
    draw_text(draw, (rx + 45, 341), "TRA CỨU LỊCH BÁC SĨ", font(12, True), BLUE)
    draw_text(draw, (rx + 45, 368), "Tìm lịch theo chuyên khoa, cơ sở, ngày\nvà bác sĩ phù hợp.", font(14), WHITE, rw - 90, spacing=4)
    draw_text(draw, (rx + 45, 417), "→ Observation: danh sách slot còn trống", font(12, True), MUTED)

    rounded(draw, (rx + 25, 465, rx + rw - 25, 635), 17, PANEL_ALT, (44, 97, 117), 2)
    pill(draw, rx + 45, 486, "schedule_appointment", TEAL, BG, 12, 29, font(13, True))
    draw_text(draw, (rx + 45, 531), "ĐẶT LỊCH KHÁM", font(12, True), TEAL)
    draw_text(draw, (rx + 45, 558), "Ghi nhận bệnh nhân, số điện thoại,\nchuyên khoa, cơ sở và datetime.", font(14), WHITE, rw - 90, spacing=4)
    draw_text(draw, (rx + 45, 607), "→ Result: booking_id + xác nhận lịch", font(12, True), MUTED)
    draw_text(draw, (rx + 25, 655), "MCP server dispatch → tool router → mock database", font(12), MUTED)

    # Outcome card.
    rounded(draw, (rx, 710, rx + rw, 960), 22, (18, 49, 63), (36, 95, 102), 2)
    draw_text(draw, (rx + 25, 735), "KẾT QUẢ DEMO", font(13, True), TEAL)
    metrics = [("5/5", "test cases", BLUE), ("2", "native tools", TEAL), ("1", "waterfall trace", ORANGE)]
    x = rx + 25
    for value, label, color in metrics:
        draw.ellipse((x, 778, x + 69, 847), fill=color)
        draw_text(draw, (x + 34, 789), value, font(17, True), BG, anchor="ma")
        draw_text(draw, (x + 82, 788), label, font(13, True), WHITE)
        x += 135
    draw.line((rx + 25, 872, rx + rw - 25, 872), fill=(41, 84, 94), width=1)
    draw_text(draw, (rx + 25, 892), "Chat UI + Interactive CLI", font(14, True), MINT)
    draw_text(draw, (rx + 25, 920), "Kết quả trả lời dựa trên Observation,\nkhông bịa lịch khám.", font(13), MUTED, rw - 50, spacing=4)

    # Footer.
    draw.line((60, 1000, W - 60, 1000), fill=LINE, width=2)
    draw_text(draw, (60, 1017), "VINMEC  /  REACT AGENT  /  MCP-ENHANCED", font(12, True), MUTED)
    draw_text(draw, (W - 60, 1017), "Thought → Action → Observation → Final Answer", font(12, True), TEAL, anchor="ra")
    im.save(PNG_PATH, "PNG", optimize=True)


def xml_part(text):
    return text.encode("utf-8")


def build_pptx():
    # A one-slide PowerPoint containing the designed 16:9 artwork as a crisp image.
    cx, cy = 12192000, 6858000
    content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Default Extension="png" ContentType="image/png"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  <Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>
  <Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>
  <Override PartName="/ppt/slides/slide1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>
  <Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>
  <Override PartName="/ppt/presProps.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presProps+xml"/>
  <Override PartName="/ppt/viewProps.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.viewProps+xml"/>
  <Override PartName="/ppt/tableStyles.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.tableStyles+xml"/>
</Types>'''
    root_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
</Relationships>'''
    presentation = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst>
  <p:sldIdLst><p:sldId id="256" r:id="rId2"/></p:sldIdLst>
  <p:sldSz cx="{cx}" cy="{cy}" type="screen16x9"/>
  <p:notesSz cx="6858000" cy="9144000"/>
  <p:defaultTextStyle><a:defPPr/><a:lvl1pPr marL="0" algn="l"><a:defRPr lang="vi-VN"/></a:lvl1pPr></p:defaultTextStyle>
</p:presentation>'''
    presentation_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide1.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme1.xml"/>
</Relationships>'''
    slide = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld name="Vinmec Care Agent"><p:spTree>
    <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
    <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
    <p:pic>
      <p:nvPicPr><p:cNvPr id="2" name="vinmec_react_agent_slide.png"/><p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr>
      <p:blipFill><a:blip r:embed="rId1"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>
      <p:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><avLst/></a:prstGeom></p:spPr>
    </p:pic>
  </p:spTree></p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>'''
    slide_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/vinmec_react_agent_slide.png"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
</Relationships>'''
    empty_layout = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="blank" preserve="1">
  <p:cSld name="Blank"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/></p:spTree></p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sldLayout>'''
    layout_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>
</Relationships>'''
    master = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld name="Master"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/></p:spTree></p:cSld>
  <p:sldLayoutIdLst><p:sldLayoutId id="1" r:id="rId2"/></p:sldLayoutIdLst>
  <p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles>
  <p:clrMap accent1="accent1" accent2="accent2" bg1="lt1" bg2="lt2" folHlink="folHlink" hlink="hlink" tx1="dk1" tx2="dk2"/></p:sldMaster>'''
    master_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
</Relationships>'''
    theme = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Vinmec Theme"><a:themeElements><a:clrScheme name="Vinmec"><a:dk1><a:sysClr val="windowText" lastClr="000000"/></a:dk1><a:lt1><a:sysClr val="window" lastClr="FFFFFF"/></a:lt1><a:dk2><a:srgbClr val="172033"/></a:dk2><a:lt2><a:srgbClr val="F5F7FA"/></a:lt2><a:accent1><a:srgbClr val="25D3AE"/></a:accent1><a:accent2><a:srgbClr val="68B2FF"/></a:accent2><a:accent3><a:srgbClr val="FFC56F"/></a:accent3><a:accent4><a:srgbClr val="FF7D74"/></a:accent4><a:accent5><a:srgbClr val="97F1DA"/></a:accent5><a:accent6><a:srgbClr val="A3B8C6"/></a:accent6><a:hlink><a:srgbClr val="0563C1"/></a:hlink><a:folHlink><a:srgbClr val="954F72"/></a:folHlink></a:clrScheme><a:fontScheme name="Vinmec Fonts"><a:majorFont><a:latin typeface="Segoe UI"/><a:ea typeface=""/><a:cs typeface=""/></a:majorFont><a:minorFont><a:latin typeface="Segoe UI"/><a:ea typeface=""/><a:cs typeface=""/></a:minorFont></a:fontScheme><a:fmtScheme name="Vinmec Format"><a:fillStyleLst/><a:lnStyleLst/><a:effectStyleLst/><a:bgFillStyleLst/></a:fmtScheme></a:themeElements></a:theme>'''
    pres_props = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><p:presentationPr xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"/>'''
    view_props = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><p:viewPr xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" lastView="sldView"><p:normalViewPr/></p:viewPr>'''
    table_styles = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><a:tblStyleLst xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"/></a:tblStyleLst>'''

    with ZipFile(PPTX_PATH, "w", ZIP_DEFLATED) as z:
        parts = {
            "[Content_Types].xml": content_types,
            "_rels/.rels": root_rels,
            "ppt/presentation.xml": presentation,
            "ppt/_rels/presentation.xml.rels": presentation_rels,
            "ppt/slides/slide1.xml": slide,
            "ppt/slides/_rels/slide1.xml.rels": slide_rels,
            "ppt/slideLayouts/slideLayout1.xml": empty_layout,
            "ppt/slideLayouts/_rels/slideLayout1.xml.rels": layout_rels,
            "ppt/slideMasters/slideMaster1.xml": master,
            "ppt/slideMasters/_rels/slideMaster1.xml.rels": master_rels,
            "ppt/theme/theme1.xml": theme,
            "ppt/presProps.xml": pres_props,
            "ppt/viewProps.xml": view_props,
            "ppt/tableStyles.xml": table_styles,
        }
        for name, content in parts.items():
            z.writestr(name, xml_part(content))
        z.write(PNG_PATH, "ppt/media/vinmec_react_agent_slide.png")


if __name__ == "__main__":
    build_png()
    build_pptx()
    print(f"Created {PNG_PATH}")
    print(f"Created {PPTX_PATH}")
