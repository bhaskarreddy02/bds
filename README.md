# Practice-Driven Growth Management System: Reflection Tree

This repository contains the deterministic reflection tree assignment for DeepThought Growth Teams.

## Directory Structure

- **/tree/**
  - `reflection-tree.json`: The core static JSON file acting as the deterministic database for the session.
  - `tree-diagram.md`: A visual representation of the node paths and conditional branches via Mermaid syntax.
- **/agent/**
  - `agent.py`: A CLI Python application that executes the JSON logic natively.
  - `generator.py`: A wrapper script that automates persona pathing.
- **/transcripts/**
  - `persona-1-transcript.md`: A simulated session representing a self-centric/entitled/external locus persona.
  - `persona-2-transcript.md`: A simulated session representing an altrocentric/contributing/internal locus persona.
- `write-up.md`: The 2-page psychological grounding and design rationale document.
- `README.md`: You are here.

## Running the Agent (Part B)

The tree can be consumed by any structured parsing engine. We have included a native Python CLI implementation.
Because it's deterministic and relies on no external APIs or LLMs at runtime, you can run it directly:

```bash
cd agent
python agent.py
```

### Navigating the Tree
The agent will print narrative text followed by numerical options.
- The `[Press Enter to continue]` prompts are mapped to `reflection` and `bridge` node types giving the user time to actually process the text.
- Enter a numerical option corresponding to the lists when asked.
- At the end, the engine performs variable interpolation for `<summary>` and `<reflection>` nodes using the `signal` state map.

## Tree Parsing Logic
If you are writing your own agent to interpret this tree, the engine must respect four core properties:
1. **String Evaluation**: Conditions found within `routing` blocks dictate edge pathing. The conditionals refer directly to the tree's accumulated `answers` dictionary and the `signals` scoreboard. 
2. **Deterministic Targeting**: If `routing[]` finds a match, the engine automatically branches to the specified `target` ID.
3. **Signal Accumulation**: When a user selects an option with an associated `"signal"` key, the engine increments that key in global context.
4. **Interpolation**: Handled via `{nodeId.property}` substitution
