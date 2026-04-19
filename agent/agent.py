import json
import sys
import re
import os

def load_tree(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def interpolate(text, state):
    # Interpolates variables like {A1_OPEN.answer_label} and {axis1.dominant}
    def get_dominant(axis):
        if axis == 'axis1':
            return 'internal' if state['signals'].get('axis1:internal', 0) >= state['signals'].get('axis1:external', 0) else 'external'
        elif axis == 'axis2':
            return 'contribution' if state['signals'].get('axis2:contribution', 0) >= state['signals'].get('axis2:entitlement', 0) else 'entitlement'
        elif axis == 'axis3':
            return 'altrocentric' if state['signals'].get('axis3:altrocentric', 0) >= state['signals'].get('axis3:selfcentric', 0) else 'selfcentric'
        return 'unknown'
    
    def replacer(match):
        expr = match.group(1)
        parts = expr.split('.')
        if len(parts) == 2:
            key, subkey = parts
            if subkey == 'dominant':
                return get_dominant(key)
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
    
    # Expose answers to the eval environment safely
    for k, v in state['answers'].items():
        local_env[f"{k}_answer"] = v
        # Replace occurrences like A1_OPEN.answer with A1_OPEN_answer
        condition = condition.replace(f"{k}.answer", f"{k}_answer")
        
    # Replace signal counts like axis1.internal
    for axis in ['axis1', 'axis2', 'axis3']:
        for pole in ['internal', 'external', 'contribution', 'entitlement', 'altrocentric', 'selfcentric']:
            val = state['signals'].get(f"{axis}:{pole}", 0)
            condition = condition.replace(f"{axis}.{pole}", str(val))
            
    try:
        return eval(condition, {"__builtins__": {}}, local_env)
    except Exception as e:
        print(f"Error evaluating condition: {condition} -> {e}")
        return False

def run_agent(tree_data):
    nodes = {node['id']: node for node in tree_data}
    current_id = "START"
    
    state = {
        'answers': {},
        'answer_labels': {},
        'signals': {}
    }
    
    while current_id:
        node = nodes.get(current_id)
        if not node:
            break
            
        # UI separation
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
                        if 'signal' in selected:
                            sig = selected['signal']
                            state['signals'][sig] = state['signals'].get(sig, 0) + 1
                        break
                    else:
                        print("Invalid choice. Try again.")
                except ValueError:
                    print("Please enter a number.")
            current_id = node.get('target') # Questions might not have a target directly
            
            # If a question doesn't have a target, the tree relies on a sequence or it's a bug in our JSON
            if not current_id:
                # Let's find the next node sequentially if possible? No, we should find the node whose id follows.
                # In our JSON, question nodes don't have targets, they just advance. 
                # This is a bug in my tree reading. Let's fix it by adding target or just taking the next index.
                # Actually, in the JSON, A1_OPEN has no target, so it relies on the JSON array order.
                idx = tree_data.index(node)
                if idx + 1 < len(tree_data):
                    current_id = tree_data[idx + 1]['id']
                else:
                    break
            
        elif node_type == 'decision':
            routed = False
            for route in node.get('routing', []):
                if evaluate_condition(route['condition'], state):
                    current_id = route['target']
                    routed = True
                    break
            if not routed:
                print("Error: No route found.")
                break
                
        elif node_type in ['reflection', 'bridge', 'start', 'summary']:
            # Wait for user
            input("\n[Press Enter to continue]")
            if 'target' in node:
                current_id = node['target']
            else:
                idx = tree_data.index(node)
                current_id = tree_data[idx + 1]['id'] if idx + 1 < len(tree_data) else None
            
        elif node_type == 'end':
            break

if __name__ == '__main__':
    # Determine the directory of the script and path to JSON
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, '..', 'tree', 'reflection-tree.json')
    
    # load and run
    tree = load_tree(json_path)
    run_agent(tree)
