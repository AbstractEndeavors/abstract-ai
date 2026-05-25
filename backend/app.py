import threading
import time

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ── INSTRUCTION_KEYS (mirrors schemas.py) ────────────────────────────────────

INSTRUCTION_KEYS = [
    "instructions",
    "additional_responses",
    "suggestions",
    "abort",
    "database_query",
    "notation",
    "generate_title",
    "additional_instruction",
    "request_chunks",
    "prompt_as_previous",
    "token_adjustment",
]

# ── Global state ──────────────────────────────────────────────────────────────

_state_lock = threading.Lock()

_state = {
    "request": "",
    "prompt_data": "",
    "chunk_data": "",
    "query": "",
    "instructions_text": "",
    "instruction_bools": {k: False for k in INSTRUCTION_KEYS},
    "header": "",
    "api_key": "",
    "api_env": "",
    "endpoint": "",
    "model": {
        "model_name": "",
        "endpoint": "",
        "max_tokens": 0,
    },
    "models": [],
    "role": "",
    "response_type": "",
    "prompt_percentage": 50,
    "completion_percentage": 50,
    "progress": {
        "total_chunks": 0,
        "current_chunk": 0,
        "done": True,
        "status_text": "Awaiting Prompt",
        "percentage": 0,
        "query_count": 0,
    },
    "urls": [],
    "query_results": [],
    "title": "",
    "collate_responses": False,
    "json_to_string": False,
    "test_run": False,
    "test_files": False,
    "scan_mode_all": False,
    "auto_chunk_title": False,
    "reuse_chunk_data": False,
    "append_chunks": False,
    "response_key_options": [],
    "feedback": {
        "request_chunks": "",
        "abort": "",
        "additional_responses": "",
        "suggestions": "",
        "notation": "",
        "other": "",
    },
    "current_response": "",
    "tracker": {
        "instructions": 0,
        "request": 0,
        "prompt_data": 0,
        "chunk": 0,
        "query": 0,
        "chunk_number": 0,
    },
    "chunk_title": "",
    "url_text": "",
}

# ── Manager cache ─────────────────────────────────────────────────────────────

_managers = {}
_managers_initialized = False


def get_managers():
    global _managers, _managers_initialized
    if _managers_initialized:
        return _managers if _managers else None

    _managers_initialized = True
    try:
        import sys
        import os
        src_path = os.path.join(os.path.dirname(__file__), "..", "src")
        if src_path not in sys.path:
            sys.path.insert(0, src_path)

        from abstract_ai import (
            ApiManager,
            ModelManager,
            PromptManager,
            InstructionManager,
            ResponseManager,
        )

        model_mgr = ModelManager(default_selection=True)
        api_mgr = ApiManager()
        instruction_mgr = InstructionManager()
        instruction_data = [
            {
                "bool_values": {"api_response": True},
                "text_values": {"api_response": "place response to prompt here"},
                "text": "",
            }
        ]
        prompt_mgr = PromptManager(
            instruction_mgr=instruction_mgr,
            model_mgr=model_mgr,
            instruction_data=instruction_data,
        )
        response_mgr = ResponseManager(
            prompt_mgr=prompt_mgr,
            api_mgr=api_mgr,
        )

        _managers = {
            "api": api_mgr,
            "model": model_mgr,
            "prompt": prompt_mgr,
            "instruction": instruction_mgr,
            "response": response_mgr,
        }

        # seed state with model info
        with _state_lock:
            _state["model"]["model_name"] = model_mgr.selected_model_name or ""
            _state["model"]["endpoint"] = model_mgr.selected_endpoint or ""
            _state["model"]["max_tokens"] = model_mgr.selected_max_tokens or 0
            _state["models"] = model_mgr.all_model_names or []

        return _managers

    except ImportError:
        _managers = {}
        return None


# ── Helpers ───────────────────────────────────────────────────────────────────

def state_snapshot():
    with _state_lock:
        import copy
        return copy.deepcopy(_state)


def update_state(patch: dict):
    with _state_lock:
        for key, value in patch.items():
            if key in _state:
                _state[key] = value
    return state_snapshot()


# ── Background submit thread ──────────────────────────────────────────────────

def _run_submit_real(managers, snapshot):
    try:
        with _state_lock:
            _state["progress"]["done"] = False
            _state["progress"]["status_text"] = "Submitting…"
            _state["progress"]["percentage"] = 0

        # Best-effort: delegate to response manager
        response_mgr = managers.get("response")
        if response_mgr and hasattr(response_mgr, "submit"):
            result = response_mgr.submit()
        else:
            result = None

        with _state_lock:
            _state["progress"]["done"] = True
            _state["progress"]["status_text"] = "Done"
            _state["progress"]["percentage"] = 100
            _state["progress"]["query_count"] += 1
            if result is not None:
                _state["query_results"].append(str(result))

    except Exception as exc:
        with _state_lock:
            _state["progress"]["done"] = True
            _state["progress"]["status_text"] = f"Error: {exc}"
            _state["progress"]["percentage"] = 0


def _run_submit_simulated():
    steps = [
        (10, "Preparing request…"),
        (30, "Chunking prompt…"),
        (60, "Calling API…"),
        (90, "Processing response…"),
        (100, "Done"),
    ]
    with _state_lock:
        _state["progress"]["done"] = False
        _state["progress"]["status_text"] = "Starting…"
        _state["progress"]["percentage"] = 0

    for pct, text in steps:
        time.sleep(0.4)
        with _state_lock:
            _state["progress"]["percentage"] = pct
            _state["progress"]["status_text"] = text

    with _state_lock:
        _state["progress"]["done"] = True
        _state["progress"]["query_count"] += 1
        _state["query_results"].append("[simulated response] abstract_ai not available")


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/api/state", methods=["GET"])
def get_state():
    return jsonify(state_snapshot())


@app.route("/api/state", methods=["POST"])
def post_state():
    try:
        body = request.get_json(force=True) or {}
        snapshot = update_state(body)
        return jsonify(snapshot)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/models", methods=["GET"])
def get_models():
    try:
        managers = get_managers()
        if managers:
            model_mgr = managers.get("model")
            models = model_mgr.all_model_names if model_mgr else []
        else:
            models = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "gpt-4o"]
        return jsonify({"models": models})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/model/select", methods=["POST"])
def select_model():
    try:
        body = request.get_json(force=True) or {}
        model_name = body.get("model_name", "")

        endpoint = ""
        max_tokens = 0

        managers = get_managers()
        if managers:
            model_mgr = managers.get("model")
            if model_mgr:
                endpoint = model_mgr._get_endpoint_by_model(model_name) or ""
                max_tokens = model_mgr._get_max_tokens_by_model(model_name) or 0

        with _state_lock:
            _state["model"]["model_name"] = model_name
            _state["model"]["endpoint"] = endpoint
            _state["model"]["max_tokens"] = max_tokens

        return jsonify({"model": _state["model"]})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/submit", methods=["POST"])
def submit_query():
    try:
        body = request.get_json(force=True) or {}
        update_state({k: v for k, v in body.items() if k in _state})

        managers = get_managers()
        snapshot = state_snapshot()

        if managers:
            t = threading.Thread(
                target=_run_submit_real,
                args=(managers, snapshot),
                daemon=True,
            )
        else:
            t = threading.Thread(target=_run_submit_simulated, daemon=True)

        t.start()
        return jsonify({"status": "submitted"})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/progress", methods=["GET"])
def get_progress():
    with _state_lock:
        import copy
        return jsonify(copy.deepcopy(_state["progress"]))


@app.route("/api/clear/requests", methods=["POST"])
def clear_requests():
    try:
        with _state_lock:
            _state["request"] = ""
            _state["prompt_data"] = ""
            _state["tracker"]["request"] = 0
            _state["tracker"]["prompt_data"] = 0
        return jsonify(state_snapshot())
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/clear/chunks", methods=["POST"])
def clear_chunks():
    try:
        with _state_lock:
            _state["chunk_data"] = ""
        return jsonify(state_snapshot())
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/urls/add", methods=["POST"])
def add_url():
    try:
        body = request.get_json(force=True) or {}
        url = body.get("url", "").strip()
        if url:
            with _state_lock:
                if url not in _state["urls"]:
                    _state["urls"].append(url)
                urls = list(_state["urls"])
        else:
            with _state_lock:
                urls = list(_state["urls"])
        return jsonify({"urls": urls})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/urls", methods=["DELETE"])
def delete_url():
    try:
        body = request.get_json(force=True) or {}
        url = body.get("url", "")
        with _state_lock:
            _state["urls"] = [u for u in _state["urls"] if u != url]
            urls = list(_state["urls"])
        return jsonify({"urls": urls})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/urls/fetch", methods=["POST"])
def fetch_url():
    try:
        body = request.get_json(force=True) or {}
        url = body.get("url", "")
        fetch_type = body.get("type", "source")

        content = ""

        try:
            from abstract_webtools import get_page_content
            content = get_page_content(url) or ""
        except ImportError:
            try:
                import requests as req_lib
                resp = req_lib.get(url, timeout=10)
                resp.raise_for_status()
                if fetch_type == "soup":
                    try:
                        from bs4 import BeautifulSoup
                        content = BeautifulSoup(resp.text, "html.parser").get_text()
                    except ImportError:
                        content = resp.text
                else:
                    content = resp.text
            except Exception as fetch_exc:
                content = f"Error fetching URL: {fetch_exc}"

        with _state_lock:
            _state["url_text"] = content

        return jsonify({"content": content})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/nav/tracker", methods=["POST"])
def nav_tracker():
    try:
        body = request.get_json(force=True) or {}
        key = body.get("key", "")
        value = body.get("value", 0)
        with _state_lock:
            if key in _state["tracker"]:
                _state["tracker"][key] = int(value)
            tracker = dict(_state["tracker"])
        return jsonify(tracker)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/generate/readme", methods=["POST"])
def generate_readme():
    return jsonify({"status": "ok", "message": "README generation not yet implemented"})


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, port=5000)
