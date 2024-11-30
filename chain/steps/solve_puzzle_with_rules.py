from typing import Any, List, Dict
import json


def solve_puzzle_with_rules(
    chain: Any,
    prompt_templates: List[str] = None,
    debug: bool = False
) -> List[Dict[str, Any]]:
    """Solve the test puzzle using the generated rules and update the context with the results."""
    context = chain.get_context()
    problem_set = context.get('problem_set')
    current_rules = context.get('current_rules')
    test_examples = problem_set.get('test', [])
    prompt_manager = chain.prompt_manager
    llm_provider = chain.llm_provider
    visualizer = TextVisualizer()
    test_results = []
    
    for idx, example in enumerate(test_examples, start=1):
        test_input_grid = example['input']
        test_output_grid = None
        test_input_representation = visualizer.visualize_pair(
            test_input_grid,
            test_output_grid,
            representation_name='vertical'
        )
        template_vars = {
            'test_input_representation': test_input_representation,
            'current_rules': json.dumps(current_rules, indent=2)
        }
        composed_prompts = prompt_manager.compose_prompt(
            prompt_templates,
            template_vars
        )
        response = llm_provider.process_prompt(composed_prompts)
        response_json = json.loads(response)
        output_grid = response_json.get('output_grid', [])
        explanation = response_json.get('explanation', '')
        test_results.append({
            'test_input': test_input_grid,
            'output_grid': output_grid,
            'explanation': explanation
        })
    
    chain.add_to_context('test_results', test_results)
    return test_results 