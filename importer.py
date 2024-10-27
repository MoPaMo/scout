import json
import csv
import sqlite3
import os
import re
from pathlib import Path

def connect_to_db(db_path):
    """Create a connection to the SQLite database."""
    return sqlite3.connect(db_path)

def parse_filename(filename):
    """Parse lecture number, part number, and given name from filename with flexible pattern matching."""
    # Pattern that handles both formats:
    # 1. "Vorlesung X - Teil Y - Name"
    # 2. "Zusammenfassung - Vorlesung X - Teil Y - Name"
    patterns = [
        r"(?:Zusammenfassung\s*-\s*)?Vorlesung\s*(\d+)\s*-\s*Teil\s*(\d+)\s*-\s*(.+)",
        r"Vorlesung\s*(\d+)\s*-\s*Teil\s*(\d+)\s*-\s*(.+)"
    ]
    
    for pattern in patterns:
        match = re.match(pattern, filename)
        if match:
            lecture_num = int(match.group(1))
            part_num = int(match.group(2))
            given_name = match.group(3).strip()
            return lecture_num, part_num, given_name
    
    # If none of the patterns match, try to extract information from any format
    # that contains the required information
    lecture_match = re.search(r'Vorlesung\s*(\d+)', filename)
    part_match = re.search(r'Teil\s*(\d+)', filename)
    
    if lecture_match and part_match:
        lecture_num = int(lecture_match.group(1))
        part_num = int(part_match.group(1))
        
        # Extract the name by removing known parts
        name_parts = filename.split('-')
        # Take the last part as the name, or if no parts, use the whole string
        given_name = name_parts[-1].strip() if len(name_parts) > 0 else filename
        
        # Clean up the name by removing any "Vorlesung X" or "Teil Y" remnants
        given_name = re.sub(r'Vorlesung\s*\d+', '', given_name)
        given_name = re.sub(r'Teil\s*\d+', '', given_name)
        given_name = given_name.strip(' -')
        
        return lecture_num, part_num, given_name
    
    raise ValueError(f"Filename '{filename}' doesn't match any expected pattern")

def process_meta_file(file_path):
    """Process a JSON metadata file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        # Convert lists to string representation for storage
        data['tags'] = json.dumps(data['tags'], ensure_ascii=False)
        data['wichtig'] = json.dumps(data['wichtig'], ensure_ascii=False)
        
        # Parse filename components
        filename = file_path.stem
        try:
            lecture_num, part_num, given_name = parse_filename(filename)
        except ValueError as e:
            print(f"Warning: {str(e)}")
            print(f"Attempting to continue with default values...")
            lecture_num = 0
            part_num = 0
            given_name = filename
        
        return {
            'lecture_number': lecture_num,
            'part_number': part_num,
            'given_name': given_name,
            'titel': data['titel'],
            'thema': data['thema'],
            'tags': data['tags'],
            'wichtig': data['wichtig']
        }

def process_timestamped_file(file_path, lecture_id):
    """Process a CSV timestamped file."""
    excerpts = []
    with open(file_path, 'r', encoding='utf-8') as f:
        # Skip header
        next(f)
        csv_reader = csv.reader(f, delimiter=';', quotechar='"')
        for row in csv_reader:
            if len(row) >= 3:  # Ensure we have all required fields
                start_time, end_time, text = row[0], row[1], row[2]
                excerpts.append({
                    'lecture_id': lecture_id,
                    'start_time': start_time,
                    'end_time': end_time,
                    'text': text
                })
    return excerpts

def import_data(db_path, data_dir):
    """Main import function."""
    conn = connect_to_db(db_path)
    cursor = conn.cursor()
    
    # Process meta directory
    meta_dir = Path(data_dir) / 'meta'
    timestamped_dir = Path(data_dir) / 'timestamped'
    
    try:
        # Process each meta file
        for meta_file in meta_dir.glob('*.json'):
            # Get base name without extension to match with timestamped file
            base_name = meta_file.stem
            
            # Process meta data
            meta_data = process_meta_file(meta_file)
            
            # Insert into lectures table with new fields
            cursor.execute('''
                INSERT INTO lectures (
                    lecture_number,
                    part_number,
                    given_name,
                    titel,
                    thema,
                    tags,
                    wichtig
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                meta_data['lecture_number'],
                meta_data['part_number'],
                meta_data['given_name'],
                meta_data['titel'],
                meta_data['thema'],
                meta_data['tags'],
                meta_data['wichtig']
            ))
            
            lecture_id = cursor.lastrowid
            
            # Look for corresponding timestamped file
            timestamped_file = next(timestamped_dir.glob(f'{base_name}.*'), None)
            
            if timestamped_file:
                excerpts = process_timestamped_file(timestamped_file, lecture_id)
                
                # Insert excerpts
                for excerpt in excerpts:
                    cursor.execute('''
                        INSERT INTO lecture_excerpts (lecture_id, text, start_time, end_time)
                        VALUES (?, ?, ?, ?)
                    ''', (
                        excerpt['lecture_id'],
                        excerpt['text'],
                        excerpt['start_time'],
                        excerpt['end_time']
                    ))
        
        conn.commit()
        print("Data import completed successfully")
        
    except Exception as e:
        conn.rollback()
        print(f"Error during import: {str(e)}")
        raise
    
    finally:
        conn.close()

if __name__ == "__main__":
    DB_PATH = "sqlite3.db"
    DATA_DIR = "data"
    
    import_data(DB_PATH, DATA_DIR)