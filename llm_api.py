from abc import ABC, abstractmethod
from typing import Dict, Any, List
import anthropic
import json
from pprint import pprint

class LLMProvider(ABC):
    def __init__(self, debug: bool = False):
        self.debug = debug

    @abstractmethod
    def convert_to_messages(self, prompt_dicts: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], str]:
        """Convert list of prompt dictionaries to provider-specific message format and system message"""
        pass

    @abstractmethod
    def generate(self, messages: tuple[List[Dict[str, Any]], str]) -> Any:
        """Make API call and return generated text"""
        pass

    @abstractmethod
    def parse_response(self, response: Any) -> str:
        """Parse provider-specific response into plain text"""
        pass

    def process_prompt(self, prompt_dicts: List[Dict[str, Any]]) -> str:
        """Main workflow to process a prompt chain through the LLM"""
        messages_and_system = self.convert_to_messages(prompt_dicts)
        if self.debug:
            print("\nDebug: Message chain and system message:")
            messages, system = messages_and_system
            print("\nMessages:")
            print(json.dumps(messages, indent=2))
            print("\nSystem message:")
            print(json.dumps(system, indent=2))
            
        response = self.generate(messages_and_system)
        
        if self.debug:
            print("\nDebug: Raw API Response:")
            if isinstance(response, anthropic.types.Message):
                debug_response = {
                    "id": response.id,
                    "type": response.type,
                    "role": response.role,
                    "content": [{"type": c.type, "text": c.text} for c in response.content],
                    "model": response.model,
                    "stop_reason": response.stop_reason,
                    "stop_sequence": response.stop_sequence,
                    "usage": {
                        "input_tokens": response.usage.input_tokens,
                        "output_tokens": response.usage.output_tokens
                    }
                }
                print(json.dumps(debug_response, indent=2))
            else:
                print("Response type:", type(response))
                print("Response:", response)
            
        return self.parse_response(response)

class AnthropicProvider(LLMProvider):
    def __init__(self, model: str = "claude-3-5-sonnet-20240620", debug: bool = False):
        """Initialize Anthropic provider using ANTHROPIC_API_KEY from environment variables"""
        super().__init__(debug=debug)
        self.client = anthropic.Anthropic()  # Will automatically use ANTHROPIC_API_KEY env var
        self.model = model

    def extract_system_message(self, messages: List[Dict[str, Any]]) -> tuple[str, List[Dict[str, Any]]]:
        """Extract system messages and combine them, returning the system message and remaining messages."""
        system_messages = []
        other_messages = []
        
        for message in messages:
            if message['role'] == 'system':
                system_messages.append(message['content'])
            else:
                other_messages.append(message)
        
        system_message = ' '.join(system_messages)
        return system_message, other_messages

    def convert_to_messages(self, prompt_dicts: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], str]:
        """Convert prompt dictionaries to Anthropic's message format, handling system messages specially."""
        system_message, other_messages = self.extract_system_message(prompt_dicts)
        
        # Convert remaining messages to Anthropic's format
        converted_messages = [
            {
                "role": msg.get("role", "user"),
                "content": msg["content"]
            }
            for msg in other_messages
        ]
        
        return converted_messages, system_message

    def generate(self, messages_and_system: tuple[List[Dict[str, Any]], str]) -> Any:
        """Generate response using Anthropic's API with proper system message handling."""
        converted_messages, system_message = messages_and_system
        
        # Create the API request with system message if present
        request_args = {
            "model": self.model,
            "messages": converted_messages,
            "max_tokens": 4096,
            "temperature": 0.0
        }
        
        if system_message:
            request_args["system"] = system_message
            
        response = self.client.messages.create(**request_args)
        return response

    def parse_response(self, response: Any) -> str:
        return response.content[0].text

def main():
    print("\n=== Starting LLM API Test ===")
    
    # Initialize Anthropic provider with debug mode enabled
    print("\n1. Setting up Anthropic provider...")
    provider = AnthropicProvider(debug=True)
    print("✓ Anthropic provider initialized")

    # Example prompt dictionaries showing system message handling
    print("\n2. Creating test prompt chain...")
    prompt_dicts = [
        {
            "role": "system",
            "content": "You are a helpful AI assistant."
        },
        {
            "role": "system",
            "content": "Always be concise and clear."
        },
        {
            "role": "user",
            "content": "Tell me a short story about a robot."
        }
    ]
    print("Input prompt chain:")
    for i, msg in enumerate(prompt_dicts):
        print(f"  Message {i+1}: [{msg['role']}] {msg['content']}")

    # Generate using Anthropic
    print("\n3. Generating response from Anthropic...")
    try:
        response = provider.process_prompt(prompt_dicts)
        print("\n=== Response ===")
        print(response)
        print("=== End Response ===")
        print("\n✓ Test completed successfully")
    except Exception as e:
        print(f"\n❌ Error during generation: {str(e)}")
        raise

if __name__ == "__main__":
    main() 