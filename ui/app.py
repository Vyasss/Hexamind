import streamlit as st
import plotly.graph_objects as go
import time
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engine.logic import ChineseCheckers
from engine.graph import HexamindGraph
from agents.players import AIPlayer, HumanPlayer, Referee

st.set_page_config(page_title="Hexamind Arena", layout="wide")

PLAYER_COLORS = {0: "#2d3436", 1: "#74b9ff", 2: "#55efc4", 3: "#ff7675", 4: "#ffeaa7", 5: "#a29bfe", 6: "#fdcb6e"}

# Initialize session state
if "game" not in st.session_state: st.session_state.game = None
if "graph_engine" not in st.session_state: st.session_state.graph_engine = None
if "players" not in st.session_state: st.session_state.players = []
if "turn" not in st.session_state: st.session_state.turn = 1
if "game_active" not in st.session_state: st.session_state.game_active = False
if "logs" not in st.session_state: st.session_state.logs = []
if "referee_log" not in st.session_state: st.session_state.referee_log = "System Ready."
if "selected" not in st.session_state: st.session_state.selected = None
if "show_moves" not in st.session_state: st.session_state.show_moves = False

def draw_board(board, current_player_id=None, selected=None, targets=None):
    if targets is None: targets = []
    xs, ys, colors, sizes, texts = [], [], [], [], []
    
    for (q, r), pid in board.items():
        x = 1.5 * q
        y = 1.732 * (r + q / 2.0)
        xs.append(x)
        ys.append(-y)
        
        color = PLAYER_COLORS.get(pid, "#2d3436")
        text_label = ""
        size = 20
        
        if selected and (q, r) == selected:
            color = "#ffffff"
            size = 35
            text_label = "✓"
        elif (q, r) in targets:
            color = "#feca57"
            size = 30
            text_label = "→"
        elif pid == current_player_id:
            size = 24
        
        colors.append(color)
        sizes.append(size)
        texts.append(text_label)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=xs, y=ys, 
        mode="markers+text",
        marker=dict(size=sizes, color=colors, line=dict(width=3, color="#ffffff"), opacity=0.95),
        text=texts, 
        textposition="middle center", 
        textfont=dict(size=12, color="black", family="Arial Black"),
        hoverinfo='skip'
    ))
    
    fig.update_xaxes(showgrid=False, zeroline=False, visible=False, fixedrange=True)
    fig.update_yaxes(showgrid=False, zeroline=False, visible=False, fixedrange=True)
    fig.update_layout(
        showlegend=False, 
        plot_bgcolor="#0e1117", 
        paper_bgcolor="#0e1117", 
        margin=dict(l=20, r=20, t=20, b=20), 
        height=650
    )
    return fig

# Sidebar
st.sidebar.title("🎮 Hexamind Arena")
game_mode = st.sidebar.selectbox("Game Mode", ["Duel (2 Players)", "Battle Royale (3 Players)"])
mode_map = {"Duel (2 Players)": 2, "Battle Royale (3 Players)": 3}
turbo_mode = st.sidebar.checkbox("🚀 Turbo Mode", value=True)

st.sidebar.subheader("Players")
player_configs = []
for i in range(1, mode_map[game_mode] + 1):
    col_a, col_b = st.sidebar.columns([1, 2])
    with col_a: 
        p_type = st.radio(f"P{i}", ["AI", "Human"], key=f"p{i}_t", label_visibility="collapsed")
    with col_b:
        if p_type == "AI":
            model = st.selectbox(f"Model P{i}", ["Gemini Flash", "GPT-4o", "Llama 3.3"], key=f"p{i}_m", label_visibility="collapsed")
            pmap = {"Gemini Flash": "groq", "GPT-4o": "github_gpt", "Llama 3.3": "groq"}
            player_configs.append({"type": "AI", "id": i, "provider": pmap[model], "label": model})
        else:
            st.write(f"**P{i} (You)**")
            player_configs.append({"type": "Human", "id": i})

if st.sidebar.button("🎬 START GAME", type="primary"):
    st.session_state.game = ChineseCheckers(player_count=mode_map[game_mode])
    st.session_state.players = []
    for conf in player_configs:
        if conf["type"] == "AI":
            # Pass display_name to show in UI, but use "groq" as backend provider
            p = AIPlayer(
                conf["id"], 
                model_provider="groq",  # Always use Groq backend
                display_name=conf['label']  # But show "Gemini Flash", "GPT-4o", etc. in UI
            )
            st.session_state.players.append(p)
        else: 
            st.session_state.players.append(HumanPlayer(conf["id"]))
    st.session_state.graph_engine = HexamindGraph(st.session_state.players)
    st.session_state.turn = 1
    st.session_state.game_active = True
    st.session_state.logs = ["🎮 Game Started!"]
    st.session_state.selected = None
    st.session_state.show_moves = False
    st.rerun()

# Main game
if st.session_state.game_active:
    game = st.session_state.game
    players = st.session_state.players
    p_idx = (st.session_state.turn - 1) % mode_map[game_mode]
    current = players[p_idx]
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"### 🎯 Turn {st.session_state.turn}: {current.name}")
        
        # Get targets for visualization
        targets = []
        if st.session_state.selected:
            valid = game.get_valid_moves(current.player_id)
            for start, end in valid:
                if start == st.session_state.selected:
                    targets.append(end)
        
        # Draw board
        fig = draw_board(game.board, current.player_id, st.session_state.selected, targets)
        st.plotly_chart(fig, width='stretch', key=f"board_{st.session_state.turn}")
    
    with col2:
        st.markdown("### 📊 Game Status")
        st.info(f"🎤 {st.session_state.referee_log}")
        
        valid = game.get_valid_moves(current.player_id)
        st.metric("Valid Moves", len(valid))
        
        if current.is_human:
            if not valid:
                st.error("❌ No valid moves! Skipping turn...")
                time.sleep(1.5)
                st.session_state.turn += 1
                st.session_state.selected = None
                st.session_state.show_moves = False
                st.rerun()
            
            # Build moves dictionary
            moves_by_piece = {}
            for start, end in valid:
                if start not in moves_by_piece:
                    moves_by_piece[start] = []
                moves_by_piece[start].append(end)
            
            # Show current selection status
            if st.session_state.selected:
                st.success(f"✅ Selected: {st.session_state.selected}")
                available_targets = moves_by_piece.get(st.session_state.selected, [])
                st.warning(f"🎯 {len(available_targets)} moves available - select destination below")
                
                if st.button("❌ Cancel Selection", key="cancel"):
                    st.session_state.selected = None
                    st.session_state.show_moves = False
                    st.rerun()
                
                st.markdown("---")
                st.markdown("#### 🎯 Choose Destination:")
                
                # Show destination buttons in a grid
                cols_per_row = 2
                targets = available_targets
                for i in range(0, len(targets), cols_per_row):
                    cols = st.columns(cols_per_row)
                    for j, col in enumerate(cols):
                        if i + j < len(targets):
                            target = targets[i + j]
                            with col:
                                if st.button(f"→ {target}", key=f"dest_{target}", width='stretch'):
                                    # Execute move
                                    game.apply_move(st.session_state.selected, target)
                                    st.session_state.logs.append(f"✅ You: {st.session_state.selected} → {target}")
                                    st.session_state.selected = None
                                    st.session_state.show_moves = False
                                    st.session_state.turn += 1
                                    st.rerun()
            
            else:
                st.info("👇 Select a piece to move:")
                
                # Show piece selection buttons
                pieces = sorted(list(moves_by_piece.keys()))
                cols_per_row = 2
                
                for i in range(0, len(pieces), cols_per_row):
                    cols = st.columns(cols_per_row)
                    for j, col in enumerate(cols):
                        if i + j < len(pieces):
                            piece = pieces[i + j]
                            num_moves = len(moves_by_piece[piece])
                            with col:
                                if st.button(f"📍 {piece} ({num_moves})", key=f"piece_{piece}", width='stretch'):
                                    st.session_state.selected = piece
                                    st.session_state.show_moves = True
                                    st.rerun()
        
        else:
            # AI Turn
            st.info("🤖 AI is thinking...")
            if not turbo_mode:
                time.sleep(0.5)
            
            result = st.session_state.graph_engine.run_turn(game.board, p_idx, st.session_state.turn)
            game.board = result["board"]
            
            if "logs" in result:
                st.session_state.logs.extend(result["logs"])
            
            if st.session_state.turn % 5 == 0:
                try:
                    st.session_state.referee_log = Referee().commentate(current.name, "played")
                except:
                    pass
            
            st.session_state.turn += 1
            st.session_state.selected = None
            st.rerun()
        
        # Game log
        st.markdown("---")
        st.markdown("### 📜 Recent Moves")
        for log in reversed(st.session_state.logs[-5:]):
            st.text(log)

else:
    st.title("🎮 Hexamind Arena")
    st.info("👈 Configure players in the sidebar and click START GAME!")
    st.markdown("""
    ### How to Play:
    1. **Select game mode** (2 or 3 players)
    2. **Choose Human or AI** for each player
    3. Click **START GAME**
    4. **Click buttons** to select your piece
    5. **Click destination button** to move
    """)