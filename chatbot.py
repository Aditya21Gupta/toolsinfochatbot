import json
import time
import google.generativeai as genai
from config import DATASET_PATH, GEMINI_API_KEY, GEMINI_MODEL

class ToolChatbot:
    def __init__(self):
        """Initialize the chatbot with proper error handling"""
        try:
            # Configure API
            genai.configure(api_key=GEMINI_API_KEY)
            
            # Initialize model
            self.model = genai.GenerativeModel(
                GEMINI_MODEL,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 1000
                },
                safety_settings=[
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
                ]
            )
            
            # Load dataset
            self.dataset = self.load_dataset()
            self.last_request_time = time.time()
            self.request_count = 0
            
        except Exception as e:
            print("Initialization error:", str(e))
            raise

    def load_dataset(self):
        """Load dataset with robust error handling"""
        try:
            print("Loading dataset from:", DATASET_PATH)
            with open(DATASET_PATH, 'r') as f:
                data = json.load(f)
                if not isinstance(data.get('tools', []), list):
                    raise ValueError("Dataset must contain 'tools' array")
                print("Loaded", len(data['tools']), "tools")
                return data
        except Exception as e:
            print("Error loading dataset:", str(e))
            return {"tools": []}

    def get_context_prompt(self):
        """Generate focused context prompt"""
        if not self.dataset.get('tools'):
            return "I currently have no tool data available."
        
        # Build knowledge base (limit to first 20 tools for efficiency)
        tools_info = []
        for tool in self.dataset['tools'][:20]:
            tools_info.append(
                f"Tool ID: {tool.get('TLMS_TOOL_ID', 'N/A')}\n"
                f"- Part: {tool.get('TLMS_PRC_PART', 'N/A')}\n"
                f"- Category: {tool.get('TLMS_CHILD_PART_CATEGORY', 'N/A')}\n"
                f"- Status: {tool.get('TLMS_TOOL_STATUS', 'N/A')}"
            )
        
        return (
            "You are a tool information assistant. "
            "Here are some tools I know about:\n\n"
            + "\n\n".join(tools_info) + "\n\n"
            "Rules:\n"
            "1. Only answer about these specific tools\n"
            "2. For unknown tools, say 'I don't have information about that tool'\n"
            "3. Keep responses concise (1-3 sentences)"
        )

    def _check_rate_limit(self):
        """Prevent API rate limiting"""
        now = time.time()
        elapsed = now - self.last_request_time
        
        if elapsed > 60:  # Reset counter after 1 minute
            self.request_count = 0
            self.last_request_time = now
        
        self.request_count += 1
        if self.request_count > 50:  # Stay under 50 requests/minute
            wait_time = 60 - elapsed
            time.sleep(wait_time)
            self.last_request_time = time.time()
            self.request_count = 0

    def generate_response(self, user_input):
        """Generate response with comprehensive error handling"""
        self._check_rate_limit()
        
        try:
            print("Processing query:", user_input)
            
            # Build the prompt correctly
            full_prompt = f"{self.get_context_prompt()}\n\nQuestion: {user_input}"
            
            # Get API response - use simple text input format
            response = self.model.generate_content(full_prompt)
            
            # Handle response
            if response.text:
                return response.text
            else:
                print("Empty response. Full API output:", response)
                return "I didn't receive a valid response."
                
        except Exception as e:
            print("Full error details:", str(e))
            return "Sorry, I encountered an error. Please try again."

    def update_dataset(self, new_data):
        """Update dataset with validation"""
        try:
            if not isinstance(new_data.get('tools', []), list):
                raise ValueError("Data must contain 'tools' array")
                
            with open(DATASET_PATH, 'w') as f:
                json.dump(new_data, f, indent=2)
            self.dataset = new_data
            return True
            
        except Exception as e:
            print("Error updating dataset:", str(e))
            return False