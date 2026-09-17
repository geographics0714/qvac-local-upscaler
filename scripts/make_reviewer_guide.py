"""Generates REVIEWER_GUIDE.pdf — a step-by-step guide for hackathon
moderators to inspect and run the QVAC Local Upscaler themselves."""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    ListFlowable, ListItem, HRFlowable, KeepTogether,
)
from reportlab.lib.enums import TA_LEFT

REPO_URL = "https://github.com/geographics0714/qvac-local-upscaler"
X_URL = "https://x.com/Geo344861554566/status/2100462023566139791"

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    "TitleCustom", parent=styles["Title"], fontSize=22, spaceAfter=4,
)
subtitle_style = ParagraphStyle(
    "Subtitle", parent=styles["Normal"], fontSize=11, textColor=colors.HexColor("#555555"),
    spaceAfter=18,
)
h1 = ParagraphStyle(
    "H1Custom", parent=styles["Heading1"], fontSize=15, spaceBefore=18, spaceAfter=8,
    textColor=colors.HexColor("#111111"),
)
h2 = ParagraphStyle(
    "H2Custom", parent=styles["Heading2"], fontSize=12, spaceBefore=10, spaceAfter=6,
    textColor=colors.HexColor("#222222"),
)
body = ParagraphStyle(
    "BodyCustom", parent=styles["Normal"], fontSize=10, leading=15, spaceAfter=6,
)
code = ParagraphStyle(
    "Code", parent=styles["Normal"], fontName="Courier", fontSize=9.5, leading=13,
    backColor=colors.HexColor("#f4f4f4"), borderPadding=8, leftIndent=4,
    spaceBefore=4, spaceAfter=10,
)
note = ParagraphStyle(
    "Note", parent=styles["Normal"], fontSize=9.5, leading=13,
    textColor=colors.HexColor("#555555"), leftIndent=10, spaceAfter=8,
)

story = []

# --- Title ---
story.append(Paragraph("QVAC Local Upscaler", title_style))
story.append(Paragraph("Reviewer guide — how to verify this submission, step by step", subtitle_style))

story.append(Paragraph(f"<b>Repo:</b> {REPO_URL}", body))
story.append(Paragraph(f"<b>X post:</b> {X_URL}", body))
story.append(Paragraph(
    "<b>What it does:</b> runs Tether's QVAC SDK <font face=\"Courier\">upscale()</font> "
    "(RealESRGAN x4plus-anime-6B) to super-resolve a photo entirely on the reviewer's own "
    "machine &mdash; no cloud call, no API key.", body,
))
story.append(HRFlowable(width="100%", color=colors.HexColor("#dddddd"), spaceAfter=12))

# --- Part 1: static inspection ---
story.append(Paragraph("Part 1 — Inspect the repo (no install needed)", h1))
story.append(Paragraph(
    "These checks can be done directly on GitHub, in under two minutes, and map "
    "one-to-one to the moderator checklist.", body,
))

cell_style = ParagraphStyle(
    "Cell", parent=styles["Normal"], fontSize=8, leading=10.5,
)
header_style = ParagraphStyle(
    "CellHeader", parent=styles["Normal"], fontSize=8, leading=10.5,
    textColor=colors.white, fontName="Helvetica-Bold",
)

def P(text, style=cell_style):
    return Paragraph(text, style)

check_rows_raw = [
    ["#", "Check", "Where to look", "What you'll see"],
    ["1", "Public, open-source license",
     "Repo homepage", "\"Public\" badge + \"MIT license\" badge under the About section"],
    ["2", "@qvac/sdk declared ≥ 0.19.0",
     "package.json, line 23", '"@qvac/sdk": "^0.19.0"'],
    ["3", "Calls loadModel + a real AI function",
     "src/upscale.js, lines 10–15 (import) and 139, 157",
     "Imports loadModel/upscale from \"@qvac/sdk\"; calls loadModel(...) then upscale({...})"],
    ["4", "No cloud AI service",
     "src/upscale.js, full file",
     "Only imports are node:fs, node:path, node:url, node:child_process, and @qvac/sdk — no openai/anthropic/gemini/replicate anywhere"],
    ["5", "Not a fork/copy of qvac-examples",
     "Commit history + file layout",
     "Single custom CLI file, original comparison-page generator, no shared file names with tetherto/qvac-examples"],
    ["6", "≥ 3 commits authored by submitter",
     "Commits page", "8 commits, all authored by GeorgeC0714"],
    ["7", "X post links repo + tags @qvac",
     "X post URL above", "Post text: \"Built a local AI upscaler with @qvac ... \" + repo link"],
    ["8", "SDK calls actually exist",
     "Compare against @qvac/sdk v0.19.x API docs",
     "loadModel, upscale, unloadModel, REALESRGAN_X4PLUS_ANIME_6B all appear in the official API Summary"],
]
check_rows = [
    [P(cell, header_style if r == 0 else cell_style) for cell in row]
    for r, row in enumerate(check_rows_raw)
]
tbl = Table(check_rows, colWidths=[0.3*inch, 1.5*inch, 1.7*inch, 2.6*inch], repeatRows=1)
tbl.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111111")),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7f7f7")]),
    ("TOPPADDING", (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ("LEFTPADDING", (0, 0), (-1, -1), 5),
    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
]))
story.append(tbl)
story.append(Spacer(1, 14))

# --- Part 2: actually run it ---
story.append(Paragraph("Part 2 — Run it yourself (optional, ~5 minutes)", h1))
story.append(Paragraph(
    "This confirms the code doesn't just read correctly &mdash; it actually performs "
    "on-device inference.", body,
))

story.append(Paragraph("Requirements", h2))
story.append(ListFlowable([
    ListItem(Paragraph("Node.js &ge; 22.17", body)),
    ListItem(Paragraph("Windows with Vulkan &ge; 1.4 (or macOS/Linux with Metal/Vulkan &mdash; see the repo's System requirements link)", body)),
    ListItem(Paragraph("~2 GB free disk space (model weights download on first run only, ~18 MB for this model)", body)),
], bulletType="bullet", leftIndent=14))

story.append(Paragraph("Step 1 — Clone the repo", h2))
story.append(Paragraph(f"git clone {REPO_URL}.git<br/>cd qvac-local-upscaler", code))

story.append(Paragraph("Step 2 — Install dependencies", h2))
story.append(Paragraph("npm install", code))
story.append(Paragraph(
    "Watch the output: it pulls <font face=\"Courier\">@qvac/sdk</font> from the public npm "
    "registry, nothing else unusual.", note,
))

story.append(Paragraph("Step 3 — Run the smoke test (bundled sample image, no photo needed)", h2))
story.append(Paragraph("node src/upscale.js samples/test-gradient.png", code))
story.append(Paragraph("Expected terminal output, in order:", body))
story.append(ListFlowable([
    ListItem(Paragraph("<font face=\"Courier\">▸ Loading RealESRGAN model on-device (first run downloads the weights)...</font>", body)),
    ListItem(Paragraph("A download progress bar the first time only (e.g. <font face=\"Courier\">▸ Downloading 100% (17.9/17.9 MB)</font>) &mdash; skipped on later runs once cached locally", body)),
    ListItem(Paragraph("<font face=\"Courier\">▸ Model loaded. Running on-device upscale...</font>", body)),
    ListItem(Paragraph("A <font face=\"Courier\">stats: {...}</font> line &mdash; check for <font face=\"Courier\">\"backendDevice\":\"gpu\"</font> (or \"cpu\") and millisecond-scale timings. This is the strongest single proof of on-device execution: there is no network call in the inference path, and cloud APIs cannot return in low hundreds of milliseconds with these numbers.", body)),
    ListItem(Paragraph("<font face=\"Courier\">✔ Wrote upscaled image to ...test-gradient.upscaled.png</font>", body)),
    ListItem(Paragraph("<font face=\"Courier\">✔ Wrote before/after comparison page to ...comparison.html</font>", body)),
], bulletType="bullet", leftIndent=14))

story.append(Paragraph("Step 4 — View the result", h2))
story.append(Paragraph(
    "The script auto-opens <font face=\"Courier\">comparison.html</font> in your default browser. "
    "You'll see the original 32&times;32 gradient PNG next to a sharper 128&times;128 output, "
    "generated by <font face=\"Courier\">upscale()</font>. If it didn't open automatically, open "
    "the file manually from <font face=\"Courier\">samples/comparison.html</font>.", body,
))

story.append(Paragraph("Step 5 (optional) — Try your own photo", h2))
story.append(Paragraph("node src/upscale.js path\\to\\any-photo.jpg", code))
story.append(Paragraph(
    "Any PNG/JPEG works. Larger or more detailed photos make the upscaling difference "
    "easier to see.", note,
))

story.append(HRFlowable(width="100%", color=colors.HexColor("#dddddd"), spaceBefore=8, spaceAfter=12))
story.append(Paragraph(
    "Reference: how the code calls the SDK (src/upscale.js, lines 139–171)", h2,
))
story.append(Paragraph(
    "const modelId = await loadModel({<br/>"
    "&nbsp;&nbsp;modelSrc: REALESRGAN_X4PLUS_ANIME_6B,<br/>"
    "&nbsp;&nbsp;modelType: \"diffusion\",<br/>"
    "&nbsp;&nbsp;modelConfig: { mode: \"upscale\", upscaler: { tile_size: args.tileSize } },<br/>"
    "});<br/><br/>"
    "const { outputs, stats } = upscale({ modelId, image: inputBuf, repeats: args.repeats });<br/>"
    "const [upscaledPng] = await outputs;<br/><br/>"
    "await unloadModel({ modelId });",
    code,
))

story.append(Spacer(1, 10))
story.append(Paragraph(
    "Questions or anything CANNOT VERIFY? The full source is one file: "
    "src/upscale.js in the repo above.", note,
))

doc = SimpleDocTemplate(
    "REVIEWER_GUIDE.pdf", pagesize=letter,
    topMargin=0.7*inch, bottomMargin=0.7*inch,
    leftMargin=0.75*inch, rightMargin=0.75*inch,
    title="QVAC Local Upscaler — Reviewer Guide",
)
doc.build(story)
print("Wrote REVIEWER_GUIDE.pdf")
