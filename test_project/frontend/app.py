import os

import requests
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8080")


@app.route("/")
def index():
    notes = []
    error = None
    try:
        resp = requests.get(f"{BACKEND_URL}/api/notes", timeout=5)
        resp.raise_for_status()
        notes = resp.json()
    except requests.RequestException as exc:
        error = f"Go backend недоступен: {exc}"

    current = request.args.get("note_id", type=int)
    selected = next((n for n in notes if n["id"] == current), None)
    return render_template("index.html", notes=notes, selected=selected, error=error)


@app.route("/notes", methods=["POST"])
def add_note():
    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()
    if title:
        try:
            requests.post(
                f"{BACKEND_URL}/api/notes",
                json={"title": title, "content": content},
                timeout=5,
            ).raise_for_status()
        except requests.RequestException:
            pass
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)