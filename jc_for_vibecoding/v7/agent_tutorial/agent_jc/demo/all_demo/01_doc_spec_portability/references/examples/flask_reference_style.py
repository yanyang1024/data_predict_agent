from __future__ import annotations

from flask import Flask, render_template, request


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

    @app.get("/")
    def index():
        return render_template("index.html", result=None, error=None)

    @app.post("/analyze")
    def analyze():
        upload = request.files.get("csv_file")
        if upload is None:
            return render_template("index.html", result=None, error="Please choose a CSV file.")
        return render_template("index.html", result={"filename": upload.filename}, error=None)

    return app

