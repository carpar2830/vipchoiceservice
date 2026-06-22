"""
VIP Choice Service — Weekly Social Content Graphics Generator
Generates 7 branded PNG graphics using Pillow for Mon-Sat posting schedule.
Run each Sunday evening after computing service rotation (see CLAUDE.md).

Usage: python3 generate_weekly_graphics.py
Output: /tmp/vip_graphics/ (7 PNG files)
"""

import os
from PIL import Image, ImageDraw, ImageFont

NAVY  = (28, 48, 77)    # #1c304d
GOLD  = (196, 158, 87)  # #c49e57
WHITE = (255, 255, 255)
OUT   = "/tmp/vip_graphics"
os.makedirs(OUT, exist_ok=True)


def get_font(size, bold=True):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf" if bold else "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def get_font_r(size):
    return get_font(size, bold=False)


def create_logo():
    """Create branded text logo (fallback — replace with actual PNG if available)."""
    W, H = 350, 140
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rectangle([2, 2, W - 3, H - 3], outline=GOLD, width=3)
    draw.text((12, 8),  "VIP",      font=get_font(52), fill=GOLD)
    draw.text((90, 18), "CHOICE",   font=get_font(30), fill=WHITE)
    draw.text((90, 55), "SERVICE",  font=get_font(28), fill=GOLD)
    draw.text((10, 100), "Taxes · Notary · Business", font=get_font_r(18), fill=(200, 200, 200, 230))
    return img


LOGO = create_logo()


def draw_logo(img, scale=0.28, margin=28):
    w, h = img.size
    lw = int(w * scale)
    lh = int(LOGO.height * (lw / LOGO.width))
    resized = LOGO.resize((lw, lh), Image.LANCZOS)
    img.paste(resized, (w - lw - margin, h - lh - margin), resized)


def divider(draw, y, W, pad=60):
    draw.rectangle([pad, y, W - pad, y + 4], fill=GOLD)


def ctext(draw, text, font, fill, W, y):
    bb = draw.textbbox((0, 0), text, font=font)
    draw.text(((W - (bb[2] - bb[0])) // 2, y), text, font=font, fill=fill)
    return y + (bb[3] - bb[1])


def cwrap(draw, text, font, fill, W, y, max_w, spc=10):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textbbox((0, 0), t, font=font)[2] <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    for line in lines:
        bb = draw.textbbox((0, 0), line, font=font)
        draw.text(((W - (bb[2] - bb[0])) // 2, y), line, font=font, fill=fill)
        y += (bb[3] - bb[1]) + spc
    return y


def ltext(draw, text, font, fill, x, y):
    bb = draw.textbbox((0, 0), text, font=font)
    draw.text((x, y), text, font=font, fill=fill)
    return y + (bb[3] - bb[1])


# ─── Piece generators ────────────────────────────────────────────────────────

def p1_mon_story_notary(label="CONSEJO DE HOY", service="Notary Public", sub="Servicio Movil · Dallas TX"):
    """P1 — Monday IG Story 1080×1920 | Notary | Spanish"""
    W, H = 1080, 1920
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)
    ctext(d, label, get_font(40), GOLD, W, 105)
    divider(d, 175, W)
    y = 220
    y = cwrap(d, "NOTARIA PUBLICA", get_font(90), WHITE, W, y, W - 80, 4) + 10
    y = cwrap(d, sub, get_font(54), GOLD, W, y, W - 80, 4) + 10
    divider(d, y, W); y += 45
    tips = ["Documentos notariados el MISMO DIA",
            "Servicio movil — le visitamos donde este",
            "Apostillas y autenticaciones",
            "Atencion bilingue, con confianza"]
    for t in tips:
        y = ltext(d, f"✦  {t}", get_font_r(48), WHITE, 80, y) + 28
    divider(d, y + 20, W); y += 65
    msg = ("Necesita documentos notariados hoy? Le atendemos en su casa, "
           "oficina o donde mas le convenga — mismo dia, sin complicaciones.")
    y = cwrap(d, msg, get_font_r(48), WHITE, W, y, W - 120, 14) + 40
    divider(d, y, W); y += 55
    ctext(d, "💬 WhatsApp (972) 807-2217", get_font(44), GOLD, W, y); y += 72
    ctext(d, "📅 Reserve en la bio",        get_font(44), WHITE, W, y); y += 72
    ctext(d, "📞 (631) 575-5110",            get_font(44), GOLD, W, y)
    ctext(d, "Taxes · Notary · Business · All in One Trusted Place.", get_font_r(36), (170, 170, 170), W, H - 170)
    draw_logo(img)
    out = f"{OUT}/P1_Mon_IGStory_Notary_ES.png"
    img.save(out); print(f"Saved {out}")


def p2_tue_feed_translations():
    """P2 — Tuesday IG Feed 1080×1080 | Translations | EN/ES"""
    W, H = 1080, 1080
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)
    divider(d, 60, W)
    ctext(d, "USCIS · COURTS · GOVERNMENT", get_font(38), GOLD, W, 82)
    divider(d, 138, W)
    y = 162
    y = cwrap(d, "Certified Translations", get_font(80), WHITE, W, y, W - 60, 4) + 6
    y = cwrap(d, "That Open Doors", get_font(80), GOLD, W, y, W - 60, 4) + 16
    divider(d, y, W); y += 28
    y = cwrap(d, "Traducciones Certificadas que Abren Puertas", get_font(46), WHITE, W, y, W - 100, 6) + 26
    for b in ["USCIS immigration documents", "Court & legal records",
               "Academic & government files", "Fast turnaround · Bilingual team"]:
        y = ltext(d, f"✅  {b}", get_font_r(40), WHITE, 100, y) + 16
    divider(d, y + 12, W); y += 46
    ctext(d, "Book your free consult today!", get_font(44), GOLD, W, y); y += 60
    ctext(d, "📅 Link in bio / Enlace en la bio", get_font(42), WHITE, W, y); y += 58
    ctext(d, "💬 (972) 807-2217  ·  📞 (631) 575-5110", get_font(42), GOLD, W, y)
    ctext(d, "vipchoiceservice.com · 9550 Forest Lane Ste 440, Dallas TX", get_font_r(33), (170, 170, 170), W, H - 58)
    draw_logo(img, scale=0.22)
    out = f"{OUT}/P2_Tue_IGFeed_Translations_ENES.png"
    img.save(out); print(f"Saved {out}")


def p3_wed_story_translations():
    """P3 — Wednesday IG Story 1080×1920 | Translations | Spanish"""
    W, H = 1080, 1920
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)
    ctext(d, "SABIA USTED?", get_font(40), GOLD, W, 105)
    divider(d, 175, W)
    y = 220
    y = cwrap(d, "TRADUCCIONES CERTIFICADAS", get_font(80), WHITE, W, y, W - 60, 4) + 10
    y = cwrap(d, "USCIS · Tribunales · Gobierno", get_font(52), GOLD, W, y, W - 80, 4) + 10
    divider(d, y, W); y += 45
    for tp in ["Aceptadas por USCIS y tribunales", "Equipo bilingue certificado",
               "Entrega rapida para su cita", "Confidencialidad garantizada", "Mas de 15 idiomas disponibles"]:
        y = ltext(d, f"🔖  {tp}", get_font_r(47), WHITE, 80, y) + 28
    divider(d, y + 20, W); y += 65
    msg = ("Cada documento merece una traduccion precisa. Confie en nuestro "
           "equipo para abrir las puertas que su familia necesita.")
    y = cwrap(d, msg, get_font_r(47), WHITE, W, y, W - 120, 14) + 40
    divider(d, y, W); y += 55
    ctext(d, "💬 WhatsApp (972) 807-2217", get_font(44), GOLD, W, y); y += 72
    ctext(d, "📅 Reserve en la bio",        get_font(44), WHITE, W, y)
    ctext(d, "Taxes · Notary · Business · All in One Trusted Place.", get_font_r(36), (170, 170, 170), W, H - 170)
    draw_logo(img)
    out = f"{OUT}/P3_Wed_IGStory_Translations_ES.png"
    img.save(out); print(f"Saved {out}")


def p4_thu_whatsapp():
    """P4 — Thursday WhatsApp Banner 1080×1080 | Spanish"""
    W, H = 1080, 1080
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)
    divider(d, 70, W)
    ctext(d, "Mensaje de VIP Choice Service", get_font(38), GOLD, W, 94)
    divider(d, 152, W)
    y = 185
    y = cwrap(d, "Buenas tardes!", get_font(72), WHITE, W, y, W - 80, 5) + 18
    y = cwrap(d, "Como va su semana?", get_font(50), GOLD, W, y, W - 100, 5) + 30
    divider(d, y, W); y += 35
    body = ("En VIP Choice Service estamos aqui para ayudarle "
            "con todo lo que su negocio y familia necesiten — "
            "notaria, traducciones certificadas o apoyo para "
            "su empresa. Con gusto le atendemos.")
    y = cwrap(d, body, get_font_r(44), WHITE, W, y, W - 100, 14) + 44
    divider(d, y, W); y += 42
    ctext(d, "Responda este mensaje 👇", get_font(42), GOLD, W, y); y += 65
    ctext(d, "💬 (972) 807-2217  ·  📞 (631) 575-5110", get_font(42), WHITE, W, y)
    ctext(d, "vipchoiceservice.com · Dallas, TX", get_font_r(33), (170, 170, 170), W, H - 58)
    draw_logo(img, scale=0.22)
    out = f"{OUT}/P4_Thu_WhatsApp_ES.png"
    img.save(out); print(f"Saved {out}")


def p5_fri_story_smallbiz():
    """P5 — Friday IG Story 1080×1920 | Small Business Support | Spanish"""
    W, H = 1080, 1920
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)
    ctext(d, "ESTE FIN DE SEMANA", get_font(40), GOLD, W, 105)
    divider(d, 175, W)
    y = 215
    y = cwrap(d, "APOYO PARA SU NEGOCIO", get_font(80), WHITE, W, y, W - 60, 4) + 10
    y = cwrap(d, "Nomina · Registro · Cumplimiento", get_font(52), GOLD, W, y, W - 80, 4) + 10
    divider(d, y, W); y += 45
    for s in ["ADP · Nomina y control de tiempo", "Sistemas POS para su negocio",
               "Reloj biometrico con geovalla", "Contratacion y cumplimiento laboral",
               "BOI — Actualice su registro HOY"]:
        y = ltext(d, f"💼  {s}", get_font_r(47), WHITE, 80, y) + 28
    divider(d, y + 20, W); y += 65
    msg = ("Aun no ha actualizado el BOI de su empresa? Tiene 30 dias desde cualquier "
           "cambio. Disponibles este fin de semana — hablemos hoy.")
    y = cwrap(d, msg, get_font_r(47), WHITE, W, y, W - 120, 14) + 40
    divider(d, y, W); y += 55
    ctext(d, "💬 WhatsApp (972) 807-2217", get_font(44), GOLD, W, y); y += 72
    ctext(d, "📅 Reserve en la bio",        get_font(44), WHITE, W, y); y += 72
    ctext(d, "📞 (631) 575-5110",            get_font(44), GOLD, W, y)
    ctext(d, "Taxes · Notary · Business · All in One Trusted Place.", get_font_r(36), (170, 170, 170), W, H - 170)
    draw_logo(img)
    out = f"{OUT}/P5_Fri_IGStory_SmallBiz_ES.png"
    img.save(out); print(f"Saved {out}")


def p6_sat_feed_notary():
    """P6 — Saturday IG Feed 1080×1080 | Notary (lead-gen) | EN/ES"""
    W, H = 1080, 1080
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)
    divider(d, 60, W)
    ctext(d, "SAME-DAY · MOBILE · DALLAS", get_font(40), GOLD, W, 82)
    divider(d, 138, W)
    y = 162
    y = cwrap(d, "Mobile Notary", get_font(84), WHITE, W, y, W - 60, 4) + 5
    y = cwrap(d, "At Your Service", get_font(84), GOLD, W, y, W - 60, 4) + 14
    divider(d, y, W); y += 26
    y = cwrap(d, "Notaria Movil · Mismo Dia · A Su Servicio", get_font(46), WHITE, W, y, W - 100, 6) + 24
    for b in ["Documents notarized same day", "Mobile — we come to your location",
               "Apostilles & legal authentication", "Bilingual — English & Espanol"]:
        y = ltext(d, f"📋  {b}", get_font_r(40), WHITE, 90, y) + 16
    divider(d, y + 10, W); y += 40
    ctext(d, "Book your free consult today!", get_font(46), GOLD, W, y); y += 64
    ctext(d, "📅 Link in bio / Enlace en la bio", get_font(42), WHITE, W, y); y += 58
    ctext(d, "💬 (972) 807-2217  ·  📞 (631) 575-5110", get_font(42), GOLD, W, y)
    ctext(d, "vipchoiceservice.com · 9550 Forest Lane Ste 440, Dallas TX", get_font_r(33), (170, 170, 170), W, H - 58)
    draw_logo(img, scale=0.22)
    out = f"{OUT}/P6_Sat_IGFeed_Notary_ENES.png"
    img.save(out); print(f"Saved {out}")


def p7_gbp_notary():
    """P7 — Tuesday GBP 1200×900 | Notary | English"""
    W, H = 1200, 900
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)
    divider(d, 55, W)
    ctext(d, "DALLAS MOBILE NOTARY", get_font(44), GOLD, W, 76)
    divider(d, 138, W)
    y = 162
    y = cwrap(d, "Same-Day Notary Service", get_font(82), WHITE, W, y, W - 80, 4) + 6
    y = cwrap(d, "Forest Lane · Dallas, TX 75243", get_font(46), GOLD, W, y, W - 100, 4) + 22
    divider(d, y, W); y += 26
    for s in ["Document notarization — same day available",
               "Mobile service — we come to you in Dallas & DFW",
               "Apostilles, authentication & legal documents",
               "Bilingual team — English & Spanish"]:
        y = ltext(d, f"✓  {s}", get_font_r(40), WHITE, 80, y) + 16
    divider(d, y + 10, W); y += 42
    ctext(d, "📞 Call (631) 575-5110", get_font(42), GOLD, W, y); y += 62
    ctext(d, "📅 Book: calendly.com/vipchoiceservice/60min", get_font(42), WHITE, W, y)
    ctext(d, "9550 Forest Lane, Suite 440, Dallas TX 75243  ·  vipchoiceservice.com",
          get_font_r(33), (170, 170, 170), W, H - 52)
    draw_logo(img, scale=0.20, margin=22)
    out = f"{OUT}/P7_Tue_GBP_Notary_EN.png"
    img.save(out); print(f"Saved {out}")


if __name__ == "__main__":
    p1_mon_story_notary()
    p2_tue_feed_translations()
    p3_wed_story_translations()
    p4_thu_whatsapp()
    p5_fri_story_smallbiz()
    p6_sat_feed_notary()
    p7_gbp_notary()
    print(f"\nAll 7 graphics saved to {OUT}/")
