import cv2
import pandas as pd
import numpy as np
import os
import sqlite3
from datetime import datetime
import uuid
from camera import get_camera_stream
from face_detection import detect_faces
from feature_extraction import get_skin_tone, delta_e

# --- Database Setup ---
os.makedirs("db", exist_ok=True)
conn = sqlite3.connect("db/session_data.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS detections (
    id TEXT PRIMARY KEY,
    session_id TEXT,
    tone TEXT,
    undertone TEXT,
    L REAL, A REAL, B REAL,
    product_name TEXT,
    price REAL,
    timestamp TEXT
)
""")
conn.commit()

# Load products database
products = pd.read_csv("products.csv")

def color_distance(c1, c2):
    return np.linalg.norm(np.array(c1) - np.array(c2))

# Session tracking
session_id = uuid.uuid4().hex[:8]
last_tone_lab = None

cap = get_camera_stream()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    faces = detect_faces(frame)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        tone, undertone, avg_lab = get_skin_tone(frame, x, y, w, h)

        if tone and undertone:
            cv2.putText(frame, f"{tone}, {undertone}", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            # --- Only log if significant change ---
            if last_tone_lab is None or delta_e(avg_lab, last_tone_lab) > 5:
                last_tone_lab = avg_lab

                # Filter by undertone first
                filtered = products[products["undertone"] == undertone]
                if not len(filtered):
                    filtered = products

                # Rank by color distance
                filtered["distance"] = filtered.apply(
                    lambda row: color_distance(avg_lab,
                        [row.target_L, row.target_A, row.target_B]),
                    axis=1
                )
                filtered = filtered.sort_values("distance")
                top3 = filtered.head(3)

                # Show top3 in frame
                y_offset = y + h + 20
                for idx, row in top3.iterrows():
                    cv2.putText(frame,
                                f"{row.product_name} (${row.price})",
                                (x, y_offset),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                (0, 255, 0), 2)
                    y_offset += 20

                # Save top1 to DB
                best_match = top3.iloc[0]
                cursor.execute("""
                    INSERT INTO detections
                    (id, session_id, tone, undertone, L, A, B, product_name, price, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    uuid.uuid4().hex[:8], session_id, tone, undertone,
                    avg_lab[0], avg_lab[1], avg_lab[2],
                    best_match.product_name, best_match.price,
                    datetime.now().isoformat()
                ))
                conn.commit()

    cv2.imshow("E-commerce Skin Tone Recommender", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC to quit
        break

cap.release()
cv2.destroyAllWindows()
conn.close()
