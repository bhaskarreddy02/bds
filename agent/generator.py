import sys
import io
import agent

def generate_transcript(inputs, output_file):
    # Prepare standard input
    sys.stdin = io.StringIO("\n".join(inputs) + "\n")
    
    # Prepare standard output
    output_capture = io.StringIO()
    sys.stdout = output_capture
    
    try:
        tree = agent.load_tree('../tree/reflection-tree.json')
        agent.run_agent(tree)
    except Exception as e:
        print("Error during execution:", e)
    
    sys.stdin = sys.__stdin__
    sys.stdout = sys.__stdout__
    
    output_text = output_capture.getvalue()
    
    with open(output_file, 'w') as f:
        f.write("# Reflection Session Transcript\n")
        f.write("```\n")
        f.write(output_text)
        f.write("```\n")

if __name__ == '__main__':
    # Persona 1: Victim / Entitled / Self-Centric
    inputs_1 = [
        "",         # START
        "3",        # A1_OPEN: Frustrating
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
        "",         # SUMMARY
    ]
    generate_transcript(inputs_1, '../transcripts/persona-1-transcript.md')
    print("Generated Persona 1 Transcript.")
    
    # Persona 2: Victor / Contributing / Altrocentric
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
        "",         # SUMMARY
    ]
    generate_transcript(inputs_2, '../transcripts/persona-2-transcript.md')
    print("Generated Persona 2 Transcript.")
