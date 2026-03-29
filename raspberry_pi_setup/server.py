import os
import re
from datetime import datetime
from pathlib import Path

from flask import Flask, render_template_string, send_from_directory

app = Flask(__name__)
ROOT = Path(__file__).parent
FOLDER_PATTERN = re.compile(r'^(\d{8})_(.+)$')

HOMEPAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Learning Navigator</title>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --sbg:#1a1a2e;--stext:#c8d0e7;--accent:#6a4c93;
  --bg:#f5f6fa;--card:#fff;--border:#dee2e6;
  --r:6px;--text:#212529;
}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
  background:var(--sbg);color:var(--stext);min-height:100vh;padding:2rem 1.5rem}
h1{font-size:1.6rem;font-weight:700;margin-bottom:0.25rem;color:#fff}
.subtitle{font-size:0.9rem;color:#8892b0;margin-bottom:2.5rem}
.field-section{margin-bottom:2.5rem}
.field-title{
  font-size:0.75rem;font-weight:600;letter-spacing:0.1em;
  text-transform:uppercase;color:#8892b0;
  border-bottom:1px solid #2d2d4e;padding-bottom:0.5rem;margin-bottom:1rem
}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:1rem}
.card{
  background:#16213e;border:1px solid #2d2d4e;border-radius:var(--r);
  padding:1rem 1.25rem;display:flex;flex-direction:column;gap:0.5rem;
  transition:border-color 0.15s,transform 0.15s;
}
.card:hover{border-color:var(--accent);transform:translateY(-2px)}
.card-date{font-size:0.75rem;color:#8892b0;font-variant-numeric:tabular-nums}
.card-title{font-size:1rem;font-weight:600;color:#e6e6f0;line-height:1.35}
.card-link{
  display:inline-block;margin-top:0.25rem;padding:0.35rem 0.85rem;
  background:var(--accent);color:#fff;border-radius:4px;
  font-size:0.8rem;font-weight:600;text-decoration:none;align-self:flex-start;
  transition:opacity 0.15s;
}
.card-link:hover{opacity:0.85}
.empty{color:#8892b0;font-size:0.9rem;padding:0.5rem 0}
</style>
</head>
<body>
<h1>Learning Navigator</h1>
<p class="subtitle">Interactive visualizations — sorted by date, newest first</p>

{% for field, pages in fields.items() %}
<section class="field-section">
  <div class="field-title">{{ field }}</div>
  <div class="cards">
    {% for p in pages %}
    <div class="card">
      <div class="card-date">{{ p.date_label }}</div>
      <div class="card-title">{{ p.title }}</div>
      <a class="card-link" href="{{ p.url }}">Open →</a>
    </div>
    {% endfor %}
    {% if not pages %}
    <div class="empty">No pages found.</div>
    {% endif %}
  </div>
</section>
{% endfor %}

{% if not fields %}
<p style="color:#8892b0">No index.html files found yet. Add a folder like
<code>math/20260401_topic_name/index.html</code> and refresh.</p>
{% endif %}
</body>
</html>
"""


def discover_pages() -> dict[str, list[dict]]:
    fields: dict[str, list[dict]] = {}

    for html in sorted(ROOT.glob("*/*/index.html")):
        parts = html.relative_to(ROOT).parts  # ('math', '20260328_...', 'index.html')
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
                "url": f"/{field}/{folder}/index.html",
            }
        )

    for entries in fields.values():
        entries.sort(key=lambda e: e["date"], reverse=True)

    return dict(sorted(fields.items()))


@app.get("/")
def homepage():
    return render_template_string(HOMEPAGE, fields=discover_pages())


@app.get("/<path:filepath>")
def static_files(filepath: str):
    return send_from_directory(ROOT, filepath)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"Learning Navigator running at http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
