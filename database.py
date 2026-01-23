import sqlite3
import json
from datetime import datetime
import os

DB_PATH = "aurora_memories.db"

def init_database(user_id):
    
    file_path = f"{user_id}.json"

    if not os.path.exists(file_path):
        data = {
            "last_id":0,
            "memories": []

        }

        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

    return file_path




def save_memory(user_id, title, summary, transcription, tags, emotional_tone, audio_tone=None, memory_data=None):
    
    data = {"last_id": 0, "memories": []}

    last_id = data.get("last_id", 0)
    new_id = last_id + 1
    data["last_id"] = new_id
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)


    #new json library:
    memory = {
    "id": new_id,
    "title": title,
    "summary": summary,
    "transcription": transcription,
    "tags": tags,
    "emotional_tone": emotional_tone,
    "audio_data": audio_tone,
    "memory_date": memory_data or datetime.now().isoformat(),
    "created_at": datetime.now().isoformat()
    }

    
    file_path = f"{user_id}.json"
    if not os.path.exists(file_path):
        data = {"last id": 0, "memories": []}


    with open(file_path, 'r') as f:
        data = json.load(f)
    data["memories"].append(memory)

    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)


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
