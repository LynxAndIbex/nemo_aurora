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
    file_path = f"{user_id}.json"

    with open(file_path, 'r') as f:
        data = json.load(f)
    
    last_id = data.get("last_id", 0)
    new_id = last_id + 1
    data["last_id"] = new_id


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


    
    data["memories"].append(memory)

    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)
   

def get_memories(user_id):

    file_path = f"{user_id}.json"
    with open(file_path, 'r') as f:
        data = json.load(f)






    return data["memories"]

def search_memories(user_id,query):

    memories = get_memories(user_id)
    matches = []
    seen_ids = set() #generate a set to move on and avoid duplicates
    fields = ["title","summary","transcription","emotional_tone"]
    query_lower = query.lower()

    for m in memories:
        found = False #reset if memories are found
        for f in fields:        
            field_text = m.get(f, "").lower()
            if query_lower in field_text:
                if m["id"] not in seen_ids:
                    matches.append(m)
                    seen_ids.add(m["id"])
                found = True
                break  # Move to the next memory after a match is found
       
        if not found:
            for t in m.get("tags", []):
                if query_lower in t.lower():
                    if m["id"] not in seen_ids:
                        matches.append(m)
                        seen_ids.add(m["id"])
                    break  # Move to the next memory after a match is found


    matches_sorted = sorted(
        matches,
        key = lambda m: datetime.fromisoformat(m["memory_date"]),
        reverse=True #only index by newer memories coming first
    )

    return matches_sorted

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
