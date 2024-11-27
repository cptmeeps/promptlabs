from typing import Dict, Any, List
import yaml
from pathlib import Path
from string import Template
import json

from prompt_manager import PromptManager
from llm_api import LLMAPIManager

class ChainManager:
    def __init__(
        self, 
        chains_dir: str = "chains",
        prompts_dir: str = "prompts",
        debug: bool = False
    ):
        self.chains_dir = Path(chains_dir)
        self.debug = debug
        self.prompt_manager = PromptManager(prompts_dir=prompts_dir, debug=debug)
        self.llm_manager = LLMAPIManager()
        
    def load_chain(self, chain_file: str) -> Dict[str, Any]:
        """Load and validate a chain configuration file"""
        chain_path = self.chains_dir / chain_file
        
        try:
            with open(chain_path) as f:
                chain_config = yaml.safe_load(f)
                
            if self.debug:
                print(f"\nDebug: Loaded chain configuration:")
                print(json.dumps(chain_config, indent=2))
                
            self._validate_chain_config(chain_config)
            return chain_config
        except Exception as e:
            raise ValueError(f"Error loading chain configuration: {str(e)}")
            
    def _validate_chain_config(self, config: Dict[str, Any]):
        """Validate the chain configuration structure"""
        required_keys = ['name', 'steps', 'input_variables']
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing required key '{key}' in chain configuration")
                
        for step in config['steps']:
            required_step_keys = ['name', 'prompt', 'model', 'output_key']
            for key in required_step_keys:
                if key not in step:
                    raise ValueError(f"Missing required key '{key}' in step configuration")
                    
    def _substitute_variables(self, template: str, variables: Dict[str, Any]) -> str:
        """Safely substitute variables in template strings"""
        return Template(template).safe_substitute(variables)
        
    def execute_chain(self, chain_file: str, input_variables: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a chain with given input variables"""
        chain_config = self.load_chain(chain_file)
        context = input_variables.copy()
        
        if self.debug:
            print(f"\nDebug: Executing chain '{chain_config['name']}'")
            print(f"Input variables: {json.dumps(input_variables, indent=2)}")
            
        # Validate input variables
        for var in chain_config['input_variables']:
            if var not in input_variables:
                raise ValueError(f"Missing required input variable: {var}")
                
        # Execute each step in the chain
        for step in chain_config['steps']:
            if self.debug:
                print(f"\nDebug: Executing step '{step['name']}'")
                
            # Prepare template variables
            template_vars = context.copy()
            if 'template_vars' in step:
                for key, value in step['template_vars'].items():
                    template_vars[key] = self._substitute_variables(value, context)
                    
            # Generate prompt using PromptManager
            prompt_result = self.prompt_manager.compose_prompt(
                [step['prompt']], 
                template_vars
            )
            
            # Execute LLM call
            model_config = step['model']
            response = self.llm_manager.generate(
                model_config['provider'],
                prompt_result
            )
            
            # Store result in context
            context[step['output_key']] = response
            
            if self.debug:
                print(f"Step '{step['name']}' output stored in '{step['output_key']}'")
                
        return context

def main():
    # Example usage
    chain_manager = ChainManager(debug=True)
    
    input_vars = {
        "text": "The quick brown fox jumps over the lazy dog.",
        "tone": "professional"
    }
    
    try:
        results = chain_manager.execute_chain(
            "example_chain.yaml",
            input_vars
        )
        
        print("\nChain execution results:")
        print(json.dumps(results, indent=2))
        
    except Exception as e:
        print(f"Error executing chain: {str(e)}")

if __name__ == "__main__":
    main() 