import json

def generate_html(input_file="json_txt.json", output_file="notes.html"):
    """
    Reads notes.json and generates a simple HTML notes page.
    """

    # Read JSON
    with open(input_file, "r", encoding="utf-8") as file:
        notes = json.load(file)

    # Start HTML
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{notes.get("title", "Notes")}</title>
    <link rel="stylesheet" href="styles/style.css">
</head>
<body>

<header>
    <h1>{notes.get("title", "Notes")}</h1>
    <p>{notes.get("overview", "")}</p>
</header>

<div class="container">
    <aside class="sidebar">
        <h2>📚 Topics</h2>
        <ul>
"""

    # Automatically generate sidebar links
    for i, section in enumerate(notes.get("sections", []), start=1):
        html += f"""
            <li>
                <a href="#section{i}">{section.get("heading", f"Section {i}")}</a>
            </li>
"""

    html += """
        </ul>
    </aside>

    <main class="content">
"""

    # ---------------- Sections ----------------
    for i, section in enumerate(notes.get("sections", []), start=1):
        html += f"""
        <div class="card" id="section{i}">
            <h2>📘 {section.get("heading", "")}</h2>
            <p>{section.get("content", "")}</p>
        </div>
"""

    # ---------------- Key Points ----------------
    if "key_points" in notes:
        html += """
        <div class="card">
            <h2>🧠 Key Points</h2>
            <ul>
"""
        for point in notes["key_points"]:
            html += f"                <li>{point}</li>\n"
        
        html += """
            </ul>
        </div>
"""

    # ---------------- Definitions ----------------
    if "definitions" in notes:
        html += """
        <div class="card">
            <h2>💡 Definitions</h2>
"""
        for definition in notes["definitions"]:
            html += f"""
            <h3>{definition.get("term", "")}</h3>
            <p>{definition.get("meaning", "")}</p>
"""
        html += """
        </div>
"""

    # ---------------- Examples ----------------
    if "examples" in notes:
        html += """
        <div class="card">
            <h2>📌 Examples</h2>
            <ul>
"""
        for example in notes["examples"]:
            html += f"                <li>{example}</li>\n"
            
        html += """
            </ul>
        </div>
"""

    # ---------------- Important Terms ----------------
    if "important_terms" in notes:
        html += """
        <div class="card">
            <h2>🏷️ Important Terms</h2>
            <div class="badge-container">
"""
        for term in notes["important_terms"]:
            html += f"""
                <span class="badge">{term}</span>
"""
        html += """
            </div>
        </div>
"""

    # ---------------- Code Snippets / Learning Assets ----------------
    if "learning_assets" in notes:
        html += """
        <div class="card">
            <h2>🎯 Learning Assets</h2>
"""
        for asset in notes["learning_assets"]:
            html += f"""
            <h3>{asset.get("title", "")}</h3>
            <p><b>Type:</b> {asset.get("type", "")}</p>
            <pre><code>{asset.get("content", "")}</code></pre>
"""
        html += "        </div>\n"

    # ---------------- Common Mistakes ----------------
    if "common_mistakes" in notes:
        html += """
        <div class="card">
            <h2>⚠ Common Mistakes</h2>
            <ul>
"""
        for mistake in notes["common_mistakes"]:
            html += f"                <li>{mistake}</li>\n"
            
        html += """
            </ul>
        </div>
"""

    # ---------------- Summary ----------------
    if "summary" in notes:
        html += f"""
        <div class="card">
            <h2>📝 Quick Revision</h2>
            <p>{notes["summary"]}</p>
        </div>
"""

    # Finish HTML
    html += """
    </main>
</div>
</body>
</html>
"""

    # Save HTML
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(html)

    print(f"✅ HTML saved as '{output_file}'")


if __name__ == "__main__":
    generate_html()