from typing import TypedDict, List, Annotated, Optional
import math
from langgraph.graph import StateGraph, END

class GrandmasterState(TypedDict):
    board: dict
    player_id: int
    valid_moves: List[tuple]
    proposed_move: Optional[tuple]
    critique: str
    attempt_count: int
    final_move: Optional[tuple]

class GrandmasterGraph:
    def __init__(self, ai_player, game_logic):
        self.ai = ai_player
        self.game = game_logic
        
        workflow = StateGraph(GrandmasterState)
        workflow.add_node("generator", self.generate_move)
        workflow.add_node("critic", self.math_critic) 
        
        workflow.set_entry_point("generator")
        
        workflow.add_conditional_edges(
            "critic",
            self.check_approval,
            {
                "approved": END,
                "retry": "generator"
            }
        )
        self.app = workflow.compile()

    def generate_move(self, state: GrandmasterState):
        attempts = state.get("attempt_count", 0)
        # Generate a move using the AI
        move = self.ai.get_move(state['board'], state['valid_moves'])
        return {
            "proposed_move": move,
            "attempt_count": attempts + 1
        }

    def math_critic(self, state: GrandmasterState):
        move = state['proposed_move']
        start, end = move
        player_id = state['player_id']
        attempts = state['attempt_count']
        
        # --- 1. DEFINE TARGETS (Matches Logic.py) ---
        target = (0,0)
        if player_id == 1: target = (0, 4)
        elif player_id == 2: target = (-4, 0) 
        elif player_id == 3: target = (4, -4)
        
        # --- 2. CALCULATE DISTANCE ---
        dist_start = math.sqrt((start[0]-target[0])**2 + (start[1]-target[1])**2)
        dist_end = math.sqrt((end[0]-target[0])**2 + (end[1]-target[1])**2)
        
        improvement = dist_start - dist_end
        
        # --- 3. DECISION LOGIC ---
        # Relaxed Rule: Allow moves that don't go backwards by more than 2 units
        # This allows side-stepping around blockers.
        is_acceptable = improvement > -2.0
        
        # FORCE APPROVE if:
        # A. We tried 3 times already
        # B. The move is acceptable
        if attempts >= 3 or is_acceptable:
            # If we are forcing a "bad" move on attempt 3, so be it. Better than crashing.
            return {"critique": "approved", "final_move": move}
        
        # Reject bad moves (moving directly backwards)
        return {
            "critique": "retry", 
            "final_move": None 
        }

    def check_approval(self, state: GrandmasterState):
        if state.get('critique') == "approved": return "approved"
        return "retry"

    def run(self, board, player_id, valid_moves):
        initial = {
            "board": board, 
            "player_id": player_id, 
            "valid_moves": valid_moves, 
            "attempt_count": 0,
            "critique": "",
            "proposed_move": None,
            "final_move": None
        }
        
        # Run graph with a higher recursion limit just in case
        config = {"recursion_limit": 10}
        res = self.app.invoke(initial, config=config)
        
        # Final Safety Net: If graph somehow failed to set final_move, pick random
        if res.get('final_move') is None:
            import random
            return random.choice(valid_moves)
            
        return res['final_move']