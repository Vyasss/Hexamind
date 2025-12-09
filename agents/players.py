import os
import re
import random
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

load_dotenv()

class HumanPlayer:
    def __init__(self, player_id):
        self.player_id = player_id
        self.name = f"Player {player_id} (YOU)"
        self.is_human = True
    def get_move(self, board_state, valid_moves): pass 

class AIPlayer:
    def __init__(self, player_id, model_provider="groq", display_name=None):
        self.player_id = player_id
        self.is_human = False
        self.provider = model_provider
        
        # Use display_name if provided, otherwise use provider name
        if display_name:
            self.name = f"P{player_id} [{display_name}]"
        else:
            self.name = f"P{player_id} [{model_provider.upper()}]"
        
        # ===== ALL MODELS USE GROQ BACKEND =====
        groq_key = os.getenv("GROQ_API_KEY")
        
        if not groq_key:
            raise ValueError("❌ GROQ_API_KEY not found in .env file! Get one free at https://console.groq.com/")
        
        # Use different Groq models for variety (all free & fast)
        model_map = {
            "groq": "llama-3.3-70b-versatile",           # Llama 3.3 70B
            "gemini": "llama-3.3-70b-versatile",         # Same model, different display
            "github_gpt": "llama-3.1-70b-versatile",     # Llama 3.1 70B for variety
        }
        
        groq_model = model_map.get(model_provider, "llama-3.3-70b-versatile")
        
        self.llm = ChatGroq(
            model_name=groq_model,
            groq_api_key=groq_key,
            temperature=0.1,
            max_retries=2
        )
        
        print(f"✅ {self.name} → Groq Backend ({groq_model})")

    def get_move(self, board_state, valid_moves):
        # Target Logic - where each player needs to go
        target = (0, 0)
        if self.player_id == 1: 
            target = (0, 4)
        elif self.player_id == 2: 
            target = (-4, 0)
        elif self.player_id == 3: 
            target = (4, -4)

        target_desc = f"Target (q={target[0]}, r={target[1]})"
        move_options = ""
        for i, move in enumerate(valid_moves):
            move_options += f"{i}:{move}|" 

        prompt = f"""
You are playing Chinese Checkers as Player {self.player_id}.

GOAL: Move your pieces to {target_desc}

AVAILABLE MOVES:
{move_options}

Choose the move that gets you CLOSEST to your goal.
Respond with ONLY the integer ID of your chosen move (e.g., "5").
"""
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            content = response.content.strip()
            
            # Extract first number from response
            match = re.search(r'\d+', content)
            if match:
                idx = int(match.group())
                if 0 <= idx < len(valid_moves): 
                    return valid_moves[idx]
            
            # Fallback to random if parsing fails
            print(f"⚠️ Could not parse AI response: {content}")
            return random.choice(valid_moves)
            
        except Exception as e:
            print(f"❌ AI Error for {self.name}: {e}")
            return random.choice(valid_moves)

class Referee:
    def __init__(self):
        groq_key = os.getenv("GROQ_API_KEY")
        if not groq_key:
            print("⚠️ Warning: GROQ_API_KEY not found, referee disabled")
            self.llm = None
        else:
            self.llm = ChatGroq(
                model_name="llama-3.3-70b-versatile",
                groq_api_key=groq_key,
                temperature=0.7
            )
    
    def commentate(self, p, m):
        if not self.llm:
            return "Nice move!"
        try: 
            response = self.llm.invoke([HumanMessage(content=f"React to {p}'s move {m} in exactly 3 words:")])
            return response.content.strip()
        except Exception as e:
            print(f"Referee error: {e}")
            return "Interesting play!"