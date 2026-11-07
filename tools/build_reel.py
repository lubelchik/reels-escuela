#!/usr/bin/env python3
"""Arma el reel 9:16 (≈59 s) a partir del video original.
Uso: python3 tools/build_reel.py VIDEO_ORIGINAL.mp4 [salida.mp4]
Si re-exportás el original desde Filmora SIN marca de agua, volvé a correr este script con ese archivo.
Requiere: ffmpeg, Pillow. Fuentes y escudo en assets/."""
import subprocess, sys, os, tempfile
from PIL import Image, ImageDraw, ImageFont

SRC = sys.argv[1]
OUT = sys.argv[2] if len(sys.argv) > 2 else "reel_ciberbullying_60s.mp4"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(ROOT, "assets")
W, H = 1080, 1920
VERDE_NOCHE, VERDE_INST, TERRACOTA, NARANJA, CREMA = "#0A3D12", "#0A5F1B", "#CD6C1B", "#E8892F", "#F6F6C5"
F = lambda n, s: ImageFont.truetype(os.path.join(A, "fonts", n), s)
TMP = tempfile.mkdtemp(prefix="reel_")
BED = 108.0  # fuente: tramo final sin voz (solo base musical) para tarjetas

escudo = Image.open(os.path.join(A, "escudo.png")).convert("RGBA")

def top_band(im):
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 210], fill=VERDE_NOCHE)
    d.rectangle([0, 206, W, 212], fill=TERRACOTA)
    e = escudo.resize((140, 140), Image.LANCZOS); im.paste(e, (40, 36), e)
    d.text((210, 62), "Esc. N.º 4-012", font=F("OpenSans-ExtraBold.ttf", 40), fill=CREMA)
    d.text((210, 114), "Ing. Ricardo Videla", font=F("PlayfairDisplay-Bold.ttf", 36), fill="white")

def center(d, y, txt, font, fill):
    w = d.textlength(txt, font=font); d.text(((W - w) / 2, y), txt, font=font, fill=fill)

def pill(im, y, txt, size=52, fill="white", bg=VERDE_NOCHE, italic=False):
    d = ImageDraw.Draw(im)
    f = F("PlayfairDisplay-BoldItalic.ttf", size) if italic else F("OpenSans-ExtraBold.ttf", size)
    w = d.textlength(txt, font=f); pad = 36
    x0 = (W - w) / 2 - pad
    d.rounded_rectangle([x0, y, x0 + w + 2 * pad, y + size + 44], 26, fill=bg)
    d.text((x0 + pad, y + 14), txt, font=f, fill=fill)

def overlay(name, kind=None, text=None):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); top_band(im)
    if kind == "ficcion": pill(im, 1720, "Escena de ficción", 50, CREMA, "#0A3D12E6", True)
    if kind == "pill": pill(im, 1720, text, 54, "white", "#0A3D12E6")
    if kind == "pillN": pill(im, 1720, text, 54, NARANJA, "#0A3D12E6")
    if kind == "ayuda":
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([60, 1440, W - 60, 1800], 30, fill="#0A3D12F0")
        d.rectangle([60, 1440, W - 60, 1448], fill=TERRACOTA)
        center(d, 1476, "Hablá con un adulto de confianza", F("OpenSans-ExtraBold.ttf", 44), "white")
        center(d, 1544, "o con el equipo de orientación", F("OpenSans-ExtraBold.ttf", 44), "white")
        center(d, 1644, "Línea 102", F("PlayfairDisplay-Bold.ttf", 92), NARANJA)
    p = os.path.join(TMP, name + ".png"); im.save(p); return p

def card_title():
    im = Image.new("RGB", (W, H), VERDE_NOCHE); d = ImageDraw.Draw(im)
    e = escudo.resize((380, 380), Image.LANCZOS); im.paste(e, ((W - 380) // 2, 520), e)
    center(d, 960, "CIBERBULLYING", F("PlayfairDisplay-Bold.ttf", 104), CREMA)
    f = F("OpenSans-ExtraBold.ttf", 60); a, b = "Actuemos ", "a tiempo"
    w = d.textlength(a + b, font=f); x = (W - w) / 2
    d.text((x, 1110), a, font=f, fill="white"); d.text((x + d.textlength(a, font=f), 1110), b, font=f, fill=NARANJA)
    d.rectangle([(W - 240) // 2, 1210, (W + 240) // 2, 1216], fill=TERRACOTA)
    p = os.path.join(TMP, "title.png"); im.save(p); return p

def card_end():
    return os.path.join(A, "cierre_1080x1920.png")

def seg(i, start, dur, mode, zoom=1.0, ov=None, card=None):
    out = os.path.join(TMP, f"s{i:02d}.mp4")
    fade = f"afade=t=in:d=0.05,afade=t=out:st={max(dur-0.05,0):.2f}:d=0.05"
    a_start = BED if card else start
    base = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"]
    if card:
        cmd = base + ["-loop", "1", "-framerate", "30", "-t", f"{dur}", "-i", card,
                      "-ss", f"{a_start}", "-t", f"{dur}", "-i", SRC]
        fc = f"[0:v]format=yuv420p[v];[1:a]aresample=44100,aformat=channel_layouts=stereo,{fade}" + (
            f",afade=t=out:st={dur-1.5:.2f}:d=1.5" if card == card_end() else "") + "[a]"
    else:
        cmd = base + ["-f", "lavfi", "-t", f"{dur}", "-i", f"color=c={VERDE_NOCHE}:s={W}x{H}:r=30",
                      "-ss", f"{start}", "-t", f"{dur}", "-i", SRC,
                      "-loop", "1", "-framerate", "30", "-t", f"{dur}", "-i", ov]
        if mode == "crop":
            cw = int(810 / zoom) // 2 * 2; ch = int(1080 / zoom) // 2 * 2
            vf = f"[1:v]crop={cw}:{ch}:(iw-{cw})/2:({1080}-{ch})/2*0.6,scale=1080:1440:flags=lanczos,fps=30[vv];[0:v][vv]overlay=0:260"
        else:
            vf = "[1:v]scale=1080:608:flags=lanczos,fps=30[vv];[0:v][vv]overlay=0:656"
        fc = f"{vf}[b];[b][2:v]overlay=0:0,format=yuv420p[v];[1:a]aresample=44100,aformat=channel_layouts=stereo,{fade}[a]"
    cmd += ["-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-t", f"{dur}",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-ar", "44100", out]
    subprocess.run(cmd, check=True); return out

# Guion (ver marca.md): (inicio_fuente, duración, modo, zoom, overlay, tarjeta)
ov0 = overlay("top")
plan = [
    (85.5, 4.4, "crop", 1.0, ov0, None),                        # gancho
    (0, 2.2, None, 1, None, card_title()),                      # título
    (4.8, 5.0, "crop", 1.0, ov0, None),                         # presentación
    (13.8, 5.0, "crop", 1.0, ov0, None),                        # definición
    (19.8, 5.0, "crop", 1.15, ov0, None),
    (26.5, 4.5, "full", 1, overlay("fic", "ficcion"), None),    # escena B/N
    (37.0, 4.0, "crop", 1.0, ov0, None),                        # testimonio
    (45.5, 4.0, "full", 1, overlay("fic2", "ficcion"), None),   # escena B/N
    (62.8, 2.4, "full", 1, overlay("q", "pillN", "¿Qué podemos hacer?"), None),
    (68.7, 3.5, "crop", 1.0, overlay("p1", "pill", "No respondas · Guardá pruebas"), None),
    (72.2, 2.3, "crop", 1.15, overlay("p2", "pill", "Bloqueá"), None),
    (74.5, 5.2, "crop", 1.0, overlay("p3", "pill", "Pedí ayuda a un adulto"), None),
    (89.9, 2.0, "crop", 1.0, ov0, None),                        # cierre hablado
    (91.9, 4.0, "crop", 1.0, overlay("ay", "ayuda"), None),     # + vía de ayuda
    (0, 3.5, None, 1, None, card_end()),                        # escudo
]
files = [seg(i, *p) for i, p in enumerate(plan)]
cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"]
for f in files: cmd += ["-i", f]
n = len(files)
fc = "".join(f"[{i}:v][{i}:a]" for i in range(n)) + f"concat=n={n}:v=1:a=1[v][a0];[a0]loudnorm=I=-14:TP=-1.5:LRA=11[a]"
cmd += ["-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-movflags", "+faststart", OUT]
subprocess.run(cmd, check=True)
print("listo:", OUT)
