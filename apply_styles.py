import re
import os

PORTFOLIO_DIR = "D:/03_Projects/Portfolio"

FILES = [
    "airport-ols.html",
    "asset-monitoring.html",
    "bioregional-atlas.html",
    "etl-geodatabase.html",
    "snowboard.html",
    "stockpile-volume.html",
]

NEW_FONT_LINK = '<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Syne:wght@400;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap" rel="stylesheet">'

NEW_ROOT = """:root {
  --bg:        #ffffff;
  --bg-off:    #f8f4ee;
  --bg-muted:  #f1ebe0;
  --border:    #e8e0d4;
  --border-m:  #d8cfc0;
  --accent:    #d44820;
  --accent-2:  #c8880a;
  --text:      #18120a;
  --text-2:    #4a3828;
  --text-3:    #9a8878;
  --mono: 'DM Mono', monospace;
  --syne: 'Syne', sans-serif;
  --sans: 'DM Sans', sans-serif;
}"""

NEW_NAV_CSS = """/* ─── NAV ─── */
nav {
  position: fixed; top: 0; left: 0; right: 0; z-index: 200;
  height: 52px;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 56px;
  background: rgba(255,255,255,0.94);
  backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--border);
}
.nav-logo {
  font-family: var(--mono); font-size: 12px; font-weight: 500;
  color: var(--text); letter-spacing: .05em; text-decoration: none;
  flex-shrink: 0;
}
.nav-logo span { color: var(--accent); }
.nav-right { display: flex; align-items: center; }
.nav-item { position: relative; }
.nav-a, .nav-plain {
  font-family: var(--mono); font-size: 10px; color: var(--text-3);
  letter-spacing: .14em; text-transform: uppercase; text-decoration: none;
  padding: 0 12px; height: 52px; display: flex; align-items: center;
  transition: color .16s; white-space: nowrap; cursor: pointer;
  background: none; border: none;
}
.nav-a:hover, .nav-plain:hover { color: var(--accent); }
.nav-chevron { margin-left: 3px; font-size: 7px; display: inline-block; transition: transform .18s; }
.nav-item:hover .nav-chevron { transform: rotate(180deg); }
.nav-drop {
  display: none; position: absolute; top: 52px; left: 0;
  background: var(--bg); border: 1px solid var(--border);
  border-top: 2px solid var(--accent);
  min-width: 250px; z-index: 300;
  box-shadow: 0 8px 24px rgba(0,0,0,.06);
}
.nav-item:hover .nav-drop { display: block; }
.nav-drop a {
  display: flex; align-items: baseline; gap: 10px;
  padding: 9px 16px; font-family: var(--mono); font-size: 10px;
  letter-spacing: .1em; color: var(--text-2); text-decoration: none;
  border-bottom: 1px solid var(--border); transition: background .14s;
}
.nav-drop a:last-child { border-bottom: none; }
.nav-drop a:hover { background: var(--bg-off); color: var(--accent); }
.nav-drop .dn { color: var(--text-3); font-size: 9px; flex-shrink: 0; }
.nav-cv {
  font-family: var(--mono); font-size: 10px; padding: 6px 13px;
  border: 1px solid var(--accent); color: var(--accent); text-decoration: none;
  letter-spacing: .1em; text-transform: uppercase; margin-left: 8px;
  transition: background .16s, color .16s;
}
.nav-cv:hover { background: var(--accent); color: var(--bg); }"""

NEW_FOOTER_CSS = """/* ─── FOOTER ─── */
footer {
  text-align: center; padding: 22px 56px;
  border-top: 1px solid var(--border);
  font-family: var(--mono); font-size: 9px; color: var(--text-3); letter-spacing: .08em;
}"""

NEW_NAV_HTML = """<nav>
  <a href="index.html" class="nav-logo">yang<span>.spatial</span></a>
  <div class="nav-right">
    <div class="nav-item">
      <a class="nav-a">Work <span class="nav-chevron">&#9660;</span></a>
      <div class="nav-drop">
        <a href="asset-monitoring.html"><span class="dn">01</span>Asset Management</a>
        <a href="airport-ols.html"><span class="dn">02</span>Airport OLS &amp; Hazard Tree</a>
        <a href="bioregional-atlas.html"><span class="dn">03</span>Bioregional Atlas</a>
        <a href="stockpile-volume.html"><span class="dn">05</span>Stockpile Volume</a>
        <a href="etl-geodatabase.html"><span class="dn">06</span>Geodatabase ETL</a>
      </div>
    </div>
    <a href="index.html#wiww" class="nav-plain">Capabilities</a>
    <a href="index.html#stack" class="nav-plain">Stack</a>
    <a href="index.html#about" class="nav-plain">About</a>
    <a href="index.html#offpiste" class="nav-plain">Off-piste</a>
    <a href="index.html#contact" class="nav-plain">Contact</a>
    <a href="#" class="nav-plain nav-cv" onclick="downloadCV(event)">CV &#8595;</a>
  </div>
</nav>"""

FOOTER_HTML = '<footer>&#169; 2025 Chenghao Yang &nbsp;&middot;&nbsp; Vancouver, BC &nbsp;&middot;&nbsp; Built with GitHub Pages</footer>'

DOWNLOAD_CV_SCRIPT = """<script>
function downloadCV(e) {
  e.preventDefault();
  var l = document.createElement('a');
  l.href = 'cv.pdf';
  l.download = 'Chenghao_Yang_CV.pdf';
  document.body.appendChild(l);
  l.click();
  document.body.removeChild(l);
}
</script>"""


def process_file(filename):
    path = os.path.join(PORTFOLIO_DIR, filename)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    changes = []

    # ── 1. Font import ──────────────────────────────────────────────────────
    # Remove the preconnect link to fonts.googleapis.com
    preconnect_pattern = re.compile(
        r'<link\s+rel="preconnect"\s+href="https://fonts\.googleapis\.com">\s*\n?',
        re.DOTALL
    )
    content, n_pre = preconnect_pattern.subn('', content)

    # Remove the preconnect link to fonts.gstatic.com (may also exist)
    gstatic_pattern = re.compile(
        r'<link\s+rel="preconnect"\s+href="https://fonts\.gstatic\.com"[^>]*>\s*\n?',
        re.DOTALL
    )
    content, _ = gstatic_pattern.subn('', content)

    # Replace the actual font stylesheet link
    font_pattern = re.compile(
        r'<link\s[^>]*fonts\.googleapis\.com[^>]*>',
        re.DOTALL
    )
    new_content, n = font_pattern.subn(NEW_FONT_LINK, content)
    if n:
        changes.append(f"  [1] Font import replaced ({n} font link(s), {n_pre} preconnect(s) removed)")
    else:
        changes.append("  [1] Font import — NOT FOUND, skipped")
    content = new_content

    # ── 2. :root block ──────────────────────────────────────────────────────
    # Match :root { ... } including all variable names regardless of format
    root_pattern = re.compile(r':root\s*\{[^}]*\}', re.DOTALL)
    new_content, n = root_pattern.subn(NEW_ROOT, content)
    if n:
        changes.append(f"  [2] :root block replaced ({n} occurrence(s))")
    else:
        changes.append("  [2] :root block — NOT FOUND, skipped")
    content = new_content

    # ── 3. body background — should be fine after :root update ─────────────
    # Verify body still uses var(--bg)
    if 'background:var(--bg)' in content or 'background: var(--bg)' in content:
        changes.append("  [3] body background uses var(--bg) — OK")
    else:
        # snowboard.html uses --cream; update body background to var(--bg)
        body_bg_pattern = re.compile(
            r'(body\s*\{[^}]*?background\s*:\s*)(var\(--\w+\)|#[0-9a-fA-F]{3,6})',
            re.DOTALL
        )
        new_content, n = body_bg_pattern.subn(r'\1var(--bg)', content)
        if n:
            changes.append(f"  [3] body background updated to var(--bg) ({n} occurrence(s))")
        else:
            changes.append("  [3] body background — could not update, check manually")
        content = new_content

    # ── 4. Remove body::before ──────────────────────────────────────────────
    before_pattern = re.compile(r'\s*body::before\s*\{[^}]*\}', re.DOTALL)
    new_content, n = before_pattern.subn('', content)
    if n:
        changes.append(f"  [4] body::before removed ({n} occurrence(s))")
    else:
        changes.append("  [4] body::before — NOT FOUND, skipped")
    content = new_content

    # ── 5. Replace nav CSS + add footer CSS ────────────────────────────────
    # Strategy: find and replace the entire nav CSS section.
    # The nav section starts at a nav comment or nav{ and ends at the last nav-related rule.
    # We'll match from (optional comment + nav{) through the last rule that references
    # .nav-back, .nav-links, .nav-cv, etc.

    # First try: match a comment-delimited nav block
    nav_css_comment = re.compile(
        r'/\*\s*[─\-]*\s*NAV\s*[─\-]*\s*\*/.*?(?=(?:/\*|</style>))',
        re.DOTALL
    )
    m = nav_css_comment.search(content)
    if m:
        new_content = content[:m.start()] + NEW_NAV_CSS + '\n' + content[m.end():]
        changes.append("  [5] Nav CSS block (comment-delimited) replaced")
        content = new_content
    else:
        # Fallback: match from 'nav{' or 'nav {' up through all nav-related rules
        # We need to find the span from the first nav CSS rule to the last nav-related rule
        nav_css_start = re.compile(r'(?:nav\s*\{|\.nav-\w+\s*\{)')
        start_m = nav_css_start.search(content)
        if start_m:
            # Find the extent: look for all nav-related rules and find the last one
            nav_rule_pattern = re.compile(
                r'(?:nav[\s{,]|\.nav-[\w]+).*?(?:\{[^}]*\}|\{[^}]*\{[^}]*\}[^}]*\})',
                re.DOTALL
            )
            last_end = start_m.start()
            search_from = start_m.start()
            while True:
                rm = nav_rule_pattern.search(content, search_from)
                if not rm:
                    break
                # Only count if it's still a nav-related rule (not too far off)
                if rm.start() - last_end > 500:
                    break
                last_end = rm.end()
                search_from = rm.end()

            block = content[start_m.start():last_end]
            new_content = content[:start_m.start()] + NEW_NAV_CSS + '\n' + content[last_end:]
            changes.append(f"  [5] Nav CSS block (fallback regex) replaced ({len(block)} chars)")
            content = new_content
        else:
            changes.append("  [5] Nav CSS — NOT FOUND, skipped")

    # Add footer CSS before </style>
    if 'footer' not in content or NEW_FOOTER_CSS not in content:
        content = content.replace('</style>', NEW_FOOTER_CSS + '\n  </style>', 1)
        changes.append("  [5b] Footer CSS added before </style>")
    else:
        changes.append("  [5b] Footer CSS already present")

    # ── 6. Replace nav HTML ─────────────────────────────────────────────────
    nav_html_pattern = re.compile(r'<nav>.*?</nav>', re.DOTALL)
    new_content, n = nav_html_pattern.subn(NEW_NAV_HTML, content)
    if n:
        changes.append(f"  [6] Nav HTML replaced ({n} occurrence(s))")
    else:
        changes.append("  [6] Nav HTML — NOT FOUND, skipped")
    content = new_content

    # ── 7. Add footer HTML before </body> ──────────────────────────────────
    if '<footer>' not in content:
        content = content.replace('</body>', FOOTER_HTML + '\n</body>', 1)
        changes.append("  [7] Footer HTML added before </body>")
    else:
        changes.append("  [7] Footer HTML already present")

    # ── 8. Add downloadCV script before </body> ─────────────────────────────
    if 'downloadCV' not in content:
        content = content.replace('</body>', DOWNLOAD_CV_SCRIPT + '\n</body>', 1)
        changes.append("  [8] downloadCV script added before </body>")
    else:
        changes.append("  [8] downloadCV script already present")

    # Save
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

    return changes


def main():
    print("=" * 60)
    print("Portfolio Style Updater")
    print("=" * 60)
    for filename in FILES:
        print(f"\nProcessing: {filename}")
        changes = process_file(filename)
        for c in changes:
            print(c)
        print(f"  -> Saved.")
    print("\n" + "=" * 60)
    print("Done. All 6 files processed.")


if __name__ == "__main__":
    main()
