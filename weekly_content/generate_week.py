#!/usr/bin/env python3
"""
VIP Choice Service — Weekly Content Generator
Week of June 9-14, 2026 | W=24
A=S6 Small Business Support | B=S2 Notary Public | C=S4 Certified Translations
Calendar flag: Q2 Estimated Taxes due Jun 15
"""

import base64, io, os, textwrap
from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUTPUT_DIR = "/home/user/vipchoiceservice/weekly_content/Week_2026-06-09"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Brand colors
NAVY   = (28,  48,  77)   # #1c304d
GOLD   = (196, 158, 87)   # #c49e57
WHITE  = (255, 255, 255)
DARK   = (15,  25,  50)

# Fonts
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG  = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

def F(size, bold=False):
    try:
        return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)
    except Exception:
        return ImageFont.load_default()

# ── Logo ─────────────────────────────────────────────────────────────────────
LOGO_PATH = "/home/user/vipchoiceservice/weekly_content/vipsolo_logo.png"

def load_logo():
    # Try to load the real logo from disk first
    try:
        if os.path.exists(LOGO_PATH):
            logo = Image.open(LOGO_PATH).convert("RGBA")
            if logo.width > 10:        # sanity check — not a corrupt stub
                return logo
    except Exception:
        pass
    # Fallback: render a compact branded badge (350×90 px, transparent bg)
    W, H = 350, 90
    badge = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(badge)
    d.rectangle([(0,0),(W-1,H-1)], fill=(28,48,77,230))
    d.rectangle([(0,0),(W-1,6)], fill=GOLD+(255,))
    d.rectangle([(0,H-7),(W-1,H-1)], fill=GOLD+(255,))
    try:
        f1 = ImageFont.truetype(FONT_BOLD, 32)
        f2 = ImageFont.truetype(FONT_REG, 18)
    except Exception:
        f1 = f2 = ImageFont.load_default()
    d.text((14, 14), "VIP", fill=GOLD+(255,), font=f1)
    d.text((70, 20), "CHOICE", fill=WHITE+(255,), font=f1)
    d.text((14, 58), "SERVICE  ·  vipchoiceservice.com", fill=WHITE+(200,), font=f2)
    return badge

def paste_logo(img, padding=40, max_w_frac=0.22):
    logo = load_logo()
    if logo is None:
        return img
    new_w = int(img.width * max_w_frac)
    ratio = new_w / logo.width
    new_h = max(1, int(logo.height * ratio))
    logo_r = logo.resize((new_w, new_h), Image.LANCZOS)
    x = img.width  - new_w - padding
    y = img.height - new_h - padding
    base = img.convert("RGBA")
    base.paste(logo_r, (x, y), logo_r)
    return base.convert("RGB")

def gline(draw, x1, y1, x2, y2, w=6):
    draw.line([(x1,y1),(x2,y2)], fill=GOLD, width=w)

def center_text(draw, text, y, font, color, canvas_w):
    try:
        bbox = draw.textbbox((0,0), text, font=font)
        tw = bbox[2] - bbox[0]
    except Exception:
        tw = len(text) * font.size // 2
    draw.text(((canvas_w - tw) // 2, y), text, fill=color, font=font)
    try:
        bbox = draw.textbbox((0, y), text, font=font)
        return bbox[3] - bbox[1]
    except Exception:
        return font.size

def text_h(draw, text, font):
    try:
        bbox = draw.textbbox((0,0), text, font=font)
        return bbox[3] - bbox[1]
    except Exception:
        return font.size

# ─────────────────────────────────────────────────────────────────────────────
#  STORY template  1080 × 1920
# ─────────────────────────────────────────────────────────────────────────────
def make_story(fname, category_label, headline_lines, body_items, cta):
    W, H = 1080, 1920
    img = Image.new("RGB", (W,H), NAVY)
    d   = ImageDraw.Draw(img)

    # — Top gold bar —
    d.rectangle([(0,0),(W,90)], fill=GOLD)
    f_cat = F(38, bold=True)
    center_text(d, category_label, 26, f_cat, NAVY, W)

    # — Brand line —
    f_brand = F(46, bold=True)
    center_text(d, "VIP CHOICE SERVICE", 108, f_brand, GOLD, W)

    gline(d, 80, 178, W-80, 178, w=4)

    # — Headline —
    f_hdl = F(70, bold=True)
    y = 206
    for line in headline_lines:
        th = text_h(d, line, f_hdl)
        center_text(d, line, y, f_hdl, WHITE, W)
        y += th + 16

    gline(d, 80, y+18, W-80, y+18, w=3)
    y += 50

    # — Bullet items —
    f_item = F(52, bold=False)
    for item in body_items:
        th = text_h(d, item, f_item)
        center_text(d, item, y, f_item, WHITE, W)
        y += th + 28

    # — Bottom CTA bar —
    d.rectangle([(0, H-160),(W, H)], fill=DARK)
    gline(d, 0, H-160, W, H-160, w=4)
    f_cta = F(44, bold=True)
    center_text(d, cta, H-118, f_cta, GOLD, W)

    img = paste_logo(img, padding=35, max_w_frac=0.20)
    path = os.path.join(OUTPUT_DIR, fname)
    img.save(path, "PNG", optimize=True)
    print(f"  ✓ {fname}")
    return path

# ─────────────────────────────────────────────────────────────────────────────
#  FEED template  1080 × 1080
# ─────────────────────────────────────────────────────────────────────────────
def make_feed(fname, headline, sub_headline, body_items, phones, cta_bar):
    W, H = 1080, 1080
    img = Image.new("RGB", (W,H), NAVY)
    d   = ImageDraw.Draw(img)

    # Top gold bar
    d.rectangle([(0,0),(W,82)], fill=GOLD)
    f_brand = F(36, bold=True)
    center_text(d, "VIP CHOICE SERVICE", 22, f_brand, NAVY, W)

    # Bottom gold CTA bar
    d.rectangle([(0, H-110),(W,H)], fill=GOLD)
    f_cta = F(36, bold=True)
    center_text(d, cta_bar, H-78, f_cta, NAVY, W)

    # Headline
    f_hdl = F(64, bold=True)
    y = 104
    th = text_h(d, headline, f_hdl)
    center_text(d, headline, y, f_hdl, GOLD, W)
    y += th + 10

    # Sub-headline
    f_sub = F(44, bold=False)
    th = text_h(d, sub_headline, f_sub)
    center_text(d, sub_headline, y, f_sub, WHITE, W)
    y += th + 18

    gline(d, 80, y+6, W-80, y+6, w=3)
    y += 30

    # Body items
    f_item = F(44)
    for item in body_items:
        th = text_h(d, item, f_item)
        center_text(d, item, y, f_item, WHITE, W)
        y += th + 22

    y += 16
    gline(d, 80, y, W-80, y, w=2)
    y += 22

    # Phone CTA
    f_ph = F(40, bold=True)
    for line in phones:
        th = text_h(d, line, f_ph)
        center_text(d, line, y, f_ph, GOLD, W)
        y += th + 12

    img = paste_logo(img, padding=28, max_w_frac=0.19)
    path = os.path.join(OUTPUT_DIR, fname)
    img.save(path, "PNG", optimize=True)
    print(f"  ✓ {fname}")
    return path

# ─────────────────────────────────────────────────────────────────────────────
#  WHATSAPP BANNER template  1080 × 1080
# ─────────────────────────────────────────────────────────────────────────────
def make_whatsapp(fname, alert_line, body_lines, cta_line):
    W, H = 1080, 1080
    img = Image.new("RGB", (W,H), NAVY)
    d   = ImageDraw.Draw(img)

    # accent bar top
    d.rectangle([(0,0),(W,82)], fill=GOLD)
    f_brand = F(36, bold=True)
    center_text(d, "VIP CHOICE SERVICE — MENSAJE PRIVADO", 22, f_brand, NAVY, W)

    # Big alert headline
    f_alert = F(60, bold=True)
    y = 110
    for line in textwrap.wrap(alert_line, width=26):
        th = text_h(d, line, f_alert)
        center_text(d, line, y, f_alert, GOLD, W)
        y += th + 14

    gline(d, 80, y+10, W-80, y+10, w=3)
    y += 44

    # Body
    f_body = F(46)
    for line in body_lines:
        for wrapped in textwrap.wrap(line, width=32):
            th = text_h(d, wrapped, f_body)
            center_text(d, wrapped, y, f_body, WHITE, W)
            y += th + 20

    y += 10
    gline(d, 80, y, W-80, y, w=2)
    y += 28

    # CTA
    f_cta = F(50, bold=True)
    for line in textwrap.wrap(cta_line, width=28):
        th = text_h(d, line, f_cta)
        center_text(d, line, y, f_cta, GOLD, W)
        y += th + 14

    img = paste_logo(img, padding=28, max_w_frac=0.19)
    path = os.path.join(OUTPUT_DIR, fname)
    img.save(path, "PNG", optimize=True)
    print(f"  ✓ {fname}")
    return path

# ─────────────────────────────────────────────────────────────────────────────
#  GBP template  1200 × 900
# ─────────────────────────────────────────────────────────────────────────────
def make_gbp(fname, headline, body_items, phone):
    W, H = 1200, 900
    img = Image.new("RGB", (W,H), NAVY)
    d   = ImageDraw.Draw(img)

    # Top gold bar
    d.rectangle([(0,0),(W,90)], fill=GOLD)
    f_brand = F(40, bold=True)
    center_text(d, "VIP CHOICE SERVICE  ·  DALLAS, TX", 24, f_brand, NAVY, W)

    # Bottom address bar
    d.rectangle([(0, H-90),(W,H)], fill=DARK)
    gline(d, 0, H-90, W, H-90, w=3)
    f_addr = F(28)
    addr = "9550 Forest Lane, Suite 440 · Dallas, TX 75243 · vipchoiceservice.com"
    center_text(d, addr, H-64, f_addr, GOLD, W)

    # Headline
    f_hdl = F(60, bold=True)
    y = 112
    for line in textwrap.wrap(headline, width=32):
        th = text_h(d, line, f_hdl)
        center_text(d, line, y, f_hdl, WHITE, W)
        y += th + 14

    gline(d, 100, y+10, W-100, y+10, w=3)
    y += 44

    # Body items
    f_item = F(42)
    for item in body_items:
        th = text_h(d, item, f_item)
        center_text(d, item, y, f_item, WHITE, W)
        y += th + 20

    y += 14
    gline(d, 100, y, W-100, y, w=2)
    y += 26

    # Phone
    f_ph = F(46, bold=True)
    th = text_h(d, phone, f_ph)
    center_text(d, phone, y, f_ph, GOLD, W)

    img = paste_logo(img, padding=28, max_w_frac=0.18)
    path = os.path.join(OUTPUT_DIR, fname)
    img.save(path, "PNG", optimize=True)
    print(f"  ✓ {fname}")
    return path

# ═══════════════════════════════════════════════════════════════════════════
#  GENERATE ALL 7 PIECES
# ═══════════════════════════════════════════════════════════════════════════

print("\n📐 Generating graphics for Week of June 9–14, 2026…\n")

# --- P1: Monday IG Story — Small Business Support (S6) ---
p1 = make_story(
    "P1_Mon_Story_SmallBizSupport.png",
    category_label="SOPORTE PARA NEGOCIOS",
    headline_lines=["Su negocio merece", "una base sólida."],
    body_items=[
        "✅  Nómina con ADP",
        "✅  Reloj de tiempo geofenciado",
        "✅  Contratación y cumplimiento",
        "✅  Punto de venta (POS)",
        "✅  Precios personalizados",
    ],
    cta="💬 WhatsApp (972) 807-2217"
)

# --- P2: Tuesday IG Feed — Notary Public (S2) bilingual ---
p2 = make_feed(
    "P2_Tue_Feed_Notary.png",
    headline="Same-Day Mobile Notary",
    sub_headline="Notario Móvil — el Mismo Día",
    body_items=[
        "✅  Apostilles / Apostillas",
        "✅  Loan Signings / Firmas de Préstamos",
        "✅  Gov't Documents / Documentos Oficiales",
        "✅  We come to you / Vamos a donde usted esté",
    ],
    phones=[
        "📞 (631) 575-5110   💬 (972) 807-2217",
    ],
    cta_bar="Link in bio / Enlace en la bio"
)

# --- P3: Wednesday IG Story — Notary Public (S2) Spanish ---
p3 = make_story(
    "P3_Wed_Story_Notary.png",
    category_label="NOTARIO PÚBLICO",
    headline_lines=["Dallas confía en", "VIP Choice Service."],
    body_items=[
        "✅  Apostillas oficiales",
        "✅  Notario móvil — vamos a usted",
        "✅  Mismo día disponible",
        "✅  Servicio rápido y confiable",
        "✅  Más de 5 años en Dallas",
    ],
    cta="💬 WhatsApp (972) 807-2217"
)

# --- P4: Thursday WhatsApp Banner — Q2 Estimated Taxes deadline ---
p4 = make_whatsapp(
    "P4_Thu_WhatsApp_Q2Taxes.png",
    alert_line="⚠️  Impuestos Q2 vencen el 15 de junio",
    body_lines=[
        "Buenos días 🌅",
        "El domingo 15 de junio es el plazo para",
        "el pago de impuestos estimados del 2° trimestre.",
        "¿Ya está al día? Podemos ayudarle a",
        "calcular y hacer su pago a tiempo.",
        "— Carlos y su equipo 📋",
    ],
    cta_line="Responda este mensaje hoy mismo"
)

# --- P5: Friday IG Story — Certified Translations (S4) + Q2 reminder ---
p5 = make_story(
    "P5_Fri_Story_Translations.png",
    category_label="TRADUCCIONES CERTIFICADAS",
    headline_lines=["¿Necesita una", "traducción certificada?"],
    body_items=[
        "📄  USCIS e Inmigración",
        "⚖️   Documentos para la corte",
        "🏛️  Gobierno federal y estatal",
        "⏱️  Entrega en 24–48 horas",
        "📅  Recuerde: Q2 vence mañana",
    ],
    cta="💬 WhatsApp (972) 807-2217"
)

# --- P6: Saturday IG Feed — Notary Public (S2) bilingual, "book consult" ---
p6 = make_feed(
    "P6_Sat_Feed_Notary_BkConsult.png",
    headline="Your Dallas Notary — On Demand",
    sub_headline="Su Notario en Dallas — Cuando lo Necesite",
    body_items=[
        "✅  Mobile · Fast · Trusted",
        "✅  Apostilles · Loan Signings · Gov't Docs",
        "✅  Móvil · Rápido · De Confianza",
        "🎯  Book a FREE 15-min consult today!",
    ],
    phones=[
        "📞 (631) 575-5110   💬 (972) 807-2217",
    ],
    cta_bar="Link in bio / Enlace en la bio"
)

# --- P7: GBP Post — Notary Public (S2) Dallas SEO ---
p7 = make_gbp(
    "P7_GBP_Notary_Dallas.png",
    headline="Same-Day Mobile Notary in Dallas, TX",
    body_items=[
        "✅  Apostilles — state & federal",
        "✅  Loan signings & real-estate closings",
        "✅  Government & immigration documents",
        "✅  Serving Forest Lane, Lake Highlands,",
        "      Richardson, Garland & all of North Dallas",
        "📅  Book online → calendly.com/vipchoiceservice/60min",
    ],
    phone="📞 Call (631) 575-5110  ·  vipchoiceservice.com"
)

print("\n✅ All 7 graphics saved.\n")

# ═══════════════════════════════════════════════════════════════════════════
#  GENERATE .DOCX CONTENT PACKAGE
# ═══════════════════════════════════════════════════════════════════════════

doc = Document()

# ── Styles helper ──────────────────────────────────────────────────────────
def add_heading(doc, text, level=1):
    p = doc.add_heading(text, level=level)
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    return p

def add_body(doc, text, bold=False, color=None):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.bold = bold
    if color:
        run.font.color.rgb = RGBColor(*color)
    return p

def add_meta(doc, **kv):
    """Add key: value lines in a compact format."""
    for k, v in kv.items():
        p = doc.add_paragraph()
        r1 = p.add_run(f"{k}: ")
        r1.bold = True
        r1.font.color.rgb = RGBColor(*GOLD)
        r2 = p.add_run(v)
        r2.bold = False

def separator(doc):
    doc.add_paragraph("─" * 80)

# ── Title Page ─────────────────────────────────────────────────────────────
doc.add_heading("VIP Choice Service", 0)
add_body(doc, "Weekly Social Content Package", bold=True)
add_body(doc, "Week of June 9–14, 2026 (ISO Week 24)")
add_body(doc, "")
add_body(doc, "Service Rotation (W=24):")
add_body(doc, "  Service A (Mon Story)  → S6: Small Business Support")
add_body(doc, "  Service B (Wed Story)  → S2: Notary Public")
add_body(doc, "  Service C (Fri Story)  → S4: Certified Translations")
add_body(doc, "")
add_body(doc, "⚠️  Calendar Flag: Q2 Estimated Taxes due Sunday June 15 — woven into Pieces 4 & 5.", bold=True)
add_body(doc, "Seasonal Tone: Mid-year planning · Amendments · BOI catch-up")
doc.add_page_break()

# ─────────────────────────────────────────────────────────────────────────────
separator(doc)
add_heading(doc, "PIECE 1 — Monday IG Story", 1)
separator(doc)
add_meta(doc,
    Platform="Instagram Story",
    Date="Monday, June 9, 2026",
    Time="11:30 AM CT",
    Format="1080 × 1920 (vertical)",
    Service="S6 — Small Business Support",
    Language="Spanish (usted form)",
    Filename="P1_Mon_Story_SmallBizSupport.png",
)
doc.add_paragraph("")
add_body(doc, "CAPTION / COPY:", bold=True)
doc.add_paragraph(
"""🏢 ¿Tiene empleados? Nosotros le ayudamos con todo.

En VIP Choice Service llevamos la operación de su negocio para que usted se enfoque en crecer.

✅ Nómina con ADP
✅ Reloj de tiempo geofenciado
✅ Contratación y cumplimiento laboral
✅ Sistema de punto de venta (POS)
✅ Precios personalizados para su negocio

💬 Escríbanos por WhatsApp → (972) 807-2217
📅 Reserve en la bio"""
)
add_body(doc, "GRAPHIC CTA STICKER: WhatsApp link sticker pointing to wa.me/19728072217", bold=True)
doc.add_paragraph("")
doc.add_page_break()

# ─────────────────────────────────────────────────────────────────────────────
separator(doc)
add_heading(doc, "PIECE 2 — Tuesday IG Feed Post", 1)
separator(doc)
add_meta(doc,
    Platform="Instagram Feed",
    Date="Tuesday, June 10, 2026",
    Time="7:00 PM CT",
    Format="1080 × 1080 (square)",
    Service="S2 — Notary Public (lead-gen hero)",
    Language="Bilingual EN / ES",
    Filename="P2_Tue_Feed_Notary.png",
)
doc.add_paragraph("")
add_body(doc, "CAPTION / COPY (English first):", bold=True)
doc.add_paragraph(
"""Need a document notarized — TODAY? 📋

VIP Choice Service offers same-day mobile notary service in Dallas, TX. We come to you — office, home, or hospital.

✅ Apostilles
✅ Loan Signings & Real-Estate Closings
✅ Government & Immigration Documents

¿Necesita un notario hoy mismo? 🇲🇽
Servicio de notario móvil el mismo día en Dallas.
Vamos a donde usted esté — oficina, hogar o hospital.

📞 Call (631) 575-5110
💬 WhatsApp (972) 807-2217
📅 Link in bio / Enlace en la bio"""
)
add_body(doc, "HASHTAGS (14):", bold=True)
doc.add_paragraph(
"#DallasNotary #MobileNotary #NotaryPublic #Apostilla #NotarioPublico "
"#DallasTexas #NegociosDallas #DallasBusiness #VIPChoiceService "
"#DallasHispano #LoanSigning #ApostilleTexas #DocumentoOficial #SameDayNotary"
)
doc.add_paragraph("")
doc.add_page_break()

# ─────────────────────────────────────────────────────────────────────────────
separator(doc)
add_heading(doc, "PIECE 3 — Wednesday IG Story", 1)
separator(doc)
add_meta(doc,
    Platform="Instagram Story",
    Date="Wednesday, June 11, 2026",
    Time="11:30 AM CT",
    Format="1080 × 1920 (vertical)",
    Service="S2 — Notary Public",
    Language="Spanish (usted form)",
    Filename="P3_Wed_Story_Notary.png",
)
doc.add_paragraph("")
add_body(doc, "CAPTION / COPY:", bold=True)
doc.add_paragraph(
"""🔏 Miles de clientes en Dallas nos confían sus documentos más importantes.

¿Por qué elegir VIP Choice Service para su notarización?

✅ Apostillas oficiales y reconocidas
✅ Notario móvil — vamos a donde usted esté
✅ Mismo día disponible — llame y agendamos hoy
✅ Servicio rápido, preciso y de confianza
✅ Más de 5 años sirviendo a la comunidad de Dallas

💬 Contáctenos hoy por WhatsApp → (972) 807-2217"""
)
add_body(doc, "GRAPHIC CTA STICKER: WhatsApp link sticker pointing to wa.me/19728072217", bold=True)
doc.add_paragraph("")
doc.add_page_break()

# ─────────────────────────────────────────────────────────────────────────────
separator(doc)
add_heading(doc, "PIECE 4 — Thursday WhatsApp Broadcast", 1)
separator(doc)
add_meta(doc,
    Platform="WhatsApp Business Broadcast",
    Date="Thursday, June 12, 2026",
    Time="10:30 AM CT",
    Format="1080 × 1080 banner + message body",
    Angle="Q2 Estimated Taxes deadline (Jun 15) — calendar intelligence",
    Language="Spanish (usted form)",
    Filename="P4_Thu_WhatsApp_Q2Taxes.png",
)
doc.add_paragraph("")
add_body(doc, "MESSAGE BODY (60–100 words, ready to paste):", bold=True)
doc.add_paragraph(
"""Buenos días 🌅

El próximo domingo 15 de junio vence el pago de impuestos estimados del 2.° trimestre (Q2). ¿Ya está al día?

En VIP Choice Service le ayudamos a calcular y tramitar su pago a tiempo — sin multas, sin sorpresas.

Responda este mensaje hoy mismo y le contactamos de inmediato.

— Carlos y su equipo 📋
VIP Choice Service · (631) 575-5110"""
)
add_body(doc, "CTA: Responda este mensaje / Reply to this broadcast", bold=True)
doc.add_paragraph("")
doc.add_page_break()

# ─────────────────────────────────────────────────────────────────────────────
separator(doc)
add_heading(doc, "PIECE 5 — Friday IG Story", 1)
separator(doc)
add_meta(doc,
    Platform="Instagram Story",
    Date="Friday, June 13, 2026",
    Time="11:30 AM CT",
    Format="1080 × 1920 (vertical)",
    Service="S4 — Certified Translations  +  Q2 tax-deadline nudge",
    Language="Spanish (usted form)",
    Filename="P5_Fri_Story_Translations.png",
)
doc.add_paragraph("")
add_body(doc, "CAPTION / COPY:", bold=True)
doc.add_paragraph(
"""📄 ¿Necesita una traducción certificada urgente?

Contamos con traductores certificados para:

📄 USCIS e Inmigración
⚖️  Documentos para la corte
🏛️ Gobierno federal y estatal
🎓 Títulos y diplomas académicos

⏱️ Entregamos en 24–48 horas hábiles.

📅 Y recuerde: mañana (15 de junio) vence el pago de impuestos estimados Q2. Si necesita ayuda con eso también, ¡escríbanos!

💬 WhatsApp → (972) 807-2217"""
)
add_body(doc, "GRAPHIC CTA STICKER: WhatsApp link sticker pointing to wa.me/19728072217", bold=True)
doc.add_paragraph("")
doc.add_page_break()

# ─────────────────────────────────────────────────────────────────────────────
separator(doc)
add_heading(doc, "PIECE 6 — Saturday IG Feed Post", 1)
separator(doc)
add_meta(doc,
    Platform="Instagram Feed",
    Date="Saturday, June 14, 2026",
    Time="10:30 AM CT",
    Format="1080 × 1080 (square)",
    Service="S2 — Notary Public (lead-gen hero, free-consult pitch)",
    Language="Bilingual EN / ES",
    Filename="P6_Sat_Feed_Notary_BkConsult.png",
)
doc.add_paragraph("")
add_body(doc, "CAPTION / COPY:", bold=True)
doc.add_paragraph(
"""Your Dallas notary — on demand. 📋

VIP Choice Service brings professional notary service to your door, same day.

✅ Mobile. Fast. Trusted.
✅ Apostilles · Loan Signings · Government Documents
✅ Real-estate closings · Immigration docs

🎯 Book a FREE 15-minute consultation today — no obligation.

---

Su notario en Dallas — cuando lo necesite. 📋
Servicio móvil, el mismo día, a su puerta.

✅ Móvil. Rápido. De confianza.
✅ Apostillas · Firmas · Documentos Oficiales
🎯 Reserve su consulta gratuita de 15 min hoy mismo.

📞 (631) 575-5110
💬 WhatsApp (972) 807-2217
📅 Link in bio / Enlace en la bio"""
)
add_body(doc, "HASHTAGS (14):", bold=True)
doc.add_paragraph(
"#DallasNotary #MobileNotary #Apostilla #LoanSigning #DallasTexas "
"#NegociosDallas #VIPChoiceService #NotarioPublico #DallasHispano "
"#SmallBusinessDallas #NotaryPublic #DocumentoOficial #DallasBusiness #FreeConsult"
)
doc.add_paragraph("")
doc.add_page_break()

# ─────────────────────────────────────────────────────────────────────────────
separator(doc)
add_heading(doc, "PIECE 7 — Google Business Profile Post (English)", 1)
separator(doc)
add_meta(doc,
    Platform="Google Business Profile",
    Date="Tuesday, June 10, 2026",
    Time="2:00 PM CT",
    Format="1200 × 900",
    Service="S2 — Notary Public (local SEO)",
    Language="English",
    Filename="P7_GBP_Notary_Dallas.png",
)
doc.add_paragraph("")
add_body(doc, "POST COPY (~150 words):", bold=True)
doc.add_paragraph(
"""Need a document notarized in Dallas? VIP Choice Service has you covered — same day, at your location.

We offer professional mobile notary services throughout the Dallas–Fort Worth area, including Forest Lane, Lake Highlands, Richardson, Garland, Plano, and beyond. Whether you need an apostille for an international document, a real-estate loan signing, or an immigration document notarized for USCIS, our certified notaries come to you.

✅ Apostilles (Texas Secretary of State recognized)
✅ Loan signings & real-estate closings
✅ Government & immigration documents
✅ Same-day scheduling available

📞 Call us: (631) 575-5110
📅 Book online: calendly.com/vipchoiceservice/60min

VIP Choice Service · 9550 Forest Lane, Suite 440 · Dallas, TX 75243
Taxes. Notary. Business. All in One Trusted Place."""
)
add_body(doc, "GBP CTA BUTTON: 'Book online' → calendly.com/vipchoiceservice/60min", bold=True)
doc.add_paragraph("")

# ─── Save docx ───────────────────────────────────────────────────────────────
docx_path = os.path.join(OUTPUT_DIR, "VIPChoice_WeekOf_2026-06-09_ContentPackage.docx")
doc.save(docx_path)
print(f"  ✓ VIPChoice_WeekOf_2026-06-09_ContentPackage.docx")
print("\n🎉 All deliverables generated successfully.\n")

# Print summary
print("Files in output directory:")
for f in sorted(os.listdir(OUTPUT_DIR)):
    size = os.path.getsize(os.path.join(OUTPUT_DIR, f))
    print(f"  {f:55s}  {size/1024:.1f} KB")
