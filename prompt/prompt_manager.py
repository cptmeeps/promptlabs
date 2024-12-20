import os
from pathlib import Path
from typing import List, Dict, Any
from jinja2 import Environment, FileSystemLoader
import yaml
import json

class PromptManager:
    def __init__(self, prompts_dir: str = None, debug: bool = False):
        if prompts_dir is None:
            prompts_dir = str(Path(__file__).parent / "templates")
        self.prompts_dir = prompts_dir
        self.debug = debug
        templates_path = Path(prompts_dir)
        self.env = Environment(loader=FileSystemLoader(str(templates_path)))

    def load_prompt_from_file(self, prompt_filename: str) -> str:
        full_path = os.path.join(self.prompts_dir, prompt_filename)
        if self.debug:
            print(f"\n[PromptManager] Debug: Loading prompt from file: {full_path}")
        
        try:
            with open(full_path, 'r') as f:
                content = f.read()
                if self.debug:
                    print("\n[PromptManager] Debug: Raw file content:")
                    print(content)
                return content
        except FileNotFoundError:
            raise FileNotFoundError(f"Could not find prompt file at {full_path}")

    def compose_prompt(self, prompt_filenames: List[str], template_vars: Dict[str, Any]) -> List[Dict[str, Any]]:
        composed_prompts = []
        
        if self.debug:
            print("\n[PromptManager] Debug: Template variables:")
            print(json.dumps(template_vars, indent=2))
        
        for prompt_filename in prompt_filenames:
            if self.debug:
                print(f"\n[PromptManager] Debug: Processing prompt file: {prompt_filename}")
            
            # Load the template and render it with template_vars
            template = self.env.get_template(prompt_filename)
            prompt_text = template.render(template_vars)
            
            if self.debug:
                print("\n[PromptManager] Debug: Rendered template:")
                print(prompt_text)
            
            # Parse the prompt text as YAML and ensure it's a list
            try:
                parsed_content = yaml.safe_load(prompt_text.strip())
                if self.debug:
                    print("\n[PromptManager] Debug: Parsed YAML content:")
                    print(json.dumps(parsed_content, indent=2))
                
                # If the content is a single dictionary, wrap it in a list
                if isinstance(parsed_content, dict):
                    parsed_content = [parsed_content]
                elif not isinstance(parsed_content, list):
                    raise ValueError(f"Prompt file {prompt_filename} must contain a dictionary or list of dictionaries")
                
                if self.debug:
                    print("\n[PromptManager] Debug: Normalized content (as list):")
                    print(json.dumps(parsed_content, indent=2))
                
                composed_prompts.extend(parsed_content)
            except yaml.YAMLError as e:
                raise ValueError(f"Failed to parse prompt as YAML in {prompt_filename}: {str(e)}")
        
        if self.debug:
            print("\n[PromptManager] Debug: Final composed prompt chain:")
            print(json.dumps(composed_prompts, indent=2))
        
        return composed_prompts


if __name__ == "__main__":
    pass