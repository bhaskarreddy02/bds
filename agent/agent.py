import json
import sys
import re
import os
import argparse

def load_tree(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def get_dominant(axis, state):
    if axis == 'axis1':
        return 'internal' if state['signals'].get('axis1:internal', 0) >= state['signals'].get('axis1:external', 0) else 'external'
    elif axis == 'axis2':
        return 'contribution' if state['signals'].get('axis2:contribution', 0) >= state['signals'].get('axis2:entitlement', 0) else 'entitlement'
    elif axis == 'axis3':
        return 'altrocentric' if state['signals'].get('axis3:altrocentric', 0) >= state['signals'].get('axis3:selfcentric', 0) else 'selfcentric'
    return 'unknown'

def interpolate(text, state):
    def replacer(match):
        expr = match.group(1)
        parts = expr.split('.')
        if len(parts) == 2:
            key, subkey = parts
            if subkey == 'dominant':
                return get_dominant(key, state)
            elif subkey == 'answer':
                return state['answers'].get(key, '')
            elif subkey == 'answer_label':
                return state['answer_labels'].get(key, '')
        return str(match.group(0))

    return re.sub(r'\{([^}]+)\}', replacer, text)

def evaluate_condition(condition, state):
    if condition.lower() == 'true':
        return True
    
    local_env = {
        'true': True,
        'false': False
    }
    
    for k, v in state['answers'].items():
        local_env[f"{k}_answer"] = v
        condition = condition.replace(f"{k}.answer", f"{k}_answer")
        
    for axis in ['axis1', 'axis2', 'axis3']:
        for pole in ['internal', 'external', 'contribution', 'entitlement', 'altrocentric', 'selfcentric']:
            val = state['signals'].get(f"{axis}:{pole}", 0)
            condition = condition.replace(f"{axis}.{pole}", str(val))
            
    # Allow axis1.dominant == 'internal' directly by injecting strings
    for axis in ['axis1', 'axis2', 'axis3']:
        local_env[f"{axis}_dominant"] = get_dominant(axis, state)
        condition = condition.replace(f"{axis}.dominant", f"{axis}_dominant")
            
    try:
        return eval(condition, {"__builtins__": {}}, local_env)
    except Exception as e:
        print(f"Error evaluating condition: {condition} -> {e}")
        return False

def run_agent(tree_data, verbose=False):
    nodes = {node['id']: node for node in tree_data}
    current_id = "START"
    
    state = {
        'answers': {},
        'answer_labels': {},
        'signals': {}
    }
    
    if verbose:
        print("\n═══════════════════════════════════════════════════════════")
        print("REFLECTION PATH (Debug Mode)")
        print("═══════════════════════════════════════════════════════════")
    
    while current_id:
        node = nodes.get(current_id)
        if not node:
            break
            
        if node['type'] not in ['decision']:
            print("\n" + "~"*60)
        
        node_type = node.get('type')
        if 'text' in node:
            print(interpolate(node['text'], state))
            
        if node_type == 'question':
            options = node.get('options', [])
            for i, opt in enumerate(options, 1):
                print(f"  {i}) {opt['label']}")
                
            while True:
                choice = input("\nSelect an option (1-{}): ".format(len(options)))
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(options):
                        selected = options[idx]
                        state['answers'][node['id']] = selected['value']
                        state['answer_labels'][node['id']] = selected['label']
                        
                        if verbose:
                            print(f"[DEBUG] Q ({node['id']}): '{selected['label']}'")
                            
                        if 'signal' in selected:
                            sig = selected['signal']
                            state['signals'][sig] = state['signals'].get(sig, 0) + 1
                            if verbose:
                                print(f"[DEBUG] Signal: {sig} ✓")
                        break
                    else:
                        print("Invalid choice. Try again.")
                except ValueError:
                    print("Please enter a number.")
                    
            if 'target' in node:
                current_id = node['target']
            else:
                idx = tree_data.index(node)
                current_id = tree_data[idx + 1]['id'] if idx + 1 < len(tree_data) else None
            
        elif node_type == 'decision':
            routed = False
            for route in node.get('routing', []):
                if evaluate_condition(route['condition'], state):
                    if verbose:
                        print(f"[DEBUG] DECISION {node['id']} matched condition -> Routing to {route['target']}")
                    current_id = route['target']
                    routed = True
                    break
            if not routed:
                print("Error: No route found.")
                break
                
        elif node_type in ['reflection', 'bridge', 'start', 'trajectory']:
            if verbose and node_type != 'start':
                print(f"[DEBUG] Rendered ({node_type}) {node['id']}")
            input("\n[Press Enter to continue]")
            if 'target' in node:
                current_id = node['target']
            else:
                idx = tree_data.index(node)
                current_id = tree_data[idx + 1]['id'] if idx + 1 < len(tree_data) else None
                
        elif node_type == 'summary':
            if verbose:
                print("\n" + "═"*59)
                print("SIGNAL TALLY:")
                for axis in ['axis1', 'axis2', 'axis3']:
                    for pole in ['internal', 'external', 'contribution', 'entitlement', 'altrocentric', 'selfcentric']:
                        val = state['signals'].get(f"{axis}:{pole}", 0)
                        if val > 0:
                            print(f"  {axis}:{pole} = {val}")
                print("\nDOMINANT TRAITS:")
                for axis in ['axis1', 'axis2', 'axis3']:
                    print(f"  {axis}: {get_dominant(axis, state)}")
                print("═"*59)

            matched = False
            for synth in node.get('syntheses', []):
                if evaluate_condition(synth['condition'], state):
                    matched = True
                    if verbose:
                        print(f"\n[DEBUG] SUMMARY SYNTHESIS MATCHED:\n  Condition: {synth['condition']}\n")
                    
                    print(interpolate(synth.get('narrative', ''), state))
                    print("\n" + interpolate(synth.get('edge_case', ''), state))
                    print("\n" + interpolate(synth.get('forward', ''), state))
                    break
                    
            if not matched:
                print("\n" + interpolate(node.get('default', 'Session Complete.'), state))
                
            input("\n[Press Enter to finish]")
            current_id = node.get('target')
            
        elif node_type == 'end':
            break

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the Reflection Agent.')
    parser.add_argument('--verbose', action='store_true', help='Enable debug mode to trace paths and signals.')
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, '..', 'tree', 'reflection-tree.json')
    
    tree = load_tree(json_path)
    run_agent(tree, verbose=args.verbose)
