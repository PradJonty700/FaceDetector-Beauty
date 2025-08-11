import sqlite3

# Connect to the database
conn = sqlite3.connect("db/session_data.db")
cursor = conn.cursor()

# Show all rows from the detections table
cursor.execute("SELECT * FROM detections")
rows = cursor.fetchall()

# Print them
for row in rows:
    print(row)

conn.close()
