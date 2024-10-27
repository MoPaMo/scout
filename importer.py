import sqlite3
import json
import csv
import os
import re

# Database connection
conn = sqlite3.connect('sqlite3.db')
cursor = conn.cursor()

# Utility to identify lecture and part number
def parse_lecture_info(filename):
    lecture_match = re.search(r"Vorlesung (\d+)", filename)
    part_match = re.search(r"Teil (\d+)", filename)
    lecture_number = int(lecture_match.group(1)) if lecture_match else None
    part_number = int(part_match.group(1)) if part_match else None
    return lecture_number, part_number

# Insert meta data
def insert_meta_data(meta_data, lecture_number, part_number, given_name):
    cursor.execute('''
        INSERT INTO lectures (titel, thema, tags, wichtig, lecture_number, part_number, given_name)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        meta_data["titel"],
        meta_data["thema"],
        json.dumps(meta_data["tags"]),
        json.dumps(meta_data["wichtig"]),
        lecture_number,
        part_number,
        given_name
    ))
    return cursor.lastrowid

# Insert timestamped data
def insert_timestamped_data(lecture_id, timestamped_file):
    print(f"Inserting timestamped data from {timestamped_file} for lecture_id {lecture_id}")
    try:
        with open(timestamped_file, 'r') as file:
            if timestamped_file.endswith('.csv'):
                reader = csv.reader(file, delimiter=';')
                next(reader, None)  # Skip headers if present
                for row in reader:
                    if len(row) < 3:
                        print(f"Skipping incomplete row in CSV: {row}")
                        continue
                    start_time, end_time, text = row
                    cursor.execute('''
                        INSERT INTO lecture_excerpts (lecture_id, text, start_time, end_time)
                        VALUES (?, ?, ?, ?)
                    ''', (lecture_id, text, start_time, end_time))
            elif timestamped_file.endswith('.json'):
                data = json.load(file)
                for entry in data:
                    cursor.execute('''
                        INSERT INTO lecture_excerpts (lecture_id, text, start_time, end_time)
                        VALUES (?, ?, ?, ?)
                    ''', (lecture_id, entry["Transcript"], entry["Start Timestamp"], entry["End Timestamp"]))
    except Exception as e:
        print(f"Failed to insert timestamped data from {timestamped_file}: {e}")

# Directory paths
meta_path = 'data/meta'
timestamped_path = 'data/timestamped'

# Process files
for meta_file in os.listdir(meta_path):
    if meta_file.endswith('.json'):
        with open(os.path.join(meta_path, meta_file), 'r') as f:
            meta_data = json.load(f)

        given_name = meta_data["titel"]
        lecture_number, part_number = parse_lecture_info(meta_file)

        # Insert metadata
        lecture_id = insert_meta_data(meta_data, lecture_number, part_number, given_name)

        # Construct flexible matching pattern
        base_pattern = re.sub(r"[^\w\s]", "", meta_file.split('.')[0]).replace("Zusammenfassung", "").strip()
        print(f"Searching for timestamped files matching: '{base_pattern}'")

        # Find matching timestamped file
        matched_files = [
            f for f in os.listdir(timestamped_path)
            if base_pattern in re.sub(r"[^\w\s]", "", f).strip()
        ]

        # Insert timestamped data from all matched files
        if matched_files:
            for timestamped_file in matched_files:
                insert_timestamped_data(lecture_id, os.path.join(timestamped_path, timestamped_file))
        else:
            print(f"No timestamped file found for {meta_file}")

# Commit and close the connection
conn.commit()
conn.close()
