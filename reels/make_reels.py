#!/usr/bin/env python3
"""Last Minute Dallas - weekly reel generator.
Renders vertical 9:16 MP4 reels (text/event slides, no audio) ready to upload.
Add in-app music on Instagram/TikTok after uploading.
"""
import os, subprocess, math
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

W, H, FPS = 1080, 1920, 24
OUT = os.path.dirname(os.path.abspath(__file__))
FF = imageio_ffmpeg.get_ffmpeg_exe()
DEJA = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
LIB = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

def font(size, path=DEJA):
    return ImageFont.truetype(path, size)

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def gradient(top, bottom):
    img = Image.new("RGB", (W, H))
    px = img.load()
    for y in range(H):
        c = lerp(top, bottom, y / (H - 1))
        for x in range(W):
            px[x, y] = c
    return img

def gradient_fast(top, bottom):
    # build a 1-px-wide column then resize (much faster)
    col = Image.new("RGB", (1, H))
    p = col.load()
    for y in range(H):
        p[0, y] = lerp(top, bottom, y / (H - 1))
    return col.resize((W, H))

def deco(img, accent):
    d = ImageDraw.Draw(img, "RGBA")
    # soft glowing circles for texture
    for (cx, cy, r, a) in [(900, 250, 380, 38), (150, 1500, 460, 30), (980, 1600, 300, 26)]:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=accent + (a,))
    # vignette bottom for text legibility
    grad = Image.new("L", (1, H), 0)
    gp = grad.load()
    for y in range(H):
        t = y / (H - 1)
        gp[0, y] = int(120 * (t ** 2))
    vig = grad.resize((W, H))
    black = Image.new("RGB", (W, H), (0, 0, 0))
    img.paste(black, (0, 0), vig)
    return img

def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=fnt) <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def draw_center_block(draw, lines, fnt, y, fill, gap=14, max_w=W - 160):
    for ln in lines:
        wl = draw.textlength(ln, font=fnt)
        draw.text(((W - wl) / 2, y), ln, font=fnt, fill=fill)
        bbox = fnt.getbbox(ln)
        y += (bbox[3] - bbox[1]) + gap
    return y

def pill(draw, text, fnt, cy, fg, bg):
    tw = draw.textlength(text, font=fnt)
    pad_x, pad_y = 36, 18
    x0 = (W - tw) / 2 - pad_x
    x1 = (W + tw) / 2 + pad_x
    bb = fnt.getbbox(text)
    th = bb[3] - bb[1]
    y0 = cy - pad_y
    y1 = cy + th + pad_y
    draw.rounded_rectangle([x0, y0, x1, y1], radius=(y1 - y0) / 2, fill=bg)
    draw.text(((W - tw) / 2, cy - bb[1]), text, font=fnt, fill=fg)

def base_slide(theme, slide):
    img = gradient_fast(theme["top"], theme["bottom"])
    img = deco(img, theme["accent"])
    d = ImageDraw.Draw(img, "RGBA")
    # brand pill top
    pill(d, "LAST MINUTE DALLAS", font(34, LIB), 90, (255, 255, 255), theme["accent"] + (235,))

    kind = slide["kind"]
    if kind == "cover":
        d_day = font(56, LIB)
        draw_center_block(d, [slide["day"]], d_day, 560, (255, 255, 255))
        title_lines = wrap(d, slide["title"], font(120), W - 120)
        y = 700
        y = draw_center_block(d, title_lines, font(120), y, (255, 255, 255), gap=4)
        if slide.get("hook"):
            draw_center_block(d, wrap(d, slide["hook"], font(46, LIB), W - 200),
                              font(46, LIB), y + 60, theme["accent_text"])
    elif kind == "event":
        # category tag
        pill(d, slide["tag"], font(36, LIB), 470, (10, 10, 10), (255, 255, 255, 235))
        name_lines = wrap(d, slide["name"], font(94), W - 140)
        y = 650
        y = draw_center_block(d, name_lines, font(94), y, (255, 255, 255), gap=6)
        meta = slide.get("meta", "")
        if meta:
            draw_center_block(d, wrap(d, meta, font(54, LIB), W - 200),
                              font(54, LIB), y + 50, theme["accent_text"])
        if slide.get("time"):
            pill(d, slide["time"], font(48), 1500, (10, 10, 10), theme["accent"] + (255,))
    elif kind == "outro":
        big = font(110)
        y = 620
        for ln in slide["lines"]:
            y = draw_center_block(d, [ln], big, y, (255, 255, 255), gap=4)
            y += 40
        draw_center_block(d, [slide.get("handle", "")], font(54, LIB), y + 30,
                          theme["accent_text"])
    return img

def render_reel(theme, slides, out_path, sec_per=3.2, fade=0.4):
    cmd = [FF, "-y", "-f", "rawvideo", "-pixel_format", "rgb24",
           "-video_size", f"{W}x{H}", "-framerate", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "medium", "-pix_fmt", "yuv420p",
           "-movflags", "+faststart", "-r", str(FPS), out_path]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)
    black = Image.new("RGB", (W, H), (0, 0, 0))
    n_frames = int(sec_per * FPS)
    fade_f = int(fade * FPS)
    for slide in slides:
        base = base_slide(theme, slide)
        for f in range(n_frames):
            t = f / max(1, n_frames - 1)
            # ken burns zoom 1.03 -> 1.07
            z = 1.03 + 0.04 * t
            zw, zh = int(W * z), int(H * z)
            zoomed = base.resize((zw, zh))
            left = (zw - W) // 2
            top = int((zh - H) * (0.35 + 0.3 * t))
            frame = zoomed.crop((left, top, left + W, top + H))
            # fade alpha
            if f < fade_f:
                a = f / fade_f
            elif f > n_frames - fade_f:
                a = (n_frames - f) / fade_f
            else:
                a = 1.0
            if a < 1.0:
                frame = Image.blend(black, frame, max(0.0, min(1.0, a)))
            proc.stdin.write(frame.tobytes())
    proc.stdin.close()
    proc.wait()

# ------------------- THEMES -------------------
T_LATIN = dict(top=(60, 8, 70), bottom=(190, 40, 90), accent=(255, 120, 60),
               accent_text=(255, 200, 120))
T_FOOD = dict(top=(40, 24, 10), bottom=(150, 95, 40), accent=(240, 190, 90),
              accent_text=(255, 220, 150))
T_WED = dict(top=(10, 40, 30), bottom=(20, 110, 80), accent=(255, 110, 60),
             accent_text=(180, 255, 210))
T_FAMILY = dict(top=(8, 60, 70), bottom=(40, 160, 150), accent=(255, 180, 70),
                accent_text=(200, 255, 245))
T_JUNE = dict(top=(20, 10, 10), bottom=(120, 20, 25), accent=(40, 160, 80),
              accent_text=(255, 210, 120))
T_SAT = dict(top=(20, 12, 55), bottom=(90, 40, 160), accent=(255, 90, 150),
             accent_text=(200, 200, 255))
T_SUN = dict(top=(120, 50, 90), bottom=(240, 140, 80), accent=(255, 200, 120),
             accent_text=(255, 235, 200))

HANDLE = "Follow @LastMinuteDallas"

REELS = [
 ("01_sun0614_latin_night", T_LATIN, [
    dict(kind="cover", day="SUNDAY · JUNE 14", title="LATIN NIGHT", hook="The weekend isn't over yet"),
    dict(kind="event", tag="LATIN NIGHTLIFE", name="Salsa Sunday", meta="Deep Ellum · Latin DJs + dancing", time="9 PM"),
    dict(kind="event", tag="ELECTRONIC", name="Cristoph (18+)", meta="SILO Dallas", time="7 PM"),
    dict(kind="event", tag="LIVE MUSIC", name="Twin Suns + aka Bobby", meta="Three Links · Deep Ellum", time="7 PM"),
    dict(kind="outro", lines=["SAVE THIS", "TAG YOUR CREW"], handle=HANDLE),
 ]),
 ("02_mon_tue_food_social", T_FOOD, [
    dict(kind="cover", day="MON – TUE · JUNE 15–16", title="FOOD & SOCIAL", hook="Slow nights hit different"),
    dict(kind="event", tag="JAZZ LOUNGE", name="Live Jazz at Babou's", meta="Hôtel Swexan · cocktails + jazz", time="Nightly"),
    dict(kind="event", tag="PATIO NIGHT", name="Vidorra Cocina", meta="Deep Ellum · Latin food + drinks", time="Evenings"),
    dict(kind="event", tag="GOLDEN HOUR", name="Dallas Arboretum", meta="Summer blooms on White Rock Lake", time="Daily"),
    dict(kind="outro", lines=["YOUR MIDWEEK", "RESET"], handle=HANDLE),
 ]),
 ("03_wed0617_salsa_worldcup", T_WED, [
    dict(kind="cover", day="WEDNESDAY · JUNE 17", title="SALSA + WORLD CUP", hook="Dance, then watch the world play"),
    dict(kind="event", tag="LATIN NIGHTLIFE", name="Salsa Wednesdays", meta="Vidorra · FREE beginner lesson 7PM", time="7–11 PM"),
    dict(kind="event", tag="LATIN NIGHTLIFE", name="La Santa", meta="Behind Taboo Lounge · live band", time="Late"),
    dict(kind="event", tag="WORLD CUP", name="England vs Croatia", meta="Dallas Stadium, Arlington", time="Match Day"),
    dict(kind="event", tag="FREE · SPORTS", name="FIFA Fan Festival", meta="Fair Park · big screens + food", time="All Day"),
    dict(kind="outro", lines=["SAVE THIS", "TAG YOUR CREW"], handle=HANDLE),
 ]),
 ("04_thu0618_family", T_FAMILY, [
    dict(kind="cover", day="THURSDAY · JUNE 18", title="FAMILY DAY", hook="Mostly FREE & kid-approved"),
    dict(kind="event", tag="FREE · STEM", name="Perot TECH Truck", meta="Klyde Warren Park · hands-on science", time="11 AM–1 PM"),
    dict(kind="event", tag="FREE · KIDS", name="KidLinks Music & Movement", meta="Klyde Warren · ages 2–6", time="10 AM"),
    dict(kind="event", tag="MARKET", name="Summer Farmers Market", meta="Trinity Overlook Park · opens today", time="10–5:30"),
    dict(kind="outro", lines=["SAVE FOR", "THE FAMILY"], handle=HANDLE),
 ]),
 ("05_fri0619_juneteenth", T_JUNE, [
    dict(kind="cover", day="FRIDAY · JUNE 19", title="JUNETEENTH", hook="Walk. Celebrate. Honor."),
    dict(kind="event", tag="COMMUNITY", name="Opal's Walk for Freedom", meta="2.5-mile walk with Opal Lee", time="Morning"),
    dict(kind="event", tag="FREE · CULTURE", name="African American Museum", meta="Fair Park · performances + exhibits", time="Free Entry"),
    dict(kind="event", tag="LIVE R&B", name="Juneteenth R&B Festival", meta="Slim (112), Case, Jacquees & more", time="Night"),
    dict(kind="event", tag="PRIDE", name="PRIDE Block Party", meta="Dallas Arts District · 9th annual", time="Evening"),
    dict(kind="outro", lines=["SAVE THIS", "SHARE THE JOY"], handle=HANDLE),
 ]),
 ("06_sat0620_food_nightlife", T_SAT, [
    dict(kind="cover", day="SATURDAY · JUNE 20", title="EAT + DANCE", hook="All-day food, all-night vibes"),
    dict(kind="event", tag="FREE · FOOD", name="Juneteenth Flavor Fest", meta="Food vendors, live music, games", time="Afternoon"),
    dict(kind="event", tag="MARKET", name="Summer Farmers Market", meta="Trinity Overlook Park", time="10–5:30"),
    dict(kind="event", tag="NIGHTLIFE", name="Live @ RBC Deep Ellum", meta="Deep Ellum · doors 8PM", time="9 PM"),
    dict(kind="event", tag="LATE SHOW", name="Deep Ellum Art Co", meta="Deep Ellum", time="8 PM"),
    dict(kind="outro", lines=["SAVE THIS", "TAG YOUR CREW"], handle=HANDLE),
 ]),
 ("07_sun0621_wind_down", T_SUN, [
    dict(kind="cover", day="SUNDAY · JUNE 21", title="WIND DOWN", hook="End the week beautifully"),
    dict(kind="event", tag="FAMILY", name="Illuminature at the Zoo", meta="Dallas Zoo · lantern + light festival", time="6:30–10 PM"),
    dict(kind="event", tag="ARTS", name="Ballet North Texas", meta="Moody Performance Hall", time="Evening"),
    dict(kind="event", tag="MARKET", name="Fair Park Farmers Market", meta="Fair Park", time="9 AM"),
    dict(kind="outro", lines=["THAT'S YOUR", "WEEK, DALLAS"], handle=HANDLE),
 ]),
]

if __name__ == "__main__":
    for name, theme, slides in REELS:
        out = os.path.join(OUT, name + ".mp4")
        print("Rendering", name, "...", flush=True)
        render_reel(theme, slides, out)
        print("  ->", out, os.path.getsize(out) // 1024, "KB", flush=True)
    print("DONE")
