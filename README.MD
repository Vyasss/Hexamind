Project Hexamind: Multi-Agent Neuro-Symbolic Cognitive Architecture

Author: Chetan Vyas

Status: Research Prototype 

Tech Stack: Python, LangGraph, LangChain, Streamlit, Google Gemini, OpenAI GPT-4o, Meta Llama 3

Project Overview

Hexamind is a stateful multi-agent system designed to orchestrate heterogeneous Large Language Models (LLMs) in a complex strategic environment (Chinese Checkers).

Unlike standard "chat" interfaces that rely on stateless API calls, Hexamind implements a Neuro-Symbolic Architecture. It combines the creative reasoning of Neural Networks (LLMs) with the deterministic validation of Symbolic Logic (Python-based Geometric Critics) to solve the problem of AI Hallucination in spatial reasoning tasks.

Architectural Pattern: The "Grandmaster" Graph

The core innovation is the Grandmaster Execution Loop, implemented via LangGraph. This moves beyond simple "Chain-of-Thought" prompting into a cyclic state machine:

Generator Node (The Intuition): An LLM (Gemini/GPT-4o) analyzes the board state and proposes a strategic vector.

Critic Node (The Guardrail): A deterministic algorithm evaluates the proposed move against Euclidean geometry rules.

Check 1: Is the move legal?

Check 2: Does the move decrease the distance to the goal? (preventing infinite loops/backwards play).

Reflexion Loop: If the Critic rejects the move, the state loops back to the Generator with specific feedback ("You moved backwards by 2 units"), forcing the LLM to self-correct.

 Key Features

Distributed Cognitive Load: Orchestrates agents across three different providers (Google, GitHub Models, Groq) simultaneously to handle rate limits and diversify reasoning patterns.

Stateful Orchestration: Uses LangGraph to maintain a persistent game state object (GameState), enabling complex turn-taking, referee intervention, and rollback capabilities.

Graceful Degradation: Implements robust error handling that detects API Rate Limits (429 Errors) and automatically switches to fallback logic or alternative providers without crashing the application.

Neuro-Symbolic Interface: A Streamlit-based UI that visualizes the "Mental State" of the graph (Thinking -> Critiquing -> Moving) in real-time.

🛠️ Technical Implementation

The Graph Engine (engine/graph.py)

The heart of the system. It defines the StateGraph that manages the flow of information between agents.

The Logic Core (engine/logic.py)

A custom-built geometric engine that maps axial coordinates to a 121-hole Star of David board. It provides the "Ground Truth" that the Critic uses to validate LLM outputs.

The Agent Swarm (agents/players.py)

A factory pattern that instantiates AIPlayer objects. Each player is a wrapper around a specific LLM (Gemini 1.5 Flash, GPT-4o, Llama 3.3) with specialized prompts designed to bypass "System Message" restrictions and optimize for spatial reasoning.

Installation & Usage

1. Clone the Repository

2. Install Dependencies

3. python -m venv venv
.\venv\Scripts\Activate
4. pip install -r requirements.txt

Run the Simulation

streamlit run ui/app.py


Future Research Directions

Long-Term Memory: Integrating Vector Databases (Pinecone) to allow agents to recall winning strategies from previous matches (RAG for Game Theory).

Monte Carlo Tree Search (MCTS): Replacing the single-step Generator with a parallelized simulation of future board states.