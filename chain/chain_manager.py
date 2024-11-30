from pathlib import Path
import yaml
import json
from typing import Dict, Any, List, Callable, Optional
from prompt.prompt_manager import PromptManager
from llm_api import AnthropicProvider

class ChainManager:
    """Manages the execution of chains defined in YAML"""
    
    # Registry for step functions
    STEP_FUNCTIONS: Dict[str, Callable] = {}
    
    @classmethod
    def register_step_function(cls, name: str):
        """Decorator to register a step function"""
        def decorator(func):
            cls.STEP_FUNCTIONS[name] = func
            return func
        return decorator
    
    def __init__(self, debug: bool = False):
        # Set default directories
        chains_dir = str(Path(__file__).parent / "templates")
        
        self.chains_dir = Path(chains_dir)
        self.debug = debug
        self.prompt_manager = PromptManager(debug=debug)
        self.llm_provider = AnthropicProvider(debug=debug)
        self.steps = []
        self.context = {}
        
    def load_chain(self, chain_file: str):
        """Load chain configuration from YAML file"""
        chain_path = self.chains_dir / chain_file
        
        try:
            with open(chain_path, 'r') as f:
                config = yaml.safe_load(f)
                
            if self.debug:
                print(f"\nDebug: Loaded chain configuration:")
                print(json.dumps(config, indent=2))
                
            self.name = config.get('name', 'unnamed_chain')
            self.description = config.get('description', '')
            
            # Initialize steps from config
            for step_config in config['steps']:
                if step_config['step_function'] not in self.STEP_FUNCTIONS:
                    raise ValueError(f"Unknown step function: {step_config['step_function']}")
                    
                self.steps.append({
                    'name': step_config['name'],
                    'input_key': step_config.get('input_key'),
                    'output_key': step_config.get('output_key'),
                    'step_function': step_config['step_function'],
                    'prompt_templates': step_config.get('prompt_templates', [])
                })
                
        except Exception as e:
            raise ValueError(f"Error loading chain configuration: {str(e)}")
            
    def get_context(self) -> Dict[str, Any]:
        """Get the current chain context"""
        return self.context
        
    def add_to_context(self, key: str, value: Any):
        """Add a value to the chain context"""
        self.context[key] = value
        
    def execute(self) -> Dict[str, Any]:
        """Execute all steps in the chain"""
        if self.debug:
            print(f"\nExecuting chain: {self.name}")
            print(f"Initial context: {json.dumps(self.context, indent=2)}")
            
        for step in self.steps:
            if self.debug:
                print(f"\nExecuting step: {step['name']}")
                
            # Get the function from registry
            func = self.STEP_FUNCTIONS[step['step_function']]
            
            # Execute the function without input_data
            result = func(
                chain=self,
                prompt_templates=step.get('prompt_templates', []),
                debug=self.debug
            )
            
            # Store result in context if output_key is specified
            if step.get('output_key'):
                self.add_to_context(step['output_key'], result)
            
            if self.debug:
                print(f"Step result: {result}")
                print(f"Updated context: {json.dumps(self.context, indent=2)}")
                
        return self.context

# Register built-in step functions
@ChainManager.register_step_function("process_with_llm")
def process_with_llm(
    chain: Any,
    prompt_templates: List[str] = None,
    debug: bool = False
) -> str:
    """Process prompts through LLM and update context"""
    context = chain.get_context()
    composed_prompts = chain.prompt_manager.compose_prompt(prompt_templates, context)
    return chain.llm_provider.process_prompt(composed_prompts)

@ChainManager.register_step_function("generate_rules")
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

@ChainManager.register_step_function("solve_puzzle_with_rules")
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

@ChainManager.register_step_function("evaluate_response")
def evaluate_response(
    chain: Any,
    prompt_templates: List[str] = None,
    debug: bool = False
) -> None:
    """Evaluate the generated outputs against the correct outputs."""
    context = chain.get_context()
    problem_set = context.get('problem_set')
    test_results = context.get('test_results')
    test_examples = problem_set.get('test', [])
    evaluation_results = []
    for idx, (test_result, test_example) in enumerate(zip(test_results, test_examples), start=1):
        generated_output = test_result.get('output_grid')
        correct_output = test_example.get('output')
        match = generated_output == correct_output
        evaluation_results.append({
            'test_index': idx,
            'match': match,
            'test_input': test_result.get('test_input'),
            'generated_output': generated_output,
            'correct_output': correct_output,
            'explanation': test_result.get('explanation')
        })
    chain.add_to_context('evaluation_results', evaluation_results)
