import logging
import os

from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, render_template, request
from flask_cors import CORS
from sqlalchemy import text

from backend.database import get_session, init_app
from backend.interval_store import IntervalStore
from backend.pipeline import STATUS_FAILED, STATUS_PENDING, STATUS_READY, compute_video_analysis
from logging_config import configure_logging
from youtube_url import YouTubeUrlError, parse_video_id

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
configure_logging()

logger = logging.getLogger(__name__)


app = Flask(__name__)

CORS(
    app,
    resources={
        r"/api/*": {
            "origins": [
                origin.strip()
                for origin in os.getenv(
                    "CORS_ORIGINS",
                    "https://www.youtube.com",
                ).split(",")
                if origin.strip()
            ],
            "methods": ["GET", "OPTIONS"],
        }
    },
)
init_app(app)


@app.route("/", methods=["GET"])
def root():
    return render_template("index.html")


def _parse_link_param():
    try:
        return parse_video_id(request.args.get("link")), None
    except YouTubeUrlError as exc:
        logger.warning("Invalid link parameter: %s", exc)
        return None, (jsonify({"error": str(exc)}), 400)


@app.route("/api/v2/timestamps", methods=["GET"])
def api_search_v2():
    video_id, error = _parse_link_param()
    if error:
        return error

    retry = request.args.get("retry", "").lower() in ("1", "true", "yes")
    logger.info(
        "timestamps request video_id=%s retry=%s",
        video_id,
        retry,
    )
    store = IntervalStore(get_session())
    result = store.request_intervals(
        video_id,
        lambda: compute_video_analysis(video_id),
        retry=retry,
    )
    status_code = 202 if result["status"] == STATUS_PENDING else 200
    if result["status"] == STATUS_READY:
        logger.info(
            "timestamps ready video_id=%s interval_count=%d",
            video_id,
            len(result.get("intervals", [])),
        )
    elif result["status"] == STATUS_FAILED:
        logger.warning(
            "timestamps failed video_id=%s error=%s",
            video_id,
            result.get("error"),
        )
    else:
        logger.info("timestamps pending video_id=%s", video_id)
    return jsonify(result), status_code


@app.route("/health", methods=["GET"])
def health():
    try:
        get_session().execute(text("SELECT 1"))
        return jsonify({"status": "ok"}), 200
    except Exception as exc:
        logger.error("Health check failed: %s", exc)
        return jsonify({"status": "error", "error": str(exc)}), 503


@app.route("/api/test", methods=["GET"])
def api_test():
    response = make_response(jsonify({"status": "success"}), 200)
    return response
