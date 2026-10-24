import math, os, random

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets')
os.makedirs(OUT, exist_ok=True)

C = dict(panel='#0a1120', panel2='#0d1830', line='#1a2a47', cyan='#22d3ee', blue='#3b82f6',
         violet='#8b5cf6', pink='#f43f9d', green='#34d399', amber='#fbbf24',
         text='#e8f0fb', mute='#8ba3c4', dim='#4b6385')
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono','Courier New',monospace"
SANS = "'Segoe UI',system-ui,-apple-system,Roboto,Helvetica,Arial,sans-serif"


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def rr(x, y, w, h, r):
    return (f"M{x+r},{y} H{x+w-r} A{r},{r} 0 0 1 {x+w},{y+r} V{y+h-r} A{r},{r} 0 0 1 {x+w-r},{y+h} "
            f"H{x+r} A{r},{r} 0 0 1 {x},{y+h-r} V{y+r} A{r},{r} 0 0 1 {x+r},{y} Z")


def defs(c1=C['cyan'], c2=C['violet'], c3=C['pink']):
    return f'''<defs>
<linearGradient id="edge" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{c1}"/><stop offset=".5" stop-color="{c2}"/><stop offset="1" stop-color="{c3}"/></linearGradient>
<linearGradient id="edge2" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{c3}"/><stop offset=".5" stop-color="{c2}"/><stop offset="1" stop-color="{c1}"/></linearGradient>
<linearGradient id="panel" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0c1629"/><stop offset="1" stop-color="#060b17"/></linearGradient>
<filter id="glow" x="-150%" y="-150%" width="400%" height="400%"><feGaussianBlur stdDeviation="2.6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M24 0H0V24" fill="none" stroke="#1a2a47" stroke-width=".6" opacity=".6"/></pattern>
</defs>'''


def svg(w, h, body, label, extra_defs=''):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{esc(label)}">{defs()}{extra_defs}{body}</svg>')


def electron(path, dur, begin=0, r=3.4, fill='#ffffff'):
    return (f'<circle r="{r}" fill="{fill}" filter="url(#glow)"><animateMotion dur="{dur}s" repeatCount="indefinite" '
            f'begin="{begin}s" path="{path}"/></circle>')


def traces(w, h, bl=False):
    """moving-dot circuit traces (electrons flowing) in the corners"""
    t = []
    specs = [
        (f"M{w-250},20 H{w-130} L{w-116},34 H{w-40}", C['cyan'], 1.4),
        (f"M{w-190},40 H{w-100} L{w-88},52 H{w-28}", C['violet'], 1.9),
        (f"M{w-130},62 H{w-60} L{w-50},72 H{w-18}", C['pink'], 1.6),
    ]
    if bl:
        specs += [(f"M20,{h-20} H120 L134,{h-34} H230", C['violet'], 1.7),
                  (f"M20,{h-42} H70 L82,{h-54} H150", C['cyan'], 2.1)]
    for d, col, dur in specs:
        t.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="1.3" stroke-dasharray="2 10" opacity=".75" stroke-linecap="round">'
                 f'<animate attributeName="stroke-dashoffset" from="0" to="-48" dur="{dur}s" repeatCount="indefinite"/></path>')
    return ''.join(t)


def frame(w, h, dur=9, r=20, uid='a', bl=False):
    p = rr(1.5, 1.5, w - 3, h - 3, r)
    return (f'<clipPath id="clip{uid}"><path d="{p}"/></clipPath>'
            f'<path d="{p}" fill="url(#panel)" stroke="{C["line"]}" stroke-width="1.2"/>'
            f'<g clip-path="url(#clip{uid})"><rect width="{w}" height="{h}" fill="url(#grid)" opacity=".55"/>{traces(w, h, bl)}</g>'
            f'<path d="{p}" fill="none" stroke="url(#edge)" stroke-width="2.4" stroke-linecap="round" pathLength="1000" '
            f'stroke-dasharray="130 870" filter="url(#glow)"><animate attributeName="stroke-dashoffset" from="0" to="-1000" dur="{dur}s" repeatCount="indefinite"/></path>'
            f'<path d="{p}" fill="none" stroke="url(#edge2)" stroke-width="2.4" stroke-linecap="round" pathLength="1000" '
            f'stroke-dasharray="130 870" filter="url(#glow)"><animate attributeName="stroke-dashoffset" from="-500" to="-1500" dur="{dur}s" repeatCount="indefinite"/></path>'
            + electron(p, dur, -0.13 * dur) + electron(p, dur, -0.63 * dur, fill=C['cyan']))


def chip(x, y, label, color=C['cyan']):
    cx = x + (len(label) + 3) * 9.9 + 2
    return (f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="13" font-weight="700" fill="{color}" letter-spacing="1.5">// {label}</text>'
            f'<rect x="{cx}" y="{y-12}" width="8" height="15" fill="{color}"><animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.5;1" dur="1.1s" repeatCount="indefinite"/></rect>')


def window_dots(w):
    return ''.join(f'<circle cx="{w-70+i*18}" cy="34" r="5" fill="{c}" opacity=".85"/>' for i, c in enumerate([C['pink'], C['amber'], C['green']]))


def appear(i, total=18.0, start=0.8, step=0.9, dx=-16):
    s = (start + i * step) / total
    kt = f"0;{s:.4f};{s+0.025:.4f};0.92;0.965;1"
    return (f'<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="{kt}" dur="{total}s" repeatCount="indefinite"/>'
            f'<animateTransform attributeName="transform" type="translate" values="{dx} 0;{dx} 0;0 0;0 0;0 0;0 0" keyTimes="{kt}" dur="{total}s" repeatCount="indefinite"/>')


def write(name, content):
    with open(os.path.join(OUT, name), 'w', encoding='utf-8') as f:
        f.write(content)
    print(name, len(content) // 1024, 'KB')


# ───────────────────────── BANNER ─────────────────────────
def banner():
    w, h = 860, 300
    rnd = random.Random(7)
    parts = [frame(w, h, dur=10, r=24, uid='b', bl=True)]
    # floating particles
    for _ in range(18):
        x = rnd.randint(30, 830); y = rnd.randint(150, 285); d = rnd.uniform(6, 11)
        col = rnd.choice([C['cyan'], C['violet'], C['pink']])
        parts.append(f'<circle cx="{x}" cy="{y}" r="{rnd.choice([1,1.4,1.8])}" fill="{col}" opacity="0">'
                     f'<animate attributeName="cy" from="{y}" to="{y-90}" dur="{d:.1f}s" begin="-{rnd.uniform(0,d):.1f}s" repeatCount="indefinite"/>'
                     f'<animate attributeName="opacity" values="0;.9;0" dur="{d:.1f}s" begin="-{rnd.uniform(0,d):.1f}s" repeatCount="indefinite"/></circle>')
    parts.append(window_dots(w))
    parts.append(f'<text x="48" y="74" font-family="{MONO}" font-size="14" fill="{C["cyan"]}" letter-spacing="1">&gt; hello_world.exe</text>')
    grad = (f'<linearGradient id="nameg" gradientUnits="userSpaceOnUse" x1="48" y1="0" x2="548" y2="0" spreadMethod="reflect">'
            f'<stop offset="0" stop-color="{C["cyan"]}"/><stop offset=".5" stop-color="{C["violet"]}"/><stop offset="1" stop-color="{C["pink"]}"/>'
            f'<animateTransform attributeName="gradientTransform" type="translate" from="0 0" to="1000 0" dur="9s" repeatCount="indefinite"/></linearGradient>')
    parts.append(f'<text x="48" y="136" font-family="{SANS}" font-size="44" font-weight="800" fill="url(#nameg)">Muhammad Abdullah</text>')
    roles = ["AI Engineer  ·  Automation & Agents", "Full-Stack Web Developer", "Learning AI  ·  ML  ·  LLMs", "Digital Marketing & Growth"]
    n = len(roles)
    for i, role in enumerate(roles):
        a = i / n; b = (i + 1) / n
        kt = f"0;{a:.3f};{a+0.02:.3f};{b-0.03:.3f};{b:.3f};1" if i else f"0;0.001;0.02;{b-0.03:.3f};{b:.3f};1"
        vals = "0;0;1;1;0;0" if i else "1;1;1;1;0;0"
        parts.append(f'<text x="48" y="186" font-family="{MONO}" font-size="22" font-weight="600" fill="{C["text"]}" opacity="0">'
                     f'<tspan fill="{C["cyan"]}">&gt; </tspan>{esc(role)}'
                     f'<animate attributeName="opacity" values="{vals}" keyTimes="{kt}" dur="14s" repeatCount="indefinite"/></text>')
    parts.append(f'<text x="48" y="226" font-family="{SANS}" font-size="14.5" fill="{C["mute"]}">Intelligent systems · automations · web products</text>')
    parts.append(f'<circle cx="54" cy="259" r="5" fill="{C["green"]}" filter="url(#glow)"><animate attributeName="r" values="4;6;4" dur="1.8s" repeatCount="indefinite"/></circle>'
                 f'<text x="70" y="263" font-family="{MONO}" font-size="12.5" font-weight="700" fill="{C["green"]}" letter-spacing="1.5">OPEN TO OPPORTUNITIES</text>')
    # atom
    ax, ay = 728, 152
    parts.append(f'<g transform="translate({ax},{ay})">')
    parts.append(f'<circle r="92" fill="none" stroke="{C["line"]}" stroke-width="1.2" stroke-dasharray="2 8"><animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="50s" repeatCount="indefinite"/></circle>')
    ell = "M-104,0 A104,38 0 1,1 104,0 A104,38 0 1,1 -104,0 Z"
    for ang, col, dur in [(0, C['cyan'], 4.2), (60, C['violet'], 5.4), (120, C['pink'], 6.6)]:
        parts.append(f'<g transform="rotate({ang})"><ellipse rx="104" ry="38" fill="none" stroke="{col}" stroke-width="1.3" opacity=".55"/>'
                     + electron(ell, dur, 0, 4.2, col) + electron(ell, dur, -dur / 2, 3, '#ffffff') + '</g>')
    parts.append(f'<circle r="20" fill="{C["violet"]}" opacity=".18"><animate attributeName="r" values="18;30;18" dur="3s" repeatCount="indefinite"/><animate attributeName="opacity" values=".3;0;.3" dur="3s" repeatCount="indefinite"/></circle>')
    parts.append(f'<circle r="15" fill="url(#nuc)" filter="url(#glow)"><animate attributeName="r" values="14;17;14" dur="2.2s" repeatCount="indefinite"/></circle>'
                 f'<text y="3.8" text-anchor="middle" font-family="{MONO}" font-size="10" font-weight="800" fill="#06101f">AI</text></g>')
    nuc = f'<radialGradient id="nuc"><stop offset="0" stop-color="#ffffff"/><stop offset=".5" stop-color="{C["cyan"]}"/><stop offset="1" stop-color="{C["violet"]}"/></radialGradient>'
    write('banner.svg', svg(w, h, ''.join(parts), 'Muhammad Abdullah — AI Engineer, Automation and Agents, Full-Stack Developer', grad + nuc))


# ───────────────────────── ABOUT ─────────────────────────
def about():
    w, h = 860, 300
    p = [frame(w, h, dur=9, uid='ab'), chip(32, 44, 'ABOUT_ME'), window_dots(w)]
    rows = [
        ('$ whoami', C['cyan'], 'muhammad_abdullah  //  AI · Automation · Full-Stack'),
        ('[NOW]', C['green'], 'Building Inkline: an AI Invoice & Expense Manager'),
        ('[LEARNING]', C['violet'], 'Artificial Intelligence, Machine Learning, LLMs & agent frameworks'),
        ('[COLLAB]', C['blue'], 'Open to working on Explore Pakistan and other AI / web projects'),
        ('[ASK ME]', C['pink'], 'AI automation · AI agents · web development · digital marketing'),
        ('[FUN FACT]', C['amber'], 'I stay calm and deliver my best work under pressure'),
    ]
    y = 96
    for i, (tag, col, txt) in enumerate(rows):
        p.append(f'<g>{appear(i)}<text x="40" y="{y}" font-family="{MONO}" font-size="14.5" font-weight="700" fill="{col}">{esc(tag)}</text>'
                 f'<text x="162" y="{y}" font-family="{MONO}" font-size="14.5" fill="{C["text"]}">{esc(txt)}</text></g>')
        y += 34
    p.append(f'<rect x="162" y="{y-34-13}" width="9" height="17" fill="{C["amber"]}" opacity="0">'
             f'<animate attributeName="opacity" values="0;0;1;0;1;0;1;0;0" keyTimes="0;.33;.34;.40;.46;.52;.58;.64;1" dur="18s" repeatCount="indefinite"/></rect>')
    write('about.svg', svg(w, h, ''.join(p), 'About me'))


# ───────────────────────── PROJECT CARDS ─────────────────────────
def wrap_chips(items, x0, y0, maxw, col):
    out, x, y = [], x0, y0
    for t in items:
        cw = len(t) * 6.7 + 18
        if x + cw > x0 + maxw:
            x = x0; y += 28
        out.append(f'<rect x="{x}" y="{y}" width="{cw:.0f}" height="21" rx="10.5" fill="{C["panel2"]}" stroke="{col}" stroke-opacity=".6"/>'
                   f'<text x="{x+cw/2:.0f}" y="{y+14.5}" text-anchor="middle" font-family="{MONO}" font-size="10.5" fill="{C["text"]}">{esc(t)}</text>')
        x += cw + 8
    return ''.join(out)


def project(name, idx, title, sub, desc, chips, link, viz, c1, c2, c3):
    w, h = 424, 376
    d = defs(c1, c2, c3).replace('<defs>', '<defs>', 1)
    body = [frame(w, h, dur=8 + idx, r=20, uid='p' + str(idx)), chip(26, 40, f'PROJECT_0{idx}', c1)]
    body.append(f'<text x="26" y="82" font-family="{SANS}" font-size="23" font-weight="800" fill="{C["text"]}">{esc(title)}</text>')
    body.append(f'<text x="26" y="104" font-family="{MONO}" font-size="12" fill="{c1}">{esc(sub)}</text>')
    for i, line in enumerate(desc):
        body.append(f'<text x="26" y="{136+i*20}" font-family="{SANS}" font-size="13" fill="{C["mute"]}">{esc(line)}</text>')
    body.append(viz)
    body.append(wrap_chips(chips, 26, 286, 372, c1))
    body.append(f'<text x="26" y="358" font-family="{MONO}" font-size="11.5" fill="{c1}">{esc(link)}</text>')
    s = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(title)}">'
         f'{defs(c1, c2, c3)}<defs><linearGradient id="bar" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c3}"/></linearGradient></defs>{"".join(body)}</svg>')
    write(name, s)


def viz_rag(c1, c2, c3):
    cx = [58, 135, 212, 289, 366]; y = 232
    labels = ['query', 'embed', 'qdrant', 'LLM', 'answer']
    cols = [c1, c2, c3, c2, c1]
    p = [f'<text x="26" y="200" font-family="{MONO}" font-size="10.5" fill="{C["dim"]}" letter-spacing="1">RAG PIPELINE</text>',
         f'<path d="M58,{y} H366" stroke="{C["line"]}" stroke-width="2"/>',
         f'<path d="M58,{y} H366" stroke="{c1}" stroke-width="1.6" stroke-dasharray="3 9" opacity=".9"><animate attributeName="stroke-dashoffset" from="0" to="-48" dur="1.6s" repeatCount="indefinite"/></path>']
    for b in (0, -1.07, -2.13):
        p.append(electron(f"M58,{y} H366", 3.2, b, 3.6, '#ffffff'))
    for i, (x, lb, col) in enumerate(zip(cx, labels, cols)):
        p.append(f'<rect x="{x-31}" y="{y-16}" width="62" height="32" rx="9" fill="#0d1830" stroke="{col}" stroke-width="1.4" stroke-opacity=".45">'
                 f'<animate attributeName="stroke-opacity" values=".45;1;.45;.45" keyTimes="0;.12;.3;1" dur="3.2s" begin="{i*0.64:.2f}s" repeatCount="indefinite"/></rect>'
                 f'<text x="{x}" y="{y+4}" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{C["text"]}">{lb}</text>')
    return ''.join(p)


def viz_bars(c1, c2, c3):
    base = 262; hs = [22, 34, 26, 44, 32, 52, 40, 58, 48]
    p = [f'<text x="26" y="200" font-family="{MONO}" font-size="10.5" fill="{C["dim"]}" letter-spacing="1">INVOICES · EXPENSES · INSIGHTS</text>',
         f'<path d="M26,{base+2} H398" stroke="{C["line"]}" stroke-width="1.4"/>']
    pts = []
    for i, hh in enumerate(hs):
        x = 34 + i * 40
        p.append(f'<rect x="{x}" y="{base-hh}" width="24" height="{hh}" rx="4" fill="url(#bar)" opacity=".85">'
                 f'<animate attributeName="height" values="{hh};{hh*0.35:.0f};{hh};{hh}" keyTimes="0;.4;.7;1" dur="4s" begin="-{i*0.37:.2f}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="y" values="{base-hh};{base-hh*0.35:.0f};{base-hh};{base-hh}" keyTimes="0;.4;.7;1" dur="4s" begin="-{i*0.37:.2f}s" repeatCount="indefinite"/></rect>')
        pts.append((x + 12, base - hh - 12))
    d = f"M{pts[0][0]},{pts[0][1]} " + ' '.join(f"L{x},{y}" for x, y in pts[1:])
    p.append(f'<path d="{d}" fill="none" stroke="#ffffff" stroke-width="1.8" stroke-linejoin="round" stroke-linecap="round" opacity=".9" pathLength="1000" stroke-dasharray="1000">'
             f'<animate attributeName="stroke-dashoffset" values="1000;0;0;1000" keyTimes="0;.5;.9;1" dur="5s" repeatCount="indefinite"/></path>')
    p.append(electron(d, 5, 0, 3.8, c1))
    return ''.join(p)


def projects():
    project('project-explore.svg', 1, 'Explore Pakistan', 'Travel guide + RAG chatbot',
            ['Travel guide to northern Pakistan: routes, seasons', 'and altitudes for six destinations, plus a RAG', "chatbot that answers from the site's own content."],
            ['Next.js', 'TypeScript', 'Tailwind', 'FastAPI', 'OpenAI', 'Qdrant'],
            'live → explore-pakistan-gules.vercel.app', viz_rag(C['cyan'], C['blue'], C['violet']), C['cyan'], C['blue'], C['violet'])
    project('project-inkline.svg', 2, 'Inkline', 'AI Invoice & Expense Manager',
            ['Invoicing & expense tracker with an AI layer that', 'auto-categorizes spending and surfaces insights', 'like overdue invoices and spending spikes.'],
            ['Python', 'Flask', 'SQLite', 'Chart.js', 'JavaScript'],
            'github → Ai-Invoice-And-Expenses-Manager', viz_bars(C['violet'], C['pink'], C['pink']), C['violet'], C['pink'], C['pink'])


# ───────────────────────── SKILLS (orbits) ─────────────────────────
def pill(label, col, w=None):
    w = w or len(label) * 6.4 + 16
    return (f'<rect x="{-w/2:.1f}" y="-11" width="{w:.1f}" height="22" rx="11" fill="{C["panel2"]}" stroke="{col}" stroke-width="1.3"/>'
            f'<text y="3.8" text-anchor="middle" font-family="{MONO}" font-size="10.5" font-weight="600" fill="{C["text"]}">{esc(label)}</text>')


def ring(cx, cy, r, items, col, dur, direction=1, phase=0):
    n = len(items)
    f, t = (0, 360) if direction > 0 else (360, 0)
    fl, tl = (0, -360) if direction > 0 else (-360, 0)
    g = [f'<g><animateTransform attributeName="transform" type="rotate" from="{f} {cx} {cy}" to="{t} {cx} {cy}" dur="{dur}s" repeatCount="indefinite"/>']
    for i, it in enumerate(items):
        a = phase + 2 * math.pi * i / n
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        g.append(f'<g transform="translate({x:.1f},{y:.1f})"><g><animateTransform attributeName="transform" type="rotate" from="{fl}" to="{tl}" dur="{dur}s" repeatCount="indefinite"/>{pill(it, col)}</g></g>')
    g.append('</g>')
    return ''.join(g)


def skills():
    w, h = 860, 524
    cx, cy = 588, 262
    p = [frame(w, h, dur=12, uid='sk'), chip(32, 44, 'TECH_STACK')]
    rings = [(96, ['Python', 'PyTorch', 'TensorFlow', 'OpenCV', 'pandas', 'scikit-learn'], C['cyan'], 70, 1, 0.3),
             (160, ['HTML', 'CSS', 'JavaScript', 'TypeScript', 'React', 'Next.js', 'Tailwind', 'Node.js', 'Flask'], C['violet'], 100, -1, 0.0),
             (224, ['PostgreSQL', 'SQLite', 'Git', 'Figma', 'Chart.js', 'Zapier', 'Docker'], C['pink'], 130, 1, 0.5)]
    for r, items, col, dur, dr, ph in rings:
        p.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{col}" stroke-width="1.1" stroke-dasharray="3 7" opacity=".45"/>')
    for r, items, col, dur, dr, ph in rings:
        circ = f"M{cx+r},{cy} A{r},{r} 0 1 1 {cx-r},{cy} A{r},{r} 0 1 1 {cx+r},{cy}"
        p.append(electron(circ, dur / 6, 0, 3.4, col) + electron(circ, dur / 6, -dur / 12, 2.6, '#ffffff'))
    for r, items, col, dur, dr, ph in rings:
        p.append(ring(cx, cy, r, items, col, dur, dr, ph))
    for k in range(3):
        p.append(f'<circle cx="{cx}" cy="{cy}" r="30" fill="none" stroke="{C["cyan"]}" stroke-width="1.4" opacity="0">'
                 f'<animate attributeName="r" values="30;74" dur="4.5s" begin="-{k*1.5}s" repeatCount="indefinite"/><animate attributeName="opacity" values=".6;0" dur="4.5s" begin="-{k*1.5}s" repeatCount="indefinite"/></circle>')
    p.append(f'<circle cx="{cx}" cy="{cy}" r="30" fill="url(#nuc)" filter="url(#glow)"><animate attributeName="r" values="28;33;28" dur="2.6s" repeatCount="indefinite"/></circle>'
             f'<text x="{cx}" y="{cy+6}" text-anchor="middle" font-family="{MONO}" font-size="17" font-weight="800" fill="#06101f">AI</text>')
    # legend
    ly = 100
    for col, title, sub in [(C['cyan'], 'AI / ML CORE', 'Python · PyTorch · TensorFlow'), (C['violet'], 'WEB DEVELOPMENT', 'Next.js · React · Flask · FastAPI'), (C['pink'], 'DATA · TOOLS · AUTOMATION', 'Postgres · Git · Zapier · n8n')]:
        p.append(f'<circle cx="46" cy="{ly}" r="6" fill="{col}" filter="url(#glow)"/>'
                 f'<text x="64" y="{ly+4}" font-family="{MONO}" font-size="12" font-weight="700" fill="{col}" letter-spacing="1">{title}</text>'
                 f'<text x="64" y="{ly+24}" font-family="{SANS}" font-size="12.5" fill="{C["mute"]}">{esc(sub)}</text>')
        ly += 70
    p.append(f'<text x="40" y="{h-34}" font-family="{MONO}" font-size="11.5" fill="{C["dim"]}">rings rotate · electrons orbit · always learning</text>')
    nuc = f'<radialGradient id="nuc"><stop offset="0" stop-color="#ffffff"/><stop offset=".5" stop-color="{C["cyan"]}"/><stop offset="1" stop-color="{C["violet"]}"/></radialGradient>'
    write('skills.svg', svg(w, h, ''.join(p), 'Tech stack orbit: AI and ML, web development, data and tools', nuc))


# ───────────────────────── SERVICES ─────────────────────────
def services():
    w, h = 860, 262
    p = [frame(w, h, dur=10, uid='sv'), chip(32, 44, 'WHAT_I_BUILD')]
    cols = [143, 430, 717]
    for x in (287, 573):
        p.append(f'<path d="M{x},84 V226" stroke="{C["line"]}" stroke-width="1.2" stroke-dasharray="3 6"/>')
    # 1: agent network
    x = cols[0]; y = 118
    nodes = [(x, y - 30), (x - 30, y + 20), (x + 30, y + 20)]
    p.append(f'<g>' + ''.join(f'<path d="M{x},{y} L{nx},{ny}" stroke="{C["cyan"]}" stroke-width="1.4" opacity=".6"/>' for nx, ny in nodes)
             + f'<path d="M{nodes[0][0]},{nodes[0][1]} L{nodes[1][0]},{nodes[1][1]} L{nodes[2][0]},{nodes[2][1]} Z" fill="none" stroke="{C["violet"]}" stroke-width="1.2" opacity=".5"/>'
             + ''.join(f'<circle cx="{nx}" cy="{ny}" r="6" fill="{C["panel2"]}" stroke="{C["cyan"]}" stroke-width="1.6"/>' for nx, ny in nodes)
             + f'<circle cx="{x}" cy="{y}" r="9" fill="{C["cyan"]}" filter="url(#glow)"><animate attributeName="r" values="8;11;8" dur="2s" repeatCount="indefinite"/></circle>'
             + electron(f"M{nodes[0][0]},{nodes[0][1]} L{nodes[1][0]},{nodes[1][1]} L{nodes[2][0]},{nodes[2][1]} Z", 3.2, 0, 3.2)
             + electron(f"M{x},{y} L{nodes[0][0]},{nodes[0][1]} L{x},{y} L{nodes[1][0]},{nodes[1][1]} L{x},{y} L{nodes[2][0]},{nodes[2][1]} Z", 4.5, 0, 2.8, C['cyan']) + '</g>')
    # 2: code brackets
    x = cols[1]; y = 118
    for d, col in [(f"M{x-24},{y-26} L{x-50},{y} L{x-24},{y+26}", C['violet']), (f"M{x+24},{y-26} L{x+50},{y} L{x+24},{y+26}", C['violet']), (f"M{x+9},{y-32} L{x-9},{y+32}", C['cyan'])]:
        p.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" pathLength="100" stroke-dasharray="100" filter="url(#glow)">'
                 f'<animate attributeName="stroke-dashoffset" values="100;0;0;100" keyTimes="0;.35;.8;1" dur="4s" repeatCount="indefinite"/></path>')
    # 3: growth
    x = cols[2]; y = 150
    for i, hh in enumerate([22, 38, 54, 72]):
        bx = x - 46 + i * 26
        p.append(f'<rect x="{bx}" y="{y-hh}" width="16" height="{hh}" rx="3" fill="{C["pink"]}" opacity=".8">'
                 f'<animate attributeName="height" values="0;{hh};{hh};0" keyTimes="0;.4;.85;1" dur="4s" begin="{i*0.15}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="y" values="{y};{y-hh};{y-hh};{y}" keyTimes="0;.4;.85;1" dur="4s" begin="{i*0.15}s" repeatCount="indefinite"/></rect>')
    arrow = f"M{x-52},{y-30} L{x-26},{y-48} L{x},{y-62} L{x+30},{y-84}"
    p.append(f'<path d="{arrow}" fill="none" stroke="#ffffff" stroke-width="2.2" stroke-linecap="round" pathLength="100" stroke-dasharray="100" filter="url(#glow)"><animate attributeName="stroke-dashoffset" values="100;0;0;100" keyTimes="0;.5;.85;1" dur="4s" repeatCount="indefinite"/></path>'
             + electron(arrow, 4, 0, 3.4, C['cyan']))
    titles = [('AI Agents & Automation', ['Custom AI agents, RAG chatbots and', 'workflow automation that saves hours.'], C['cyan']),
              ('Web Development', ['Fast, responsive Next.js, React and', 'Flask applications built end to end.'], C['violet']),
              ('Digital Marketing', ['Social media growth, content strategy', 'and campaigns that convert.'], C['pink'])]
    for cxx, (t, ls, col) in zip(cols, titles):
        p.append(f'<text x="{cxx}" y="196" text-anchor="middle" font-family="{SANS}" font-size="17.5" font-weight="800" fill="{col}">{esc(t)}</text>')
        for i, l in enumerate(ls):
            p.append(f'<text x="{cxx}" y="{218+i*18}" text-anchor="middle" font-family="{SANS}" font-size="12.5" fill="{C["mute"]}">{esc(l)}</text>')
    write('services.svg', svg(w, h, ''.join(p), 'Services: AI agents and automation, web development, digital marketing'))


# ───────────────────────── CONNECT ─────────────────────────
def connect():
    w, h = 860, 190
    p = [frame(w, h, dur=8, uid='cn', bl=True), chip(32, 44, 'LETS_CONNECT')]
    for k in range(3):
        p.append(f'<circle cx="76" cy="112" r="10" fill="none" stroke="{C["green"]}" stroke-width="1.6" opacity="0">'
                 f'<animate attributeName="r" values="10;42" dur="3s" begin="-{k}s" repeatCount="indefinite"/><animate attributeName="opacity" values=".8;0" dur="3s" begin="-{k}s" repeatCount="indefinite"/></circle>')
    p.append(f'<circle cx="76" cy="112" r="10" fill="{C["green"]}" filter="url(#glow)"/>')
    p.append(f'<text x="140" y="92" font-family="{MONO}" font-size="13" font-weight="700" fill="{C["green"]}" letter-spacing="2">OPEN TO OPPORTUNITIES</text>')
    p.append(f'<text x="140" y="130" font-family="{SANS}" font-size="29" font-weight="800" fill="url(#nameg)">Let’s build something intelligent.</text>')
    p.append(f'<text x="140" y="160" font-family="{SANS}" font-size="14" fill="{C["mute"]}">Full-time roles · internships · freelance projects in AI, automation &amp; full-stack.</text>')
    grad = (f'<linearGradient id="nameg" gradientUnits="userSpaceOnUse" x1="140" y1="0" x2="540" y2="0" spreadMethod="reflect">'
            f'<stop offset="0" stop-color="{C["cyan"]}"/><stop offset=".5" stop-color="{C["violet"]}"/><stop offset="1" stop-color="{C["pink"]}"/>'
            f'<animateTransform attributeName="gradientTransform" type="translate" from="0 0" to="800 0" dur="8s" repeatCount="indefinite"/></linearGradient>')
    write('connect.svg', svg(w, h, ''.join(p), 'Open to opportunities', grad))


# ───────────────────────── DIVIDER ─────────────────────────
def divider():
    w, h = 860, 28
    g = (f'<linearGradient id="fade" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{C["cyan"]}" stop-opacity="0"/><stop offset=".2" stop-color="{C["cyan"]}"/>'
         f'<stop offset=".5" stop-color="{C["violet"]}"/><stop offset=".8" stop-color="{C["pink"]}"/><stop offset="1" stop-color="{C["pink"]}" stop-opacity="0"/></linearGradient>')
    p = [f'<path d="M0,14 H860" stroke="url(#fade)" stroke-width="2"/>',
         f'<path d="M0,14 H860" stroke="#ffffff" stroke-width="1.4" stroke-dasharray="2 14" opacity=".7"><animate attributeName="stroke-dashoffset" from="0" to="-64" dur="2.4s" repeatCount="indefinite"/></path>']
    for x in (215, 430, 645):
        p.append(f'<circle cx="{x}" cy="14" r="5" fill="#060b17" stroke="{C["violet"]}" stroke-width="1.6"><animate attributeName="r" values="4;6.5;4" dur="2.4s" begin="{(x-215)/215*0.6}s" repeatCount="indefinite"/></circle>')
    p.append(electron("M0,14 H860", 4.5, 0, 3.8, C['cyan']) + electron("M0,14 H860", 4.5, -2.25, 3, '#ffffff'))
    write('divider.svg', svg(w, h, ''.join(p), 'divider', g))


# ───────────────────────── FOOTER ─────────────────────────
def wave(base, amp, period, w, y2):
    segs = int(math.ceil((w + period) / (period / 2))) + 2
    d = f"M0,{base} Q{period/4},{base-amp} {period/2},{base}"
    for i in range(2, segs + 1):
        d += f" T{period/2*i:.1f},{base}"
    return d + f" L{period/2*segs:.1f},{y2} L0,{y2} Z"


def footer():
    w, h = 860, 150
    g = (f'<linearGradient id="wg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{C["cyan"]}"/><stop offset=".5" stop-color="{C["violet"]}"/><stop offset="1" stop-color="{C["pink"]}"/></linearGradient>')
    p = [f'<clipPath id="fc"><rect width="{w}" height="{h}" rx="20"/></clipPath><g clip-path="url(#fc)"><rect width="{w}" height="{h}" fill="#060b17"/>']
    for base, amp, per, dur, op in [(86, 16, 430, 9, .28), (100, 13, 310, 6.5, .4), (114, 10, 240, 4.5, .65)]:
        p.append(f'<path d="{wave(base, amp, per, w, h)}" fill="url(#wg)" opacity="{op}"><animateTransform attributeName="transform" type="translate" from="0 0" to="-{per} 0" dur="{dur}s" repeatCount="indefinite"/></path>')
    p.append(f'<text x="430" y="54" text-anchor="middle" font-family="{MONO}" font-size="13.5" fill="{C["text"]}" letter-spacing="1">thanks for stopping by <tspan fill="{C["cyan"]}">·</tspan> let’s build something</text>')
    p.append(electron("M40,30 H820", 6, 0, 3, C['cyan']))
    p.append('</g>')
    write('footer.svg', svg(w, h, ''.join(p), 'footer', g))


if __name__ == '__main__':
    banner(); about(); projects(); skills(); services(); connect(); divider(); footer()
