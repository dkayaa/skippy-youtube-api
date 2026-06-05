from flask import Flask, render_template, request, jsonify, make_response
from dotenv import load_dotenv
import os
from flask_cors import CORS

from backend.database import get_session, init_app
from backend.interval_store import IntervalStore
from backend.pipeline import STATUS_PENDING, compute_video_analysis
from youtube_url import YouTubeUrlError, parse_video_id

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))


app = Flask(__name__)

# TO DO : Proper CORS headers
CORS(app)
init_app(app)


@app.route("/", methods=["GET"])
def root():
    return render_template("index.html")


def _parse_link_param():
    try:
        return parse_video_id(request.args.get("link")), None
    except YouTubeUrlError as exc:
        return None, (jsonify({"error": str(exc)}), 400)


@app.route("/api/v2/timestamps", methods=["GET"])
def api_search_v2():
    video_id, error = _parse_link_param()
    if error:
        return error

    retry = request.args.get("retry", "").lower() in ("1", "true", "yes")
    store = IntervalStore(get_session())
    result = store.request_intervals(
        video_id,
        lambda: compute_video_analysis(video_id),
        retry=retry,
    )
    status_code = 202 if result["status"] == STATUS_PENDING else 200
    return jsonify(result), status_code


@app.route("/api/test", methods=["GET"])
def api_test():
    response = make_response(jsonify({"status": "success"}), 200)
    return response
