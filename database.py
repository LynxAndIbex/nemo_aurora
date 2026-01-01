import sqlite3
import json
from datetime import datetime
import os

DB_PATH = "aurora_memories.db"

def init_database():
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            summary TEXT,
            transcription TEXT,
            tags TEXT,
            emotional_tone TEXT,
            audio_url TEXT,
            memory_date TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

def save_memory(title, summary, transcription, tags, emotional_tone, audio_url=None, memory_date=None):
    """Save a new memory to the database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    tags_json = json.dumps(tags) if isinstance(tags, list) else tags
   
    if not memory_date:
        memory_date = datetime.now().strftime("%Y-%m-%d")
    
    cursor.execute("""
        INSERT INTO memories (title, summary, transcription, tags, emotional_tone, audio_url, memory_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (title, summary, transcription, tags_json, emotional_tone, audio_url, memory_date))
    
    memory_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    print(f"Memory saved with ID: {memory_id}")
    return memory_id

def get_all_memories():
    """Get all memories, ordered by date"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM memories ORDER BY memory_date DESC")
    rows = cursor.fetchall()
    conn.close()
    
    memories = []
    for row in rows:
        memory = {
            "id": row[0],
            "title": row[1],
            "summary": row[2],
            "transcription": row[3],
            "tags": json.loads(row[4]) if row[4] else [],
            "emotional_tone": row[5],
            "audio_url": row[6],
            "memory_date": row[7],
            "created_at": row[8]
        }
        memories.append(memory)
    
    return memories

def search_memories(query):
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    search_term = f"%{query}%"
    cursor.execute("""
        SELECT * FROM memories 
        WHERE title LIKE ? OR summary LIKE ? OR tags LIKE ? OR transcription LIKE ?
        ORDER BY memory_date DESC
    """, (search_term, search_term, search_term, search_term))
    
    rows = cursor.fetchall()
    conn.close()
    
    memories = []
    for row in rows:
        memory = {
            "id": row[0],
            "title": row[1],
            "summary": row[2],
            "transcription": row[3],
            "tags": json.loads(row[4]) if row[4] else [],
            "emotional_tone": row[5],
            "memory_date": row[7]
        }
        memories.append(memory)
    
    return memories

def get_recent_memories(limit=5):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM memories ORDER BY memory_date DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    memories = []
    for row in rows:
        memory = {
            "id": row[0],
            "title": row[1],
            "summary": row[2],
            "tags": json.loads(row[4]) if row[4] else [],
            "emotional_tone": row[5],
            "memory_date": row[7]
        }
        memories.append(memory)
    
    return memories

def delete_memory(memory_id):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
    conn.commit()
    conn.close()
    print(f"Memory {memory_id} deleted")

if not os.path.exists(DB_PATH):
    init_database()
