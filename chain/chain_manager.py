from pathlib import Path
import yaml
import json
from typing import Dict, Any, List, Callable, Optional
from prompt.prompt_manager import PromptManager
from llm_api import AnthropicProvider
from .steps import process_with_llm, generate_rules, solve_puzzle_with_rules

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
ChainManager.register_step_function("process_with_llm")(process_with_llm)
ChainManager.register_step_function("generate_rules")(generate_rules)
ChainManager.register_step_function("solve_puzzle_with_rules")(solve_puzzle_with_rules)
