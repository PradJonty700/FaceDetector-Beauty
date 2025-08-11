# # app.py
# from flask import Flask, jsonify, send_from_directory, render_template, request
# from flask_cors import CORS
# import sqlite3
# import os
# import pandas as pd

# DB_PATH = "db/session_data.db"

# app = Flask(__name__, static_folder="static", template_folder="templates")
# CORS(app)

# def get_db_connection():
#     if not os.path.exists(DB_PATH):
#         raise FileNotFoundError(f"Database not found at {DB_PATH}")
#     conn = sqlite3.connect(DB_PATH)
#     conn.row_factory = sqlite3.Row
#     return conn

# @app.route("/")
# def index():
#     return render_template("index.html")

# @app.route("/api/sessions", methods=["GET"])
# def api_sessions():
#     """Return all detections, optionally filtered by tone/undertone."""
#     tone = request.args.get("tone")
#     undertone = request.args.get("undertone")
#     conn = get_db_connection()
#     df = pd.read_sql_query("SELECT * FROM detections ORDER BY timestamp DESC", conn)
#     conn.close()

#     if tone:
#         df = df[df["tone"] == tone]
#     if undertone:
#         df = df[df["undertone"] == undertone]

#     records = df.to_dict(orient="records")
#     return jsonify(records)

# @app.route("/api/sessions/<session_id>", methods=["GET"])
# def api_session(session_id):
#     conn = get_db_connection()
#     df = pd.read_sql_query("SELECT * FROM detections WHERE session_id = ? ORDER BY timestamp DESC", conn, params=(session_id,))
#     conn.close()
#     return jsonify(df.to_dict(orient="records"))

# @app.route("/api/summary", methods=["GET"])
# def api_summary():
#     """Return aggregated stats: counts per tone and top products."""
#     conn = get_db_connection()
#     df = pd.read_sql_query("SELECT * FROM detections", conn)
#     conn.close()
#     if df.empty:
#         return jsonify({"total": 0, "by_tone": {}, "top_products": []})

#     total = len(df)
#     by_tone = df["tone"].value_counts().to_dict()
#     top_products = df["product_name"].value_counts().head(10).to_dict()
#     return jsonify({"total": total, "by_tone": by_tone, "top_products": top_products})

# # Optional: serve product images if you add them to static/images/
# @app.route("/images/<path:filename>")
# def images(filename):
#     return send_from_directory(os.path.join(app.static_folder, "images"), filename)

# if __name__ == "__main__":
#     app.run(debug=True)
