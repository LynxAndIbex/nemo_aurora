import requests
import json
import os
from datetime import datetime
from database import save_memory

OPENROUTER_API_KEY = os.getenv("API_KEY")


#I ran into a huge problem here because JSON parsing from the AI was failing due to extra text.
#So now I made the AI ONLY return JSON
#I learned parsing logic from GPT.
def process_memory(transcript, audio_file=None):
    
    if not transcript or len(transcript.strip()) == 0:
        return None
    
    try:
        prompt = f"""
You are an assistant that converts voice memories into structured metadata.
Analyze the transcript below and output ONLY clean JSON.

Transcript:
\"\"\"{transcript}\"\"\"

Return JSON like:
{{
  "title": "Short title",
  "summary": "1–3 sentence summary",
  "tags": ["keyword1","keyword2"],
  "emotional_tone": "happy, sad, nostalgic, excited, etc."
}}
        """.strip()
        
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "meta-llama/llama-3.2-3b-instruct:free",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a careful JSON-producing assistant. Always return valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 300,
            "temperature": 0.2
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_text = result["choices"][0]["message"]["content"]
            
            # Try to parse JSON from response
            try:
                metadata = json.loads(ai_text.strip())
            except json.JSONDecodeError:
                # Try to extract JSON from markdown code blocks
                import re
                match = re.search(r'\{[\s\S]*\}', ai_text)
                if match:
                    metadata = json.loads(match.group(0))
                else:
                    print("Failed to parse JSON from AI response")
                    return None
            
            return metadata
        else:
            print(f"API Error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error processing memory: {e}")
        return None


#I named like ten other variables 'create memory' while debugging this, which is why the name is so long
#definitely a future cleanup item on the list
def create_memory_from_conversation(user_query, assistant_response, audio_file=None):

    
    transcript = f"User asked: {user_query}\nAssistant responded: {assistant_response}"
    
    
    metadata = process_memory(transcript, audio_file)
    
    if not metadata:
        print("Could not process memory")
        return None
    
    memory_id = save_memory(
        title=metadata.get("title", "Untitled Memory"),
        summary=metadata.get("summary", ""),
        transcription=transcript,
        tags=metadata.get("tags", []),
        emotional_tone=metadata.get("emotional_tone", "neutral"),
        audio_url=audio_file,
        memory_date=datetime.now().strftime("%Y-%m-%d")
    )
    
    print(f"✅ Memory created: {metadata.get('title')}")
    return memory_id
