import requests
import json
import os
from database import search_memories, get_recent_memories
from dotenv import load_dotenv
load_dotenv()


OPENROUTER_API_KEY = os.getenv("API_KEY") #api key is in .env; not on github.


def process_query_api(text, user_id):
    
    
    if not text or len(text.strip()) == 0:
        return "Sorry, I'm having trouble right now."
    
    
    try:
        # searching for memories
        relevant_memories = search_memories(user_id, text)
        memory_context = ""
        


        if relevant_memories:
            memory_context = "\n\nRelevant memories from past conversations:\n"
            for mem in relevant_memories[:3]:  # Use top 3 relevant memories
                memory_context += f"- {mem['transcription']}\n"
        
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        
        system_prompt = """You are Nemo, a memory voice assistant for someone with Alzheimer's Disease. 
                        CRITICAL RULES:
                        1. ONLY answer using information explicitly stated in the "Past Conversations" section below
                        2. If the requested info is not in past conversations, say "I don't have that information saved yet"
                        3. NEVER guess or make up information
                        4. Keep responses brief (1-2 sentences) but ACCURATE.
                        5. If responses require more than 2 sentences to be accurate, use more than 2 sentences. Express the idea as quickly as possible without being inaccurate.
                        6. If there are multiple references, choose the most recent memory. this is the most current information, and recency is truth.
                        7. Use quotes. Do NOT exaggerate. For example, if someone is tired, quote 'tired', not 'exhausted'
                        When asking, think: "Is this EXACTLY what was said in past conversations, or am I guessing?". Do not guess. If you do not have that info, reply with "I don't have that information yet".
                        
"""        
        user_message = text
        if memory_context:
            user_message = f"""Question: {text}
            {memory_context}

        Remember to ONLY answer using the information in the "Past Conversations" section above. If the information isn't there, say "I don't have that information saved yet"."""
        else:
            user_message = f"""Question: {text}

        No relevant memories found

        Say: I don't have that information saved yet."""
            
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
            "temperature": 0.3
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

