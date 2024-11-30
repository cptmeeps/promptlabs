from typing import Any, List

def process_with_llm(
    chain: Any,
    prompt_templates: List[str] = None,
    debug: bool = False
) -> str:
    """Process prompts through LLM and update context"""
    context = chain.get_context()
    composed_prompts = chain.prompt_manager.compose_prompt(prompt_templates, context)
    return chain.llm_provider.process_prompt(composed_prompts) 