import requests
import json
import os
from database import search_memories, get_recent_memories
from dotenv import load_dotenv
load_dotenv()


OPENROUTER_API_KEY = os.getenv("API_KEY") #api key is in .env; not on github.


def process_query_api(text):
    
    
    if not text or len(text.strip()) == 0:
        return None
    
    try:
        # searching for memories
        relevant_memories = search_memories(text)
        memory_context = ""
        
        if relevant_memories:
            memory_context = "\n\nRelevant memories from past conversations:\n"
            for mem in relevant_memories[:3]:  # Use top 3 relevant memories
                memory_context += f"- {mem['title']}: {mem['summary']}\n"
        
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        
        system_prompt = """You are Nemo, a helpful voice assistant running on a Raspberry Pi. 
Keep responses concise and conversational since they will be spoken aloud. Aim for 1-3 sentences maximum.
You have access to memories from past conversations - use them to provide personalized responses."""
        
        user_message = text
        if memory_context:
            user_message = f"{text}{memory_context}"
        
        payload = {
            "model": "meta-llama/llama-3.2-3b-instruct:free",
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            "max_tokens": 150
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions", 
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result["choices"][0]["message"]["content"]
            return ai_response.strip()
        else:
            print(f"API Error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("API timeout")
        return None
    except Exception as e:
        print(f"OpenRouter failed: {e}")
        return None

