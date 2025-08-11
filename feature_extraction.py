# import cv2
# import numpy as np

# def get_skin_tone(frame, x, y, w, h):
#     face_roi = frame[y:y+h, x:x+w]

#     if face_roi.size == 0:
#         return None, None  # No face region

#     # Convert to YCrCb for skin detection
#     ycrcb = cv2.cvtColor(face_roi, cv2.COLOR_BGR2YCrCb)

#     # Equalize lighting in Y channel
#     y, cr, cb = cv2.split(ycrcb)
#     y_eq = cv2.equalizeHist(y)
#     ycrcb_eq = cv2.merge((y_eq, cr, cb))

#     # Skin mask
#     lower = np.array([0, 133, 77], dtype=np.uint8)
#     upper = np.array([255, 173, 127], dtype=np.uint8)
#     mask = cv2.inRange(ycrcb_eq, lower, upper)
#     mask = cv2.medianBlur(mask, 5)

#     # Extract skin pixels
#     skin_pixels = face_roi[mask > 0]
#     if len(skin_pixels) == 0:
#         return None, None

#     # Remove extreme pixels
#     skin_pixels = np.array(skin_pixels, dtype=np.float32)
#     lower_bound = np.percentile(skin_pixels, 5, axis=0)
#     upper_bound = np.percentile(skin_pixels, 95, axis=0)
#     filtered_pixels = skin_pixels[
#         np.all(skin_pixels >= lower_bound, axis=1) &
#         np.all(skin_pixels <= upper_bound, axis=1)
#     ]

#     if len(filtered_pixels) == 0:
#         return None, None

#     # Average BGR color
#     avg_color_bgr = np.mean(filtered_pixels, axis=0).astype(int)

#     # Convert to LAB for brightness classification
#     lab = cv2.cvtColor(np.uint8([[avg_color_bgr]]), cv2.COLOR_BGR2LAB)
#     L, A, B = lab[0][0]

#     # Classify lightness
#     if L > 180:
#         tone = "Fair"
#     elif L > 140:
#         tone = "Medium"
#     else:
#         tone = "Deep"

#     # Map to descriptive tone name
#     descriptive_name = map_to_descriptive_name(avg_color_bgr, tone)

#     return descriptive_name, tuple(int(c) for c in avg_color_bgr)


# def map_to_descriptive_name(bgr_color, tone):
#     """Maps average skin tone BGR values to a human-readable name."""
#     b, g, r = bgr_color

#     if tone == "Fair":
#         if r > g and r > b:
#             return "Light Peach"
#         elif g > r and g > b:
#             return "Ivory"
#         else:
#             return "Light Beige"

#     elif tone == "Medium":
#         if r > g and r > b:
#             return "Golden Beige"
#         elif g > r and g > b:
#             return "Olive Tan"
#         else:
#             return "Warm Sand"

#     else:  # Deep
#         if r > g and r > b:
#             return "Deep Mahogany"
#         elif g > r and g > b:
#             return "Rich Espresso"
#         else:
#             return "Chocolate Brown"


import cv2
import numpy as np

def get_skin_tone(frame, x, y, w, h):
    face_roi = frame[y:y+h, x:x+w]

    if face_roi.size == 0:
        return None, None, None

    # Convert to LAB for consistent skin tone detection
    lab = cv2.cvtColor(face_roi, cv2.COLOR_BGR2LAB)
    avg_lab = np.mean(lab.reshape(-1, 3), axis=0)  # Mean LAB color
    L, A, B = avg_lab

    # Classify tone
    if L > 180:
        tone = "Fair"
    elif L > 140:
        tone = "Medium"
    else:
        tone = "Deep"

    # Classify undertone
    if A > 140 and B > 140:
        undertone = "Warm"
    elif A < 120 and B < 120:
        undertone = "Cool"
    else:
        undertone = "Neutral"

    return tone, undertone, avg_lab

def delta_e(lab1, lab2):
    """Calculate perceptual difference between two LAB colors."""
    return np.linalg.norm(np.array(lab1) - np.array(lab2))
