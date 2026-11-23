"""Rebuild the dannytsmith.com Adobe Muse site as static HTML from the .muse SQLite file."""
import sqlite3, re, html, os, struct, zlib, xml.etree.ElementTree as ET

SRC = r"C:/Users/uqdsmi34/OneDrive - The University of Queensland/uni_archive/uni_QCA_photo/Website"
DB = SRC + "/dannytsmithcom.muse"
OUT = SRC + "/site"
os.makedirs(OUT + "/images", exist_ok=True)

c = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
O = {u: (cl, ET.fromstring(x), b) for u, cl, x, b in c.execute("select uid,className,xmlData,blobData from active")}
el = lambda u: O[u][1]
HEADER = 121  # A-Master headerBottom; page items are offset by this


def kids(e):
    return [k.get("uid") for p in e.findall("PersistCollection") if p.get("id") == "children" for k in p]


def pos(e):
    m = e.find("MuseMatrix")
    return float(m.get("e")), float(m.get("f"))


def states(e):
    g = e.find("GraphicStyleDef")
    return {s.get("subStateName"): s.attrib for s in g.iter("state")} if g is not None else {}


def amf_bytes(b):
    # AMF3 ByteArray: 0x0c marker, U29 (len<<1|1), payload
    i, n = 1, 0
    for k in range(4):
        byte = b[i]; i += 1
        if k < 3:
            n = (n << 7) | (byte & 0x7F)
            if not byte & 0x80:
                break
        else:
            n = (n << 8) | byte
    return b[i:i + (n >> 1)]


def png(w, h, argb):
    rows = b"".join(b"\0" + b"".join(bytes((argb[j + 1], argb[j + 2], argb[j + 3], argb[j]))
                                     for j in range(r * w * 4, (r + 1) * w * 4, 4)) for r in range(h))
    chunk = lambda t, d: struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(rows, 9)) + chunk(b"IEND", b""))


_saved = {}


def image_for(item_uid):
    """ImageItem uid -> saved file name (via LinkInstance -> BaseLink -> LinkProxy blob)."""
    li = el(item_uid).get("linkInstance")
    base = el(li).get("parent")
    if base in _saved:
        return _saved[base]
    be = el(base)
    name = re.sub(r"[^\w.-]", "_", be.get("name"))
    proxies = [k.get("uid") for p in be.findall("PersistCollection") if p.get("id") == "proxies" for k in p]
    px = max(proxies, key=lambda u: len(O[u][2] or b""))
    data = amf_bytes(O[px][2])
    if data[:2] == b"\xff\xd8":
        name = os.path.splitext(name)[0] + ".jpg"
    elif data[:4] == b"\x89PNG":
        name = os.path.splitext(name)[0] + ".png"
    else:  # raw ARGB pixels
        pe = el(px)
        data = png(int(pe.get("width")), int(pe.get("height")), data)
        name = os.path.splitext(name)[0] + ".png"
    stem, ext = os.path.splitext(name); k = 1
    while name in _saved.values():
        name = f"{stem}_{k}{ext}"; k += 1
    open(f"{OUT}/images/{name}", "wb").write(data)
    _saved[base] = name
    return name


def frame_image(frame_uid):
    return image_for(next(k for k in kids(el(frame_uid)) if O[k][0] == "ImageItem"))


# page uid -> (siteNode uid, file)
PAGES = {"U63": "index.html", "U166": "photo.html", "U173": "video.html", "U180": "about.html",
         "U321": "varanassi.html", "U1383": "black-and-white.html"}
NODE2FILE = {el(p).get("siteNode"): f for p, f in PAGES.items()}
link = lambda url: NODE2FILE.get(url[5:], "#") if url and url.startswith("page:") else url


def abs_style(e, dx=0, dy=HEADER):
    x, y = pos(e)
    return f"left:{x + dx:g}px;top:{y + dy:g}px;width:{float(e.get('width')):g}px;height:{float(e.get('height')):g}px"


def textflow(e):
    tf = ET.fromstring(e.get("textModel"))
    ns = "{http://ns.adobe.com/textLayout/2008}"
    out = []
    for p in tf.iter(ns + "p"):
        inner = ""
        for node in p:
            spans = [node] if node.tag == ns + "span" else list(node)
            s = ""
            for sp in spans:
                t = html.escape(sp.text or "")
                if not t: continue
                if sp.get("fontStyle") == "italic": t = f"<em>{t}</em>"
                if sp.get("fontWeight") == "normal": t = f'<span style="font-weight:normal">{t}</span>'
                s += t
            if node.tag == ns + "a":
                s = f'<a href="{node.get("href")}" target="_blank" rel="noopener">{s}</a>'
            inner += s
        style = []
        if p.get("textAlign"): style.append(f"text-align:{p.get('textAlign')}")
        if p.get("fontWeight") == "bold": style.append("font-weight:bold")
        out.append(f'<p style="{";".join(style)}">{inner or "&nbsp;"}</p>')
    return "".join(out)


# ---------- master header / footer ----------
m = {k: el(k) for k in kids(el("U61"))}
logo = frame_image("U250")
nav = []
for r in ("U1848", "U1859", "U1870"):  # About, Photo, Video
    st = states(el(r))
    nav.append((link(st["*"]["hyperlinkURL"]), frame_image(st["*"]["background_ImageFrame"]),
                frame_image(st["rollover"]["background_ImageFrame"]), abs_style(el(r), dy=0)))
# The original footer held an email and phone number; the site links to contact.html instead.


def page(title, file, body, height, extra=""):
    navhtml = "".join(
        f'<a class="abs nav{" active" if f == file or (file in ("varanassi.html", "black-and-white.html") and f == "photo.html") else ""}" '
        f'href="{f}" style="{s}"><img class="n" src="images/{a}" alt=""><img class="r" src="images/{b}" alt=""></a>'
        for f, a, b, s in nav)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>{title}</title>
<meta name="viewport" content="width=960"><link rel="stylesheet" href="style.css"></head>
<body><div class="page" style="height:{height}px">
<a href="index.html" class="abs" style="{abs_style(m['U250'], dy=0)}"><img src="images/{logo}" alt="Danny Smith"></a>
{navhtml}
{body}
<div class="footer"><a href="contact.html">contact</a></div>
</div>{extra}</body></html>"""


def img_frame(u):
    e = el(u); st = states(e).get("*", {})
    tag = f'<img src="images/{frame_image(u)}" alt="">'
    if st.get("hyperlinkURL"):
        return f'<a class="abs" href="{link(st["hyperlinkURL"])}" style="{abs_style(e)}">{tag}</a>'
    return f'<div class="abs" style="{abs_style(e)}">{tag}</div>'


def text_frame(u, cls=""):
    e = el(u); st = states(e).get("*", {})
    t = textflow(e)
    if st.get("hyperlinkURL"):
        t = f'<a href="{link(st["hyperlinkURL"])}">{t}</a>'
    return f'<div class="abs text {cls}" style="{abs_style(e)};height:auto">{t}</div>'


def bottom(uids):
    return max(pos(el(u))[1] + float(el(u).get("height")) for u in uids) + HEADER


def build():
    files = {}
    # Home
    files["index.html"] = page("Home", "index.html", img_frame("U146"), bottom(["U146"]) + 70)
    # Photo
    files["photo.html"] = page("Photo", "photo.html",
                               img_frame("U296") + img_frame("U305") + text_frame("U346", "label") + text_frame("U348", "label"),
                               bottom(["U348"]) + 70)
    # Video
    vids = ""
    for u in ("U1821", "U1823"):
        e = el(u)
        vid = re.search(r'videoID" type="input" value="([^"]*)', ET.tostring(e, encoding="unicode")).group(1)
        vids += (f'<iframe class="abs" style="{abs_style(e)}" src="https://www.youtube-nocookie.com/embed/{vid}?rel=0&amp;modestbranding=1" '
                 f'frameborder="0" allowfullscreen></iframe>')
    files["video.html"] = page("Video", "video.html", vids, bottom(["U1823"]) + 70)
    # About
    files["about.html"] = page("About", "about.html", text_frame("U1819", "about"), bottom(["U1819"]) + 170)
    # Slideshows
    for pid, wid, title in (("U321", "U891", "Varanassi"), ("U1383", "U1388", "Black &amp; White")):
        w = el(wid); wx, wy = pos(w)
        panel = next(k for k in kids(w) if states(el(k)).get("*", {}).get("codegen_ClassName") == "SlideShowContentPanel")
        slides = [k for k in kids(el(panel)) if states(el(k)).get("*", {}).get("codegen_ClassName") == "SSSlide"]
        imgs = "".join(f'<img src="images/{frame_image(s)}" alt="">' for s in slides)
        pe = el(panel)
        body = (f'<div class="abs slideshow" style="{abs_style(pe, wx, wy + HEADER)}"><div class="track">{imgs}</div></div>'
                f'<div class="abs ssnav" style="left:{wx + pos(pe)[0]:g}px;top:{wy + HEADER + pos(pe)[1] + float(pe.get("height")) + 12:g}px;width:{float(pe.get("width")):g}px">'
                f'<button class="prev" aria-label="Previous">&lt;</button><span class="count"></span><button class="next" aria-label="Next">&gt;</button></div>')
        f = PAGES[pid]
        files[f] = page(title, f, body, wy + HEADER + pos(pe)[1] + float(pe.get("height")) + 110, "<script src=\"slideshow.js\"></script>")
    for f, s in files.items():
        open(f"{OUT}/{f}", "w", encoding="utf-8").write(s)
    print("wrote", list(files), len(_saved), "images")


build()
