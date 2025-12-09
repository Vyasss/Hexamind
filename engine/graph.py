from typing import TypedDict, List, Any
from langgraph.graph import StateGraph, END
from engine.logic import ChineseCheckers
# Use Grandmaster if available, else simple
try:
    from engine.grandmaster import GrandmasterGraph
    USE_GRANDMASTER = True
except ImportError:
    USE_GRANDMASTER = False

from agents.players import AIPlayer, HumanPlayer

class GameState(TypedDict):
    board: dict
    current_player_idx: int
    players: List[Any]
    turn_count: int
    last_move: str
    logs: List[str]

class HexamindGraph:
    def __init__(self, players):
        self.game_logic = ChineseCheckers(player_count=len(players))
        self.players = players
        
        workflow = StateGraph(GameState)
        workflow.add_node("agent_move", self.agent_node)
        workflow.set_entry_point("agent_move")
        workflow.add_edge("agent_move", END) # Simple loop for now
        self.app = workflow.compile()

    def agent_node(self, state: GameState):
        p_idx = state['current_player_idx']
        player = state['players'][p_idx]
        
        self.game_logic.board = state['board']
        valid_moves = self.game_logic.get_valid_moves(player.player_id)

        if not valid_moves:
            return {"logs": [f"{player.name} stuck!"]}

        # If human, we expect move to be handled by UI, but if we reach here 
        # for an AI, we calculate it.
        if player.is_human:
             # In this architecture, human moves are applied directly in UI
             # This node is a pass-through or AI generator
             return {}
        else:
             move = player.get_move(state['board'], valid_moves)
             self.game_logic.apply_move(move[0], move[1])
             return {
                 "board": self.game_logic.board,
                 "logs": [f"{player.name} moved {move}"]
             }

    def run_turn(self, current_board, current_player_idx, turn_count):
        initial = {
            "board": current_board,
            "current_player_idx": current_player_idx,
            "players": self.players,
            "turn_count": turn_count,
            "last_move": "",
            "logs": []
        }
        return self.app.invoke(initial)