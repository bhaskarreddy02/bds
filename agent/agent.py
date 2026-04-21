import json
import sys
import re
import os
import argparse
import logging

# Configure logging for guardrail monitoring
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_tree(filepath):
    """Load and validate the reflection tree JSON with guardrails."""
    try:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Tree file not found: {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            tree_data = json.load(f)

        # Guardrail: Validate tree structure
        if not isinstance(tree_data, list):
            raise ValueError("Tree data must be a list of nodes")

        required_fields = ['id', 'type']
        node_ids = set()

        for node in tree_data:
            if not isinstance(node, dict):
                raise ValueError(f"Node must be a dictionary: {node}")

            # Check required fields
            for field in required_fields:
                if field not in node:
                    raise ValueError(f"Node missing required field '{field}': {node}")

            # Check for duplicate IDs
            if node['id'] in node_ids:
                raise ValueError(f"Duplicate node ID: {node['id']}")
            node_ids.add(node['id'])

            # Validate node types
            valid_types = ['start', 'question', 'decision', 'reflection', 'bridge', 'trajectory', 'summary', 'end']
            if node['type'] not in valid_types:
                raise ValueError(f"Invalid node type '{node['type']}' for node {node['id']}")

            # Validate question nodes have options
            if node['type'] == 'question':
                if 'options' not in node or not isinstance(node['options'], list):
                    raise ValueError(f"Question node {node['id']} missing valid options list")
                for option in node['options']:
                    if not isinstance(option, dict) or 'value' not in option or 'label' not in option:
                        raise ValueError(f"Invalid option format in node {node['id']}: {option}")

            # Validate decision nodes have routing
            if node['type'] == 'decision':
                if 'routing' not in node or not isinstance(node['routing'], list):
                    raise ValueError(f"Decision node {node['id']} missing valid routing list")
                for route in node['routing']:
                    if not isinstance(route, dict) or 'condition' not in route or 'target' not in route:
                        raise ValueError(f"Invalid routing format in node {node['id']}: {route}")

        logger.info(f"Successfully loaded and validated tree with {len(tree_data)} nodes")
        return tree_data

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in tree file: {e}")
        raise
    except Exception as e:
        logger.error(f"Error loading tree: {e}")
        raise

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
    """Safely evaluate routing conditions with guardrails against code injection."""
    if not isinstance(condition, str):
        logger.warning(f"Condition must be string, got {type(condition)}: {condition}")
        return False

    # Guardrail: Reject obviously dangerous patterns
    dangerous_patterns = [
        '__import__', 'import ', 'exec', 'eval', 'open', 'file', 'input',
        'system', 'subprocess', 'os.', 'sys.', 'globals', 'locals'
    ]

    condition_lower = condition.lower()
    for pattern in dangerous_patterns:
        if pattern in condition_lower:
            logger.error(f"Rejected potentially dangerous condition: {condition}")
            return False

    if condition.lower() == 'true':
        return True

    # Guardrail: Limit evaluation environment
    local_env = {
        'true': True,
        'false': False,
        'len': len,
        'str': str,
        'int': int,
        'float': float,
        'bool': bool,
        'isinstance': isinstance,
        'sum': sum,
        'max': max,
        'min': min,
        'abs': abs,
        'round': round
    }

    # Safely inject state variables
    try:
        for k, v in state['answers'].items():
            if not isinstance(v, (str, int, float, bool)):
                logger.warning(f"Skipping non-primitive answer value for {k}: {type(v)}")
                continue
            local_env[f"{k}_answer"] = v
            # Replace in condition string safely
            condition = condition.replace(f"{k}.answer", f"{k}_answer")

        for axis in ['axis1', 'axis2', 'axis3']:
            for pole in ['internal', 'external', 'contribution', 'entitlement', 'altrocentric', 'selfcentric']:
                val = state['signals'].get(f"{axis}:{pole}", 0)
                local_env[f"{axis}_{pole}"] = val
                condition = condition.replace(f"{axis}.{pole}", f"{axis}_{pole}")

        # Inject dominant values safely
        for axis in ['axis1', 'axis2', 'axis3']:
            dominant = get_dominant(axis, state)
            local_env[f"{axis}_dominant"] = dominant
            condition = condition.replace(f"{axis}.dominant", f"{axis}_dominant")

        # Guardrail: Evaluate with restricted globals and timeout consideration
        result = eval(condition, {"__builtins__": {}}, local_env)

        if not isinstance(result, bool):
            logger.warning(f"Condition did not evaluate to boolean: {condition} -> {result}")
            return False

        return result

    except Exception as e:
        logger.error(f"Error evaluating condition '{condition}': {e}")
        return False

def run_agent(tree_data, verbose=False, chat_mode=False):
    """Run the reflection agent with comprehensive guardrails."""
    if not tree_data or not isinstance(tree_data, list):
        logger.error("Invalid tree data provided")
        return

    nodes = {node['id']: node for node in tree_data}
    current_id = "START"

    # Guardrail: Initialize state with validation
    state = {
        'answers': {},
        'answer_labels': {},
        'signals': {}
    }

    if verbose and not chat_mode:
        print("\n═══════════════════════════════════════════════════════════")
        print("REFLECTION PATH (Debug Mode)")
        print("═══════════════════════════════════════════════════════════")

    max_iterations = 100  # Guardrail: Prevent infinite loops
    iteration_count = 0

    while current_id and iteration_count < max_iterations:
        iteration_count += 1

        node = nodes.get(current_id)
        if not node:
            logger.error(f"Node not found: {current_id}")
            break

        if not chat_mode and node['type'] not in ['decision']:
            print("\n" + "~"*60)

        node_type = node.get('type')
        if 'text' in node:
            try:
                text_out = interpolate(node['text'], state)
                if chat_mode and node_type != 'end':
                    print(f"**Coach:** {text_out}\n")
                elif not chat_mode or node_type == 'end':
                    print(text_out)
            except Exception as e:
                logger.error(f"Error interpolating text for node {current_id}: {e}")
                print("Error: Could not process reflection text.")

        if node_type == 'question':
            options = node.get('options', [])
            if not options:
                logger.error(f"Question node {current_id} has no options")
                break

            if not chat_mode:
                for i, opt in enumerate(options, 1):
                    print(f"  {i}) {opt['label']}")

            # Guardrail: Input validation with retry limits
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    prompt_text = "" if chat_mode else "\nSelect an option (1-{}): ".format(len(options))
                    choice = input(prompt_text).strip()

                    if not choice:
                        if not chat_mode:
                            print("Please make a selection.")
                        continue

                    idx = int(choice) - 1
                    if 0 <= idx < len(options):
                        selected = options[idx]

                        # Guardrail: Validate selected option structure
                        if not isinstance(selected, dict) or 'value' not in selected or 'label' not in selected:
                            logger.error(f"Invalid option structure in node {current_id}")
                            break

                        state['answers'][node['id']] = selected['value']
                        state['answer_labels'][node['id']] = selected['label']

                        if chat_mode:
                            print(f"**You:** {selected['label']}\n")

                        if verbose and not chat_mode:
                            print(f"[DEBUG] Q ({node['id']}): '{selected['label']}'")

                        if 'signal' in selected:
                            sig = selected['signal']
                            # Guardrail: Validate signal format
                            if not isinstance(sig, str) or ':' not in sig:
                                logger.warning(f"Invalid signal format: {sig}")
                            else:
                                state['signals'][sig] = state['signals'].get(sig, 0) + 1
                                if verbose and not chat_mode:
                                    print(f"[DEBUG] Signal: {sig} ✓")
                        break
                    else:
                        if not chat_mode:
                            print(f"Invalid choice. Please select 1-{len(options)}.")
                except ValueError:
                    if not chat_mode:
                        print("Please enter a valid number.")
                except KeyboardInterrupt:
                    print("\nSession interrupted by user.")
                    return
                except Exception as e:
                    logger.error(f"Unexpected error during input: {e}")
                    if not chat_mode:
                        print("An error occurred. Please try again.")

            else:
                # Max retries exceeded
                print("Too many invalid attempts. Ending session.")
                break

            if 'target' in node:
                current_id = node['target']
            else:
                idx = tree_data.index(node)
                current_id = tree_data[idx + 1]['id'] if idx + 1 < len(tree_data) else None
            
        elif node_type == 'decision':
            routed = False
            routing_rules = node.get('routing', [])
            if not routing_rules:
                logger.error(f"Decision node {current_id} has no routing rules")
                break

            for route in routing_rules:
                try:
                    condition = route.get('condition', '')
                    target = route.get('target', '')

                    if not condition or not target:
                        logger.warning(f"Invalid routing rule in node {current_id}: {route}")
                        continue

                    if evaluate_condition(condition, state):
                        if verbose and not chat_mode:
                            print(f"[DEBUG] DECISION {node['id']} matched condition -> Routing to {target}")

                        # Guardrail: Validate target exists
                        if target not in nodes:
                            logger.error(f"Decision node {current_id} routes to non-existent target: {target}")
                            break

                        current_id = target
                        routed = True
                        break
                except Exception as e:
                    logger.error(f"Error processing routing rule in node {current_id}: {e}")
                    continue

            if not routed:
                logger.error(f"No valid route found for decision node {current_id}")
                if not chat_mode:
                    print("Error: Could not determine next step in reflection.")
                break
                
        elif node_type in ['reflection', 'bridge', 'start', 'trajectory']:
            if verbose and node_type != 'start' and not chat_mode:
                print(f"[DEBUG] Rendered ({node_type}) {node['id']}")
            try:
                input("" if chat_mode else "\n[Press Enter to continue]")
            except KeyboardInterrupt:
                print("\nSession interrupted by user.")
                return

            if 'target' in node:
                current_id = node['target']
            else:
                idx = tree_data.index(node)
                current_id = tree_data[idx + 1]['id'] if idx + 1 < len(tree_data) else None
                
        elif node_type == 'summary':
            if verbose and not chat_mode:
                print("\n" + "═"*59)
                print("SIGNAL TALLY:")
                for axis in ['axis1', 'axis2', 'axis3']:
                    for pole in ['internal', 'external', 'contribution', 'entitlement', 'altrocentric', 'selfcentric']:
                        val = state['signals'].get(f"{axis}:{pole}", 0)
                        if val > 0:
                            print(f"  {axis}:{pole} = {val}")
                print("\nDOMINANT TRAITS:")
                for axis in ['axis1', 'axis2', 'axis3']:
                    dominant = get_dominant(axis, state)
                    print(f"  {axis}: {dominant}")
                print("═"*59)

            matched = False
            syntheses = node.get('syntheses', [])
            if not syntheses:
                logger.warning(f"Summary node {current_id} has no synthesis rules")

            for synth in syntheses:
                try:
                    condition = synth.get('condition', '')
                    if not condition:
                        continue

                    if evaluate_condition(condition, state):
                        matched = True
                        if verbose and not chat_mode:
                            print(f"\n[DEBUG] SUMMARY SYNTHESIS MATCHED:\n  Condition: {condition}\n")

                        # Guardrail: Safe interpolation of summary text
                        try:
                            if chat_mode:
                                narrative = interpolate(synth.get('narrative', ''), state)
                                edge_case = interpolate(synth.get('edge_case', ''), state)
                                forward = interpolate(synth.get('forward', ''), state)
                                print(f"**Coach:** {narrative}")
                                if edge_case:
                                    print(edge_case)
                                if forward:
                                    print(forward)
                                print()
                            else:
                                narrative = interpolate(synth.get('narrative', ''), state)
                                edge_case = interpolate(synth.get('edge_case', ''), state)
                                forward = interpolate(synth.get('forward', ''), state)
                                print(narrative)
                                if edge_case:
                                    print("\n" + edge_case)
                                if forward:
                                    print("\n" + forward)
                        except Exception as e:
                            logger.error(f"Error interpolating summary text: {e}")
                            print("Error generating personalized summary.")
                        break
                except Exception as e:
                    logger.error(f"Error processing synthesis rule: {e}")
                    continue

            if not matched:
                try:
                    default_text = interpolate(node.get('default', 'Session Complete.'), state)
                    if chat_mode:
                        print(f"**Coach:** {default_text}\n")
                    else:
                        print("\n" + default_text)
                except Exception as e:
                    logger.error(f"Error interpolating default summary: {e}")
                    print("Session Complete.")

            try:
                input("" if chat_mode else "\n[Press Enter to finish]")
            except KeyboardInterrupt:
                print("\nSession interrupted by user.")
                return

            current_id = node.get('target')

        elif node_type == 'end':
            current_id = None  # End the session

        else:
            logger.warning(f"Unknown node type: {node_type} for node {current_id}")
            break

    if iteration_count >= max_iterations:
        logger.error("Session terminated due to excessive iterations (possible loop)")
        print("Session ended due to safety timeout.")

    logger.info(f"Session completed after {iteration_count} steps")

if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(description='Run the Reflection Agent.')
        parser.add_argument('--verbose', action='store_true', help='Enable debug mode to trace paths and signals.')
        parser.add_argument('--chat', action='store_true', help='Format output as a humanly chat transcript.')
        args = parser.parse_args()

        script_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(script_dir, '..', 'tree', 'reflection-tree.json')

        # Guardrail: Load and validate tree before running
        tree = load_tree(json_path)
        run_agent(tree, verbose=args.verbose, chat_mode=args.chat)

    except KeyboardInterrupt:
        print("\nProgram interrupted by user.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"An error occurred: {e}")
        print("Please check the logs for more details.")
        sys.exit(1)
