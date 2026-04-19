import sys
import io
import agent
import os

def generate_transcript(inputs, output_file, verbose=False):
    sys.stdin = io.StringIO("\n".join(inputs) + "\n")
    output_capture = io.StringIO()
    sys.stdout = output_capture
    
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(script_dir, '..', 'tree', 'reflection-tree.json')
        tree = agent.load_tree(json_path)
        agent.run_agent(tree, verbose=verbose)
    except Exception as e:
        print("Error during execution:", e)
    
    sys.stdin = sys.__stdin__
    sys.stdout = sys.__stdout__
    
    output_text = output_capture.getvalue()
    
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Reflection Session Transcript\n")
        f.write("```\n")
        f.write(output_text)
        f.write("```\n")

if __name__ == '__main__':
    # Persona 1: Victim / Entitled / Self-Centric (Runs in Verbose Mode to show debug output)
    inputs_1 = [
        "",         # START
        "3",        # A1_OPEN: Frustrating
        "",         # A1_EMOTIONAL_ACKNOWLEDGE
        "4",        # A1_Q_AGENCY_L: external_stuck ("system is broken")
        "",         # A1_R_EXT reflection
        "",         # BRIDGE_1_2
        "1",        # A2_OPEN: unacknowledged
        "2",        # A2_Q_ENTITLE: owes_me
        "",         # A2_R_ENTITLE reflection
        "",         # BRIDGE_2_3
        "1",        # A3_OPEN: just_me
        "1",        # A3_Q_SELF: struggle_stress
        "",         # A3_R_SELF
        "",         # TRAJECTORY
        "",         # SUMMARY
    ]
    generate_transcript(inputs_1, '../transcripts/persona-1-transcript.md', verbose=True)
    print("Generated Persona 1 Transcript.")
    
    # Persona 2: Victor / Contributing / Altrocentric (Standard Mode)
    inputs_2 = [
        "",         # START
        "1",        # A1_OPEN: Productive
        "1",        # A1_Q_AGENCY_H: internal_prep
        "",         # A1_R_INT reflection
        "",         # BRIDGE_1_2
        "3",        # A2_OPEN: help_unasked
        "1",        # A2_Q_CONTRIB: build_team
        "",         # A2_R_CONTRIB reflection
        "",         # BRIDGE_2_3
        "3",        # A3_OPEN: broader_team
        "2",        # A3_Q_ALTRO: unit_succeed
        "",         # A3_R_ALTRO
        "",         # TRAJECTORY
        "",         # SUMMARY
    ]
    generate_transcript(inputs_2, '../transcripts/persona-2-transcript.md', verbose=False)
    print("Generated Persona 2 Transcript.")
