from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

root = Path(__file__).resolve().parent
source = root / "Video_Guideline.md"
dest = root / "Video_Guideline.pdf"
text = source.read_text(encoding="utf-8")
lines = text.splitlines()

c = canvas.Canvas(str(dest), pagesize=letter)
width, height = letter

x = 40
y = height - 40

c.setFont("Helvetica-Bold", 16)
c.drawString(x, y, "FinGuard AI Video Guideline")
y -= 24

c.setFont("Helvetica", 10)
for line in lines:
    if y < 60:
        c.showPage()
        y = height - 40
        c.setFont("Helvetica", 10)
    if line.startswith("# "):
        c.setFont("Helvetica-Bold", 14)
        c.drawString(x, y, line[2:].strip())
        y -= 18
        c.setFont("Helvetica", 10)
    elif line.startswith("## "):
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x, y, line[3:].strip())
        y -= 16
        c.setFont("Helvetica", 10)
    elif line.startswith("### "):
        c.setFont("Helvetica-Bold", 11)
        c.drawString(x, y, line[4:].strip())
        y -= 14
        c.setFont("Helvetica", 10)
    elif line.startswith("* "):
        c.drawString(x + 20, y, "• " + line[2:].strip())
        y -= 12
    elif line.strip() == "":
        y -= 10
    else:
        c.drawString(x, y, line)
        y -= 12

c.save()
print(f"Created {dest}")
