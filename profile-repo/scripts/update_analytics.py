#!/usr/bin/env python3
"""
Builds assets/analytics.svg: an animated GitHub analytics card from REAL data.

No third-party image services, no personal token. It uses:
  - the public GitHub REST API (repos, stars, followers, languages)
  - the public contribution calendar HTML that GitHub serves for every profile
Python standard library only.

Usage:
  python scripts/update_analytics.py                 # live data
  python scripts/update_analytics.py --placeholder   # "syncing" state, no network
"""
import argparse, datetime as dt, json, math, os, re, sys, urllib.request

USER_DEFAULT = "M-Abdullah-Prog"
C = dict(panel2='#0d1830', line='#1a2a47', cyan='#22d3ee', blue='#3b82f6', violet='#8b5cf6', pink='#f43f9d',
         green='#34d399', amber='#fbbf24', text='#e8f0fb', mute='#8ba3c4', dim='#4b6385')
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono','Courier New',monospace"
SANS = "'Segoe UI',system-ui,-apple-system,Roboto,Helvetica,Arial,sans-serif"
LEVELS = ['#0f1a2e', '#0b4a63', '#0e7490', '#22d3ee', '#a5f3fc']
LANG_COLORS = [C['cyan'], C['violet'], C['pink'], C['blue'], C['green'], C['amber']]


# ───────────────────────── data ─────────────────────────
def http_get(url, headers=None):
    h = {'User-Agent': 'profile-analytics-script'}
    h.update(headers or {})
    with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=40) as r:
        return r.read().decode('utf-8', 'replace')


def gh_api(path):
    h = {'Accept': 'application/vnd.github+json'}
    tok = os.environ.get('GITHUB_TOKEN')
    if tok:
        h['Authorization'] = f'Bearer {tok}'
    return json.loads(http_get('https://api.github.com' + path, h))


def parse_contributions(html):
    tips = {}
    for m in re.finditer(r'<tool-tip[^>]*\bfor="([^"]+)"[^>]*>([^<]*)</tool-tip>', html):
        n = re.match(r'\s*(\d[\d,]*)\s+contribution', m.group(2))
        tips[m.group(1)] = int(n.group(1).replace(',', '')) if n else 0
    seen, days = set(), []
    for m in re.finditer(r'<td\b[^>]*>', html):
        tag = m.group(0)
        d = re.search(r'data-date="([^"]+)"', tag)
        if not d or d.group(1) in seen:
            continue
        seen.add(d.group(1))
        i = re.search(r'\bid="([^"]+)"', tag)
        l = re.search(r'data-level="(\d)"', tag)
        days.append([d.group(1), tips.get(i.group(1), 0) if i else 0, int(l.group(1)) if l else 0])
    days.sort()
    if days and sum(x[1] for x in days) == 0 and any(x[2] for x in days):  # tooltips missing: estimate from level
        est = [0, 2, 5, 9, 14]
        for x in days:
            x[1] = est[x[2]]
    return days


def streaks(days):
    counts = [d[1] for d in days]
    longest = run = 0
    for c in counts:
        run = run + 1 if c > 0 else 0
        longest = max(longest, run)
    cur, i = 0, len(counts) - 1
    if i >= 0 and counts[i] == 0:
        i -= 1  # today may not have contributions yet
    while i >= 0 and counts[i] > 0:
        cur += 1
        i -= 1
    return cur, longest


def fetch_live(user):
    repos, page = [], 1
    while True:
        chunk = gh_api(f'/users/{user}/repos?per_page=100&type=owner&page={page}')
        repos += chunk
        if len(chunk) < 100:
            break
        page += 1
    profile = gh_api(f'/users/{user}')
    own = [r for r in repos if not r.get('fork')]
    stars = sum(r.get('stargazers_count', 0) for r in own)
    langs = {}
    for r in sorted(own, key=lambda r: r.get('pushed_at') or '', reverse=True)[:40]:
        try:
            for k, v in gh_api(f"/repos/{user}/{r['name']}/languages").items():
                langs[k] = langs.get(k, 0) + v
        except Exception:
            if r.get('language'):
                langs[r['language']] = langs.get(r['language'], 0) + 1000
    days = parse_contributions(http_get(f'https://github.com/users/{user}/contributions'))
    if not days:
        raise RuntimeError('could not read the contribution calendar')
    cur, longest = streaks(days)
    best = max(days, key=lambda d: d[1])
    return dict(user=user, repos=profile.get('public_repos', len(repos)), stars=stars, followers=profile.get('followers', 0),
                total=sum(d[1] for d in days), current=cur, longest=longest, best=best,
                langs=sorted(langs.items(), key=lambda kv: -kv[1])[:6], days=days,
                updated=dt.datetime.utcnow().strftime('%Y-%m-%d %H:%M'), placeholder=False)


def placeholder(user):
    end = dt.date.today()
    start = end - dt.timedelta(days=370)
    days = [[(start + dt.timedelta(days=i)).isoformat(), 0, 0] for i in range(371)]
    return dict(user=user, repos=None, stars=None, followers=None, total=None, current=None, longest=None, best=None,
                langs=[], days=days, updated='waiting for first sync', placeholder=True)


# ───────────────────────── svg helpers ─────────────────────────
def esc(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def rr(x, y, w, h, r):
    return (f"M{x+r},{y} H{x+w-r} A{r},{r} 0 0 1 {x+w},{y+r} V{y+h-r} A{r},{r} 0 0 1 {x+w-r},{y+h} "
            f"H{x+r} A{r},{r} 0 0 1 {x},{y+h-r} V{y+r} A{r},{r} 0 0 1 {x+r},{y} Z")


def electron(path, dur, begin=0, r=3.4, fill='#ffffff'):
    return (f'<circle r="{r}" fill="{fill}" filter="url(#glow)"><animateMotion dur="{dur}s" repeatCount="indefinite" '
            f'begin="{begin}s" path="{path}"/></circle>')


def appear(i, total=18.0, start=0.6, step=0.12):
    s = (start + i * step) / total
    kt = f"0;{s:.4f};{s+0.02:.4f};0.93;0.97;1"
    return f'<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="{kt}" dur="{total}s" repeatCount="indefinite"/>'


def smooth(pts):
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        mx = (x0 + x1) / 2
        d += f" C{mx:.1f},{y0:.1f} {mx:.1f},{y1:.1f} {x1:.1f},{y1:.1f}"
    return d


def fmt(n):
    return '—' if n is None else f'{n:,}'


# ───────────────────────── render ─────────────────────────
def render(d):
    W, H = 860, 650
    p = rr(1.5, 1.5, W - 3, H - 3, 20)
    o = []
    o.append(f'<defs>'
             f'<linearGradient id="edge" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{C["cyan"]}"/><stop offset=".5" stop-color="{C["violet"]}"/><stop offset="1" stop-color="{C["pink"]}"/></linearGradient>'
             f'<linearGradient id="edge2" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{C["pink"]}"/><stop offset=".5" stop-color="{C["violet"]}"/><stop offset="1" stop-color="{C["cyan"]}"/></linearGradient>'
             f'<linearGradient id="panel" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0c1629"/><stop offset="1" stop-color="#060b17"/></linearGradient>'
             f'<linearGradient id="area" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{C["violet"]}" stop-opacity=".45"/><stop offset="1" stop-color="{C["violet"]}" stop-opacity="0"/></linearGradient>'
             f'<linearGradient id="scan" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ffffff" stop-opacity="0"/><stop offset=".5" stop-color="{C["cyan"]}" stop-opacity=".35"/><stop offset="1" stop-color="#ffffff" stop-opacity="0"/></linearGradient>'
             f'<linearGradient id="bar" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{C["cyan"]}"/><stop offset="1" stop-color="{C["violet"]}"/></linearGradient>'
             f'<filter id="glow" x="-150%" y="-150%" width="400%" height="400%"><feGaussianBlur stdDeviation="2.6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
             f'<pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M24 0H0V24" fill="none" stroke="#1a2a47" stroke-width=".6" opacity=".6"/></pattern>'
             f'<clipPath id="clipan"><path d="{p}"/></clipPath></defs>')
    # frame
    o.append(f'<path d="{p}" fill="url(#panel)" stroke="{C["line"]}" stroke-width="1.2"/>'
             f'<g clip-path="url(#clipan)"><rect width="{W}" height="{H}" fill="url(#grid)" opacity=".55"/></g>')
    for frm, to, grad in [(0, -1000, 'edge'), (-500, -1500, 'edge2')]:
        o.append(f'<path d="{p}" fill="none" stroke="url(#{grad})" stroke-width="2.4" stroke-linecap="round" pathLength="1000" stroke-dasharray="130 870" filter="url(#glow)">'
                 f'<animate attributeName="stroke-dashoffset" from="{frm}" to="{to}" dur="12s" repeatCount="indefinite"/></path>')
    o.append(electron(p, 12, -1.56) + electron(p, 12, -7.56, fill=C['cyan']))
    # header
    label = 'GITHUB_ANALYTICS'
    o.append(f'<text x="32" y="44" font-family="{MONO}" font-size="13" font-weight="700" fill="{C["cyan"]}" letter-spacing="1.5">// {label}</text>'
             f'<rect x="{32+(len(label)+3)*9.9+2:.0f}" y="32" width="8" height="15" fill="{C["cyan"]}"><animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.5;1" dur="1.1s" repeatCount="indefinite"/></rect>')
    live = '' if d['placeholder'] else 'LIVE'
    o.append(f'<circle cx="{W-100}" cy="39" r="4.5" fill="{C["green"] if not d["placeholder"] else C["amber"]}" filter="url(#glow)"><animate attributeName="r" values="3.5;5.5;3.5" dur="1.6s" repeatCount="indefinite"/></circle>'
             f'<text x="{W-88}" y="43" font-family="{MONO}" font-size="12" font-weight="700" fill="{C["green"] if not d["placeholder"] else C["amber"]}" letter-spacing="1.5">{live or "SYNCING"}</text>')

    # stat tiles
    tiles = [('REPOSITORIES', d['repos'], C['cyan']), ('STARS EARNED', d['stars'], C['amber']), ('FOLLOWERS', d['followers'], C['blue']),
             ('CONTRIBUTIONS · 1Y', d['total'], C['violet']), ('CURRENT STREAK', d['current'], C['green']), ('LONGEST STREAK', d['longest'], C['pink'])]
    tw, gap, x0, ty = 124, 10.4, 32, 62
    for i, (lab, val, col) in enumerate(tiles):
        x = x0 + i * (tw + gap)
        unit = ''
        if lab.endswith('STREAK') and val is not None:
            unit = ' d'
        o.append(f'<g>{appear(i)}<rect x="{x:.1f}" y="{ty}" width="{tw}" height="80" rx="12" fill="{C["panel2"]}" stroke="{C["line"]}"/>'
                 f'<rect x="{x+14:.1f}" y="{ty}" width="{tw-28}" height="3" rx="1.5" fill="{col}" filter="url(#glow)"/>'
                 f'<text x="{x+tw/2:.1f}" y="{ty+43}" text-anchor="middle" font-family="{SANS}" font-size="27" font-weight="800" fill="{C["text"]}">{fmt(val)}<tspan font-size="13" fill="{col}">{unit}</tspan></text>'
                 f'<text x="{x+tw/2:.1f}" y="{ty+65}" text-anchor="middle" font-family="{MONO}" font-size="9.5" fill="{C["mute"]}" letter-spacing=".8">{lab}</text></g>')

    # heatmap
    days = d['days']
    first = dt.date.fromisoformat(days[0][0])
    start_row = (first.weekday() + 1) % 7
    gx, gy, cs, step = 32, 202, 12, 15
    ttl = 'contribution_calendar' + ('' if d['total'] is None else f" · best day {d['best'][1]} on {d['best'][0]}")
    o.append(f'<text x="32" y="172" font-family="{MONO}" font-size="12" font-weight="700" fill="{C["text"]}" letter-spacing="1">{esc(ttl)}</text>')
    cols = {}
    last_month = None
    for i, (date, cnt, lvl) in enumerate(days):
        idx = i + start_row
        col, row = idx // 7, idx % 7
        cols.setdefault(col, []).append((row, date, cnt, lvl))
        dd = dt.date.fromisoformat(date)
        if row == 0 and dd.month != last_month and dd.day <= 7:
            last_month = dd.month
            o.append(f'<text x="{gx+col*step}" y="192" font-family="{MONO}" font-size="10" fill="{C["dim"]}">{dd.strftime("%b")}</text>')
    ncols = max(cols) + 1
    for col in sorted(cols):
        cells = ''.join(f'<rect x="{gx+col*step}" y="{gy+row*step}" width="{cs}" height="{cs}" rx="2.6" fill="{LEVELS[lvl]}"/>' for row, date, cnt, lvl in cols[col])
        o.append(f'<g>{appear(col, 18.0, 0.5, 0.045)}{cells}</g>')
    gw = ncols * step
    o.append(f'<clipPath id="gclip"><rect x="{gx}" y="{gy-2}" width="{gw}" height="{7*step}"/></clipPath>'
             f'<g clip-path="url(#gclip)"><rect x="{gx-60}" y="{gy-2}" width="60" height="{7*step}" fill="url(#scan)"><animate attributeName="x" from="{gx-60}" to="{gx+gw}" dur="6s" repeatCount="indefinite"/></rect></g>')
    lx = gx + gw - 5 * (cs + 4) - 62
    o.append(f'<text x="{lx}" y="{gy+7*step+16}" font-family="{MONO}" font-size="10" fill="{C["dim"]}">less</text>')
    for i, c in enumerate(LEVELS):
        o.append(f'<rect x="{lx+30+i*(cs+4)}" y="{gy+7*step+7}" width="{cs}" height="{cs}" rx="2.6" fill="{c}"/>')
    o.append(f'<text x="{lx+30+5*(cs+4)+4}" y="{gy+7*step+16}" font-family="{MONO}" font-size="10" fill="{C["dim"]}">more</text>')

    # weekly activity chart
    cy0 = 352
    o.append(f'<text x="32" y="{cy0}" font-family="{MONO}" font-size="12" font-weight="700" fill="{C["text"]}" letter-spacing="1">weekly_activity</text>')
    weekly = [sum(c[2] for c in cols[k]) for k in sorted(cols)]
    px0, px1, py0, py1 = 32, 828, cy0 + 16, cy0 + 106
    mx = max(weekly) or 1
    pts = [(px0 + (px1 - px0) * i / max(len(weekly) - 1, 1), py1 - (py1 - py0 - 8) * (v / mx)) for i, v in enumerate(weekly)]
    for gl in range(4):
        gy_ = py0 + gl * (py1 - py0) / 3
        o.append(f'<path d="M{px0},{gy_:.1f} H{px1}" stroke="{C["line"]}" stroke-width="1" stroke-dasharray="2 6"/>')
    line = smooth(pts)
    o.append(f'<path d="{line} L{px1},{py1} L{px0},{py1} Z" fill="url(#area)"><animate attributeName="opacity" values=".55;1;.55" dur="4s" repeatCount="indefinite"/></path>')
    o.append(f'<path d="{line}" fill="none" stroke="url(#edge)" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" pathLength="1000" stroke-dasharray="1000" filter="url(#glow)">'
             f'<animate attributeName="stroke-dashoffset" values="1000;0;0;1000" keyTimes="0;.3;.9;1" dur="9s" repeatCount="indefinite"/></path>')
    o.append(electron(line, 9, 0, 4, C['cyan']))
    if d['total'] is not None and mx > 0:
        k = weekly.index(max(weekly))
        o.append(f'<circle cx="{pts[k][0]:.1f}" cy="{pts[k][1]:.1f}" r="4.5" fill="{C["pink"]}" filter="url(#glow)"><animate attributeName="r" values="3.5;6;3.5" dur="2s" repeatCount="indefinite"/></circle>'
                 f'<text x="{min(max(pts[k][0], px0+30), px1-30):.1f}" y="{pts[k][1]-12:.1f}" text-anchor="middle" font-family="{MONO}" font-size="10.5" font-weight="700" fill="{C["pink"]}">peak {mx}</text>')

    # languages
    ly = 488
    o.append(f'<text x="32" y="{ly}" font-family="{MONO}" font-size="12" font-weight="700" fill="{C["text"]}" letter-spacing="1">top_languages <tspan fill="{C["dim"]}" font-weight="400">(by code size, public repos)</tspan></text>')
    langs = d['langs']
    tot = sum(v for _, v in langs) or 1
    if not langs:
        o.append(f'<text x="32" y="{ly+34}" font-family="{MONO}" font-size="12" fill="{C["mute"]}">waiting for the first sync…</text>')
    for i, (name, val) in enumerate(langs):
        colx = 32 if i < 3 else 450
        y = ly + 20 + (i % 3) * 28
        pct = 100 * val / tot
        col = LANG_COLORS[i % len(LANG_COLORS)]
        bw = 196
        fill = max(bw * pct / 100, 4)
        o.append(f'<g>{appear(i, 18.0, 0.9, 0.2)}<text x="{colx}" y="{y+10}" font-family="{MONO}" font-size="12" fill="{C["text"]}">{esc(name)}</text>'
                 f'<rect x="{colx+112}" y="{y}" width="{bw}" height="10" rx="5" fill="{C["panel2"]}" stroke="{C["line"]}"/>'
                 f'<rect x="{colx+112}" y="{y}" width="{fill:.1f}" height="10" rx="5" fill="{col}" filter="url(#glow)" opacity=".9"><animate attributeName="width" values="0;{fill:.1f};{fill:.1f}" keyTimes="0;.35;1" dur="6s" repeatCount="indefinite"/></rect>'
                 f'<text x="{colx+112+bw+10}" y="{y+10}" font-family="{MONO}" font-size="11.5" fill="{col}">{pct:.1f}%</text></g>')
    o.append(f'<text x="32" y="{H-26}" font-family="{MONO}" font-size="10.5" fill="{C["dim"]}">synced {esc(d["updated"])} UTC · github.com/{esc(d["user"])} · refreshed daily by GitHub Actions</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="GitHub analytics for {esc(d["user"])}">{"".join(o)}</svg>')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--user', default=USER_DEFAULT)
    ap.add_argument('--out', default='assets/analytics.svg')
    ap.add_argument('--json', default='data/stats.json')
    ap.add_argument('--placeholder', action='store_true')
    ap.add_argument('--fixture', help='load a saved stats.json instead of the network (testing)')
    a = ap.parse_args()
    if a.placeholder:
        d = placeholder(a.user)
    elif a.fixture:
        d = json.load(open(a.fixture))
    else:
        try:
            d = fetch_live(a.user)
        except Exception as e:  # keep the old SVG if anything goes wrong
            print('FAILED, keeping existing file:', e, file=sys.stderr)
            sys.exit(1)
    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    with open(a.out, 'w', encoding='utf-8') as f:
        f.write(render(d))
    if not a.placeholder and not a.fixture:
        os.makedirs(os.path.dirname(a.json) or '.', exist_ok=True)
        slim = {k: v for k, v in d.items() if k != 'days'}
        json.dump(slim, open(a.json, 'w'), indent=2)
    print('wrote', a.out)


if __name__ == '__main__':
    main()
