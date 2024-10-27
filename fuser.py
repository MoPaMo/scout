import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('sqlite3.db')
cursor = conn.cursor()

# Create a new table to store fused excerpts
cursor.execute('''
    CREATE TABLE IF NOT EXISTS fused_lecture_excerpts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lecture_id INTEGER,
        text TEXT,
        start_time TEXT,
        end_time TEXT
    )
''')
conn.commit()

# Fetch all rows ordered by lecture_id and start_time
cursor.execute("SELECT lecture_id, text, start_time, end_time FROM lecture_excerpts ORDER BY lecture_id, start_time")
rows = cursor.fetchall()

# List to store the final sentences
fused_sentences = []
current_text = ""
current_start_time = None
current_lecture_id = None

for i, row in enumerate(rows):
    lecture_id, text, start_time, end_time = row
    
    # If this is a new lecture, finalize the previous sentence
    if current_lecture_id is not None and lecture_id != current_lecture_id:
        if current_text:
            fused_sentences.append((current_lecture_id, current_text.strip(), current_start_time, end_time))
        current_text = ""
        current_start_time = None

    # Update lecture ID
    current_lecture_id = lecture_id

    # Check if the current row represents a complete sentence
    if text.endswith(('.', '?', '!')):
        # If it's a complete sentence, append the previous incomplete one if exists
        if current_text:
            fused_sentences.append((lecture_id, current_text.strip(), current_start_time, end_time))
            current_text = ""
            current_start_time = None
        # Add the complete sentence directly
        fused_sentences.append((lecture_id, text.strip(), start_time, end_time))
    else:
        # Otherwise, add the text to the ongoing sentence
        if not current_text:
            current_start_time = start_time
        current_text += " " + text if current_text else text

# Insert any remaining incomplete text as a new entry if it exists
if current_text:
    fused_sentences.append((current_lecture_id, current_text.strip(), current_start_time, end_time))

# Insert the fused sentences into the new table
cursor.executemany('''
    INSERT INTO fused_lecture_excerpts (lecture_id, text, start_time, end_time)
    VALUES (?, ?, ?, ?)
''', fused_sentences)

conn.commit()
conn.close()
