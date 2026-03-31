#!/usr/bin/env python3
"""
Generate pure CSS Mastermind game.

Black pegs: enumerate 2^4=16 position-match masks per row.
White pegs: hidden helper elements + CSS counter.
  - 6 colors x 4 levels = 24 helpers per row
  - Each helper shown when white(color) >= level
  - CSS counter sums visible helpers → @counter-style symbolic renders ○ circles
"""

from itertools import combinations

COLORS = ["red", "orange", "yellow", "green", "blue", "purple"]
ROWS = 10
SLOTS = 4
HEX = {
    "red": "#E74C3C", "orange": "#E67E22", "yellow": "#F1C40F",
    "green": "#27AE60", "blue": "#2980B9", "purple": "#8E44AD",
}

def sid(p, c): return f"s{p}-{c}"
def gid(r, p, c): return f"g{r}-{p}-{c}"

def pos_match_has(r, p):
    """`:has()` clause: position p matches any color in row r."""
    alts = ", ".join(f"#{sid(p, c)}:checked ~ #{gid(r, p, c)}:checked" for c in COLORS)
    return f":has({alts})"


def html():
    L = []
    def w(s=""): L.append(s)

    w("<!DOCTYPE html>")
    w('<html lang="en"><head>')
    w('<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">')
    w("<title>Mastermind — Pure CSS</title>")
    w('<link rel="stylesheet" href="style.css">')
    w("</head><body>")

    # All inputs as direct children of body
    w('<input type="checkbox" id="lock-in" class="sr">')
    for r in range(1, ROWS+1):
        w(f'<input type="checkbox" id="submit-{r}" class="sr">')
    for p in range(1, SLOTS+1):
        for c in COLORS:
            w(f'<input type="radio" name="secret-{p}" id="{sid(p,c)}" class="sr">')
    for r in range(1, ROWS+1):
        for p in range(1, SLOTS+1):
            for c in COLORS:
                w(f'<input type="radio" name="guess-{r}-{p}" id="{gid(r,p,c)}" class="sr">')

    w('<div class="g">')
    w('<h1>Mastermind</h1><p class="sub">Pure CSS — No JavaScript</p>')

    # SETUP
    w('<div class="setup">')
    w('<h2>Player 1: Set the Secret Code</h2>')
    w('<p class="hint">Pick a color for each slot, then lock it in.</p>')
    w('<div class="sd">')
    for p in range(1, SLOTS+1):
        w(f'<div class="ps" id="sd-{p}"><span class="ep">?</span>')
        for c in COLORS:
            w(f'<span class="peg peg-{c}" data-for="{sid(p,c)}"></span>')
        w('</div>')
    w('</div>')
    for p in range(1, SLOTS+1):
        w(f'<div class="pk"><div class="pl">Slot {p}</div><div class="opts">')
        for c in COLORS:
            w(f'<label for="{sid(p,c)}" class="opt opt-{c}"></label>')
        w('</div></div>')
    w('<label for="lock-in" class="btn lock">Lock In Code</label>')
    w('</div>')

    # PLAY
    w('<div class="play">')
    w('<h2>Player 2: Crack the Code</h2>')
    w('<div class="sh">')
    for _ in range(SLOTS):
        w('<div class="hp">?</div>')
    w('</div>')

    for r in range(1, ROWS+1):
        w(f'<div class="row" id="row-{r}">')
        w(f'<div class="rn">{r}</div><div class="gd">')
        for p in range(1, SLOTS+1):
            w(f'<div class="ps"><span class="ep"></span>')
            for c in COLORS:
                w(f'<span class="peg peg-{c}" data-for="{gid(r,p,c)}"></span>')
            w('</div>')
        w('</div><div class="rp">')
        for p in range(1, SLOTS+1):
            w('<div class="mp">')
            for c in COLORS:
                w(f'<label for="{gid(r,p,c)}" class="opt mi opt-{c}"></label>')
            w('</div>')
        w('</div>')
        w(f'<label for="submit-{r}" class="btn sb">Submit</label>')
        # Feedback
        w(f'<div class="fb" id="fb-{r}">')
        for i in range(1, 5):
            w(f'<span class="fbb fbb-{i}"></span>')
        w(f'<span class="ww" id="ww-{r}">')
        for c in COLORS:
            for lv in range(1, 5):
                w(f'<span class="wh wh-{r}-{c}-{lv}"></span>')
        w('</span>')
        w('</div>')
        w('</div>')

    w('</div>')

    # GAME OVER
    w('<div class="go">')
    w('<div class="win"><h2>Code Cracked!</h2><p>Player 2 wins!</p></div>')
    w('<div class="loss"><h2>Out of Guesses!</h2><p>Player 1 wins!</p></div>')
    w('<div class="rev">')
    for p in range(1, SLOTS+1):
        w(f'<div class="ps">')
        for c in COLORS:
            w(f'<span class="peg peg-{c}" data-for="{sid(p,c)}"></span>')
        w('</div>')
    w('</div>')
    w('<a href="" class="btn nb">New Game</a>')
    w('</div>')

    w('</div></body></html>')
    return "\n".join(L)


def css():
    L = []
    def w(s=""): L.append(s)

    # === BASE STYLES ===
    w("/* Mastermind — Pure CSS — generated */")
    w("*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}")
    w("body{font-family:'Segoe UI',system-ui,sans-serif;background:#1a1a2e;color:#e0e0e0;min-height:100vh;display:flex;justify-content:center}")
    w(".sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0);border:0}")
    w(".g{max-width:480px;width:100%;padding:20px;text-align:center}")
    w("h1{font-size:2rem;color:#fff;letter-spacing:2px;margin-bottom:2px}")
    w(".sub{font-size:.8rem;color:#555;margin-bottom:20px}")
    w("h2{font-size:1.1rem;color:#ccc;margin-bottom:10px}")
    w(".hint{font-size:.8rem;color:#777;margin-bottom:14px}")

    for c, h in HEX.items():
        w(f".peg-{c},.opt-{c}{{background:{h}}}")

    w(".ps{width:44px;height:44px;border-radius:50%;background:#2a2a4a;display:inline-flex;align-items:center;justify-content:center;position:relative;overflow:hidden;margin:0 4px}")
    w(".ep{font-size:1rem;color:#555}")
    w(".peg{position:absolute;inset:0;border-radius:50%;display:none}")
    w(".pk{margin-bottom:10px}")
    w(".pl{font-size:.75rem;color:#666;margin-bottom:3px}")
    w(".opts,.mp{display:flex;gap:6px;justify-content:center}")
    w(".opt{width:32px;height:32px;border-radius:50%;cursor:pointer;border:3px solid transparent;transition:transform .12s,border-color .12s}")
    w(".opt:hover{transform:scale(1.12);border-color:rgba(255,255,255,.4)}")
    w(".mi{width:20px;height:20px;border-width:2px}")
    w(".btn{display:none;margin:12px auto;padding:8px 24px;background:#16213e;color:#fff;border:2px solid #0f3460;border-radius:8px;cursor:pointer;font-size:.95rem;text-decoration:none;width:fit-content;transition:background .15s}")
    w(".btn:hover{background:#0f3460}")
    w(".sd{display:flex;justify-content:center;gap:8px;margin-bottom:16px}")
    w(".row{display:none;flex-direction:column;align-items:center;background:#16213e;border-radius:10px;padding:10px;margin-bottom:8px}")
    w(".rn{font-size:.7rem;color:#444;margin-bottom:4px}")
    w(".gd{display:flex;justify-content:center;margin-bottom:6px}")
    w(".rp{display:flex;gap:14px;justify-content:center;margin-bottom:6px}")
    w(".mp{display:grid;grid-template-columns:repeat(3,1fr);gap:3px}")
    w(".fb{display:none;gap:6px;justify-content:center;align-items:center;margin-top:8px}")
    w(".fbb{display:none;width:20px;height:20px;border-radius:50%;background:#1a1a1a;border:3px solid #fff;box-shadow:0 0 0 1px rgba(255,255,255,0.3)}")
    w(".ww{display:inline-flex;counter-reset:wp;align-items:center}")
    w(".wh{display:none;counter-increment:wp}")
    w(".sh{display:flex;justify-content:center;gap:8px;margin-bottom:16px}")
    w(".hp{width:40px;height:40px;border-radius:50%;background:#0f3460;display:flex;align-items:center;justify-content:center;font-size:1rem;color:#444}")
    w(".go{display:none}")
    w(".win,.loss{display:none}")
    w(".win h2{color:#27AE60}")
    w(".loss h2{color:#E74C3C}")
    w(".rev{display:flex;justify-content:center;gap:8px;margin:14px 0}")
    w(".nb{display:inline-block !important}")

    # Counter style for white pegs
    # 'symbolic' renders N as N repetitions of the symbol. Range 1-4 so 0 falls through
    # to fallback (which we set to a custom empty style).
    w("@counter-style wempty{system:cyclic;symbols:'';suffix:''}")
    w("@counter-style wdots{system:symbolic;symbols:'\\25CB';suffix:'';range:1 4;fallback:wempty}")
    w(".ww::after{content:counter(wp,wdots);font-size:20px;letter-spacing:2px;color:rgba(255,255,255,0.5)}")

    # === STATE MACHINE ===
    w(".setup{display:block}.play{display:none}")
    w("#lock-in:checked~.g .setup{display:none}")
    w("#lock-in:checked~.g .play{display:block}")
    w("#lock-in:checked~.g .play #row-1{display:flex}")

    # === PEG PREVIEWS ===
    for p in range(1, SLOTS+1):
        for c in COLORS:
            w(f'#{sid(p,c)}:checked~.g .peg[data-for="{sid(p,c)}"]{{display:block}}')
        w(f'body:has([name="secret-{p}"]:checked) .g #sd-{p} .ep{{display:none}}')

    for r in range(1, ROWS+1):
        for p in range(1, SLOTS+1):
            for c in COLORS:
                w(f'#{gid(r,p,c)}:checked~.g .peg[data-for="{gid(r,p,c)}"]{{display:block}}')

    # === SELECTED OPTION STYLING ===
    for p in range(1, SLOTS+1):
        for c in COLORS:
            w(f'#{sid(p,c)}:checked~.g label[for="{sid(p,c)}"]{{border-color:#fff;transform:scale(1.12)}}')
    for r in range(1, ROWS+1):
        for p in range(1, SLOTS+1):
            for c in COLORS:
                w(f'#{gid(r,p,c)}:checked~.g label[for="{gid(r,p,c)}"]{{border-color:#fff;transform:scale(1.12)}}')

    # === VALIDATION ===
    hs = "".join(f':has([name="secret-{p}"]:checked)' for p in range(1, SLOTS+1))
    w(f"body{hs} .g .lock{{display:block}}")
    for r in range(1, ROWS+1):
        hs = "".join(f':has([name="guess-{r}-{p}"]:checked)' for p in range(1, SLOTS+1))
        w(f"body{hs} .g #row-{r} .sb{{display:block}}")

    # === ROW PROGRESSION ===
    for r in range(1, ROWS+1):
        w(f"#submit-{r}:checked~.g #row-{r} .fb{{display:flex}}")
        w(f"#submit-{r}:checked~.g #row-{r} .sb{{display:none !important}}")
        w(f"#submit-{r}:checked~.g #row-{r} .rp{{display:none}}")
        w(f"#submit-{r}:checked~.g #row-{r} .gd{{pointer-events:none}}")
        if r < ROWS:
            w(f"#submit-{r}:checked~.g #row-{r+1}{{display:flex}}")

    # === WIN ===
    for r in range(1, ROWS+1):
        m = "".join(pos_match_has(r, p) for p in range(1, SLOTS+1))
        w(f"body:has(#submit-{r}:checked){m} .g .go{{display:block}}")
        w(f"body:has(#submit-{r}:checked){m} .g .go .win{{display:block}}")
        w(f"body:has(#submit-{r}:checked){m} .g .play{{display:none}}")

    # === LOSS ===
    m10 = "".join(pos_match_has(ROWS, p) for p in range(1, SLOTS+1))
    w(f"body:has(#submit-{ROWS}:checked):not({m10}) .g .go{{display:block}}")
    w(f"body:has(#submit-{ROWS}:checked):not({m10}) .g .go .loss{{display:block}}")
    w(f"body:has(#submit-{ROWS}:checked):not({m10}) .g .play{{display:none}}")

    # Hide future rows on win
    for r in range(1, ROWS):
        m = "".join(pos_match_has(r, p) for p in range(1, SLOTS+1))
        for fr in range(r+1, ROWS+1):
            w(f"body:has(#submit-{r}:checked){m} .g #row-{fr}{{display:none !important}}")

    # === BLACK PEGS ===
    for r in range(1, ROWS+1):
        for mask in range(1, 16):
            on = [p for p in range(1, 5) if mask & (1<<(p-1))]
            off = [p for p in range(1, 5) if not(mask & (1<<(p-1)))]
            parts = f":has(#submit-{r}:checked)"
            for p in on: parts += pos_match_has(r, p)
            for p in off: parts += f":not({pos_match_has(r, p)})"
            for i in range(1, len(on)+1):
                w(f"body{parts} .g #fb-{r} .fbb-{i}{{display:block}}")

    # === WHITE PEG HELPERS ===
    # For each color C and level L (1-4):
    # white(C) >= L means >= L secret positions are C and not-black,
    # AND >= L guess positions are C and not-black.
    # A secret pos is "C and not-black" = secret[pos]=C AND guess[pos]!=C.
    # Enumerate all combos of L secret positions and L guess positions.

    for r in range(1, ROWS+1):
        for c in COLORS:
            for lv in range(1, 5):
                sels = []
                for s_set in combinations(range(1, 5), lv):
                    for g_set in combinations(range(1, 5), lv):
                        parts = f":has(#submit-{r}:checked)"
                        for sp in s_set:
                            parts += f":has(#{sid(sp, c)}:checked)"
                            parts += f":not(:has(#{gid(r, sp, c)}:checked))"
                        for gp in g_set:
                            parts += f":has(#{gid(r, gp, c)}:checked)"
                            parts += f":not(:has(#{sid(gp, c)}:checked))"
                        sels.append(f"body{parts}")
                target = f".g .wh-{r}-{c}-{lv}"
                # Comma-join all selectors targeting the same element
                w(",\n".join(f"{s} {target}" for s in sels) + "{display:inline}")

    return "\n".join(L)


if __name__ == "__main__":
    import os, sys
    base = os.path.dirname(os.path.abspath(__file__))

    h = html()
    with open(os.path.join(base, "index.html"), "w") as f: f.write(h)
    print(f"index.html: {len(h):,} bytes")

    c = css()
    with open(os.path.join(base, "style.css"), "w") as f: f.write(c)
    print(f"style.css: {len(c):,} bytes")

    # Count selectors
    sel_count = c.count("{")
    print(f"~{sel_count:,} CSS rules")
