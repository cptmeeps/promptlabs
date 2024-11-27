from chain_manager import ChainManager
from llm_api import AnthropicProvider

def main():
    # Initialize chain manager
    chain_manager = ChainManager(
        chains_dir="chains",
        prompts_dir="prompts",
        debug=True
    )
    
    # Register the Anthropic provider
    chain_manager.llm_manager.register_provider("anthropic", AnthropicProvider(debug=True))
    
    # Example of running the analysis chain
    chain_name = "example_chain.yaml"
    input_vars = {
        "text": "The quick brown fox jumps over the lazy dog. This classic pangram " 
                "has been used for centuries to display typefaces and test equipment.",
        "tone": "professional"
    }
    
    # Execute the chain
    try:
        results = chain_manager.execute_chain(chain_name, input_vars)
        
        # Print the results
        print("\nChain Results:")
        print("-" * 50)
        for key, value in results.items():
            print(f"\n{key.upper()}:")
            print(value)
            
    except Exception as e:
        print(f"Error running chain: {str(e)}")

if __name__ == "__main__":
    main() 