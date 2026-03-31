"""Generate a static index.html from the folder structure."""
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent
FOLDER_PATTERN = re.compile(r'^(\d{8})_(.+)$')

HOMEPAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Learning Navigator</title>
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --sbg:#1a1a2e;--stext:#c8d0e7;--accent:#6a4c93;
  --bg:#f5f6fa;--card:#fff;--border:#dee2e6;
  --r:6px;--text:#212529;
}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
  background:var(--sbg);color:var(--stext);min-height:100vh;padding:2rem 1.5rem}}
h1{{font-size:1.6rem;font-weight:700;margin-bottom:0.25rem;color:#fff}}
.subtitle{{font-size:0.9rem;color:#8892b0;margin-bottom:1.5rem}}
.intro{{font-size:0.85rem;color:#8892b0;line-height:1.6;max-width:640px;margin-bottom:2.5rem;padding:1rem 1.25rem;background:#16213e;border:1px solid #2d2d4e;border-radius:var(--r)}}
.field-section{{margin-bottom:2.5rem}}
.field-title{{
  font-size:0.75rem;font-weight:600;letter-spacing:0.1em;
  text-transform:uppercase;color:#8892b0;
  border-bottom:1px solid #2d2d4e;padding-bottom:0.5rem;margin-bottom:1rem
}}
.cards{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:1rem}}
.card{{
  background:#16213e;border:1px solid #2d2d4e;border-radius:var(--r);
  padding:1rem 1.25rem;display:flex;flex-direction:column;gap:0.5rem;
  transition:border-color 0.15s,transform 0.15s;
  text-decoration:none;color:inherit;cursor:pointer;
}}
.card:hover{{border-color:var(--accent);transform:translateY(-2px)}}
.card-date{{font-size:0.75rem;color:#8892b0;font-variant-numeric:tabular-nums}}
.card-title{{font-size:1rem;font-weight:600;color:#e6e6f0;line-height:1.35}}
.empty{{color:#8892b0;font-size:0.9rem;padding:0.5rem 0}}
</style>
</head>
<body>
<h1>Learning Navigator</h1>
<p class="subtitle">Interactive visualizations — sorted by date, newest first</p>
<p class="intro">This page is a place for me, Jayvee Abella, to create content that helps me learn more about any given topic. My goal is to make one of these a day. All content is generated using AI, so accuracy may vary.</p>
{sections}
{empty_msg}
</body>
</html>
"""

SECTION_TMPL = """
<section class="field-section">
  <div class="field-title">{field}</div>
  <div class="cards">
    {cards}
  </div>
</section>
"""

CARD_TMPL = """
    <a class="card" href="{url}">
      <div class="card-date">{date_label}</div>
      <div class="card-title">{title}</div>
    </a>
"""


def discover_pages() -> dict[str, list[dict]]:
    fields: dict[str, list[dict]] = {}

    for html in sorted(ROOT.glob("*/*/index.html")):
        parts = html.relative_to(ROOT).parts
        if len(parts) != 3:
            continue

        field, folder, _ = parts
        m = FOLDER_PATTERN.match(folder)

        if m:
            date = datetime.strptime(m.group(1), "%Y%m%d")
            title = m.group(2).replace("_", " ").title()
            date_label = date.strftime("%b %d, %Y")
        else:
            date = datetime.min
            title = folder.replace("_", " ").title()
            date_label = ""

        fields.setdefault(field, []).append(
            {
                "title": title,
                "date": date,
                "date_label": date_label,
                "url": f"{field}/{folder}/index.html",
            }
        )

    for entries in fields.values():
        entries.sort(key=lambda e: e["date"], reverse=True)

    return dict(sorted(fields.items()))


def build() -> None:
    fields = discover_pages()

    sections = ""
    for field, pages in fields.items():
        cards = "".join(
            CARD_TMPL.format(
                date_label=p["date_label"],
                title=p["title"],
                url=p["url"],
            )
            for p in pages
        )
        sections += SECTION_TMPL.format(field=field, cards=cards)

    empty_msg = (
        ""
        if fields
        else '<p style="color:#8892b0">No index.html files found yet.</p>'
    )

    output = HOMEPAGE.format(sections=sections, empty_msg=empty_msg)
    (ROOT / "index.html").write_text(output)
    print(f"Built index.html with {sum(len(v) for v in fields.values())} pages across {len(fields)} field(s).")


if __name__ == "__main__":
    build()
