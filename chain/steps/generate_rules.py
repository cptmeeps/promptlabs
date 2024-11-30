from typing import Any, List
import json

def generate_rules(
    chain: Any,
    prompt_templates: List[str] = None,
    debug: bool = False
) -> None:
    """Generate rules by processing the problem set and updating the context."""
    context = chain.get_context()
    problem_set = context.get('problem_set')
    train_examples = problem_set.get('train', [])
    current_rules = None  # No rules initially
    prompt_manager = chain.prompt_manager
    llm_provider = chain.llm_provider
    visualizer = TextVisualizer()
    
    for idx, example in enumerate(train_examples, start=1):
        input_grid = example['input']
        output_grid = example['output']
        problem_set_representation = visualizer.visualize_pair(
            input_grid,
            output_grid,
            representation_name='vertical_with_numbers'
        )
        template_vars = {
            'problem_set_representation': problem_set_representation,
            'existing_rules': json.dumps(current_rules, indent=2) if current_rules else None
        }
        composed_prompts = prompt_manager.compose_prompt(
            prompt_templates,
            template_vars
        )
        response = llm_provider.process_prompt(composed_prompts)
        response_json = json.loads(response)
        generated_rules = response_json.get('rules', [])
        explanation = response_json.get('explanation', '')
        current_rules = {
            'rules': generated_rules,
            'explanation': explanation
        }
        rules_key = f"rules_after_example_{idx}"
        chain.add_to_context(rules_key, current_rules)
        chain.add_to_context('current_rules', current_rules) 