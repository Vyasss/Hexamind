import time
import os
from engine.logic import ChineseCheckers
from agents.players import AIPlayer, HumanPlayer, Referee

def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def setup_player(player_id):
    """Configuration Menu for a single player slot"""
    print(f"\n--- Configuring Player {player_id} ---")
    while True:
        ptype = input(f"Who controls Player {player_id}? [H]uman or [A]I? > ").lower()
        if ptype in ['h', 'human']:
            return HumanPlayer(player_id)
        elif ptype in ['a', 'ai']:
            print("\n🤖 Select AI Provider (FREE OPTIONS):")
            print("1. Groq - Llama 3.3 70B (RECOMMENDED - 30 req/min free)")
            print("2. Together AI - Llama 3.3 70B (Generous free tier)")
            print("3. DeepSeek - DeepSeek V3 (Very cheap: $0.27/M tokens)")
            print("4. OpenRouter - Free Llama models")
            print("5. Gemini - Flash 2.0 (Google free tier)")
            
            choice = input("\nChoice (1-5) [default: 1] > ").strip() or "1"
            model_map = {
                "1": "groq",
                "2": "together",
                "3": "deepseek",
                "4": "openrouter",
                "5": "gemini"
            }
            provider = model_map.get(choice, "groq")
            print(f"✅ Selected: {provider.upper()}")
            return AIPlayer(player_id, model_provider=provider)
        else:
            print("❌ Invalid choice. Please type 'H' or 'A'.")

def main():
    clear_screen()
    print("=" * 60)
    print("🏟️  HEXAMIND ARENA - Chinese Checkers AI Tournament 🏟️")
    print("=" * 60)
    
    # 1. Select Game Mode
    while True:
        try:
            print("\n📋 Select Game Mode:")
            print("  1. ⚔️  Duel (2 Players)")
            print("  2. 🔺 Triangle Battle (3 Players)")
            print("  3. 🎯 Team Skirmish (4 Players)")
            print("  4. 🌪️  Total Chaos (6 Players)")
            
            choice = int(input("\nEnter choice (1-4): "))
            player_counts = {1: 2, 2: 3, 3: 4, 4: 6}
            num_players = player_counts.get(choice)
            
            if num_players:
                print(f"\n✅ {num_players}-Player mode selected!")
                break
            print("❌ Invalid selection.")
        except ValueError:
            print("❌ Please enter a number.")

    # 2. Setup Game
    game = ChineseCheckers(player_count=num_players)
    players = []
    
    print(f"\n🎮 Setting up {num_players} players...")
    print("=" * 60)
    
    # Position mapping info
    position_names = {
        2: {1: "Top", 2: "Bottom"},
        3: {1: "Top", 2: "Bottom-Right", 3: "Bottom-Left"},
        4: {1: "Top", 2: "Top-Right", 3: "Bottom", 4: "Bottom-Left"},
        6: {1: "Top", 2: "Top-Right", 3: "Bottom-Right", 
            4: "Bottom", 5: "Bottom-Left", 6: "Top-Left"}
    }
    
    for i in range(1, num_players + 1):
        pos_name = position_names.get(num_players, {}).get(i, f"Position {i}")
        print(f"\n📍 Player {i} starts at: {pos_name}")
        p = setup_player(i)
        players.append(p)
    
    # Optional referee
    use_referee = input("\n🎙️  Enable AI commentary? [y/N] > ").lower() == 'y'
    referee = Referee() if use_referee else None
    
    print("\n" + "=" * 60)
    print("✅ Setup Complete! Starting Match...")
    print("=" * 60)
    time.sleep(2)
    
    # Initial board display
    clear_screen()
    game.visualize()
    
    # 3. Game Loop
    turn = 1
    max_turns = 200  # Prevent infinite games
    
    while turn <= max_turns:
        # Check for winner
        winner = game.check_winner()
        if winner > 0:
            print(f"\n{'='*60}")
            print(f"🏆 VICTORY! Player {winner} ({players[winner-1].name}) WINS! 🏆")
            print(f"{'='*60}")
            break
        
        # Determine current player
        p_idx = (turn - 1) % num_players
        current_agent = players[p_idx]
        
        print(f"\n{'─'*60}")
        print(f"🔹 TURN {turn}: {current_agent.name}")
        print(f"{'─'*60}")
        
        # Get Valid Moves
        moves = game.get_valid_moves(current_agent.player_id)
        if not moves:
            print(f"⚠️  {current_agent.name} has no valid moves! Skipping turn.")
            turn += 1
            time.sleep(1)
            continue
        
        print(f"📊 {len(moves)} valid moves available")
        
        # Agent Decision
        if not current_agent.is_human:
            print(f"🤔 {current_agent.name} is thinking...")
            start_time = time.time()
        
        try:
            move = current_agent.get_move(game.board, moves)
            
            if not current_agent.is_human:
                elapsed = time.time() - start_time
                print(f"⏱️  Decision time: {elapsed:.2f}s")
        except Exception as e:
            print(f"❌ Error getting move: {e}")
            move = moves[0]  # Fallback to first valid move
        
        # Apply Move
        if move:
            success = game.apply_move(move[0], move[1])
            if success:
                print(f"✅ Moved: {move[0]} → {move[1]}")
                
                # Visualize updated board
                time.sleep(0.5)
                clear_screen()
                game.visualize()
                
                # Commentary
                if referee and (not current_agent.is_human or turn % 5 == 0):
                    referee.commentate(current_agent.name, f"{move[0]}→{move[1]}")
            else:
                print(f"❌ Invalid move attempted!")
        
        turn += 1
        
        # Pause for AI moves
        if not current_agent.is_human:
            time.sleep(1.5)
    
    if turn > max_turns:
        print(f"\n{'='*60}")
        print("⏰ Game ended - Turn limit reached!")
        print(f"{'='*60}")
    
    print("\n🎮 Thanks for playing HEXAMIND ARENA! 🎮\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⛔ Game interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()