# import json
# import time
# import google.generativeai as genai
# import logging # Import logging

# from config import DATASET_PATH, GEMINI_API_KEY, GEMINI_MODEL

# # Configure logging
# # Changed to DEBUG for better visibility during debugging.
# # You can change it back to INFO for production.
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# class ToolChatbot:
#     # Define constants for clarity and easier modification
#     REQUEST_WINDOW_SECONDS = 60
#     MAX_REQUESTS_PER_WINDOW = 50
#     MAX_TOOLS_IN_CONTEXT = 20

#     def __init__(self):
#         """Initialize the chatbot with proper error handling"""
#         try:
#             # Configure API
#             genai.configure(api_key=GEMINI_API_KEY)

#             # Initialize model
#             self.model = genai.GenerativeModel(
#                 GEMINI_MODEL,
#                 generation_config={
#                     "temperature": 0.7,
#                     "max_output_tokens": 1000
#                 },
#                 safety_settings=[
#                     {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
#                     {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
#                 ]
#             )

#             # Load dataset
#             self.dataset = self.load_dataset()
#             self.last_request_time = time.time()
#             self.request_count = 0

#         except Exception as e:
#             logging.error("Initialization error: %s", str(e))
#             raise # Re-raise the exception to stop execution if init fails

#     def load_dataset(self):
#         """Load dataset with robust error handling"""
#         try:
#             logging.info("Loading dataset from: %s", DATASET_PATH)
#             with open(DATASET_PATH, 'r') as f:
#                 data = json.load(f)
#                 if not isinstance(data.get('tools', []), list):
#                     raise ValueError("Dataset must contain 'tools' array")
#                 logging.info("Loaded %d tools", len(data['tools']))
#                 return data
#         except FileNotFoundError:
#             logging.error("Dataset file not found at: %s", DATASET_PATH)
#             return {"tools": []} # Return empty tools if file not found
#         except json.JSONDecodeError:
#             logging.error("Error decoding JSON from dataset file: %s", DATASET_PATH)
#             return {"tools": []} # Return empty tools if JSON is malformed
#         except Exception as e:
#             logging.error("Error loading dataset: %s", str(e))
#             return {"tools": []} # Catch any other general exceptions

#     def get_context_prompt(self):
#         """Generate focused context prompt"""
#         if not self.dataset.get('tools'):
#             return "I currently have no tool data available."

#         tools_info = []
#         for tool in self.dataset['tools'][:self.MAX_TOOLS_IN_CONTEXT]: # Use constant
#             tools_info.append(
#                 f"🔧 Tool Summary\n"
#                 f"Tool ID: {tool.get('TLMS_TOOL_ID', 'N/A')}\n"
#                 f"Part No: {tool.get('TLMS_PRC_PART', 'N/A')}\n"
#                 f"Child Part No: {tool.get('TLMS_CHILD_PART_NO', 'N/A')}\n"
#                 f"Category: {tool.get('TLMS_CHILD_PART_CATEGORY', 'N/A')} ({tool.get('TLMS_CHILD_PART_CATEGORY_DET', 'N/A')})\n"
#                 f"Quantity: {tool.get('TLMS_CHILD_PART_QTY', 'N/A')}\n"
#                 f"Tool Status: {tool.get('TLMS_TOOL_STATUS', 'N/A')} ({tool.get('TLMS_ACTIVE_FLAG', 'N/A')})\n"
#                 f"Ownership Code: {tool.get('TLMS_TOOL_OWNERSHIP', 'N/A')}\n"
#                 f"Operation No: {tool.get('TLMS_TOOL_OPERATION_NO', 'N/A')}\n"
#                 f"Tool Has Detail: {tool.get('TLMS_TOOL_HAS_TOOL_DET', 'N/A')}\n"
#                 f"Asset No: {tool.get('TLMS_MSIL_ASSET_NO', 'N/A')} | Flag: {tool.get('TLMS_ASSET_NO_FLG', 'N/A')}\n"
#                 f"Defined Tool Life: {tool.get('TLMS_MSIL_DEFINED_TOOLLIFE', 'N/A')}\n"
#                 f"System Cal Stroke: {tool.get('TLMS_SYS_CAL_STROKE', 'N/A')} (Date: {tool.get('TLMS_SYS_CAL_STROKE_DT', 'N/A')})\n"
#                 f"Duplicate Set Tooling: {tool.get('TLMS_DUPLICATE_SET_TOOLING', 'N/A')}\n"
#                 f"Retooling Status: {tool.get('TLMS_RETOOLING_STS', 'N/A')}\n"
#                 f"Vendor Code: {tool.get('TLMS_VEND_CODE', 'N/A')} | Mail: {tool.get('TLMS_VENDOR_MAIL_ID', 'N/A')}\n"
#                 f"Tool Vend Date: {tool.get('TLMS_TOOL_VEND_DATE', 'N/A')}\n"
#                 f"Approved During RFQ: {tool.get('TLMS_TOOLS_APPROVED_DURING_RFQ', 'N/A')}\n"
#                 f"Close Date: {tool.get('TLMS_CLOSE_DATE', 'N/A')}\n"
#                 f"Created By: {tool.get('TLMS_CREATED_BY', 'N/A')} on {tool.get('TLMS_CREATED_ON', 'N/A')}\n"
#             )
#         return (
#             "You are a tool information assistant. "
#             "Here are some tools I know about:\n\n"
#             + "\n\n".join(tools_info) + "\n\n"
#             "Rules:\n"
#             "1. Only answer about these specific tools\n"
#             "2. For unknown tools, say 'I don't have information about that tool'\n"
#             "3. Keep responses concise (1-3 sentences)"
#         )

#     # FIX: Corrected indentation - This method must be at the same level as get_context_prompt
#     def _check_rate_limit(self):
#         """Prevent API rate limiting"""
#         now = time.time()
#         elapsed = now - self.last_request_time

#         if elapsed > self.REQUEST_WINDOW_SECONDS:  # Use constant
#             self.request_count = 0
#             self.last_request_time = now

#         self.request_count += 1
#         if self.request_count > self.MAX_REQUESTS_PER_WINDOW:  # Use constant
#             wait_time = self.REQUEST_WINDOW_SECONDS - elapsed
#             logging.warning("Rate limit hit. Waiting for %.2f seconds...", wait_time)
#             time.sleep(max(0, wait_time)) # Ensure wait_time is not negative
#             self.last_request_time = time.time()
#             self.request_count = 0

#     def generate_response(self, user_input):
#         """Generate response with comprehensive error handling"""
#         self._check_rate_limit()

#         try:
#             logging.info("Processing query: %s", user_input)

#             # Build the prompt correctly
#             full_prompt = f"{self.get_context_prompt()}\n\nQuestion: {user_input}"
#             logging.debug("Full prompt sent to model:\n%s", full_prompt) # Log the full prompt
#             logging.debug("Prompt length: %d characters", len(full_prompt)) # Log prompt length

#             # Get API response
#             response = self.model.generate_content(full_prompt)

#             # --- Debugging specific response issues ---
#             if not response.text:
#                 logging.warning("Empty response. Checking details...")
#                 if response.prompt_feedback and response.prompt_feedback.block_reason:
#                     logging.error("Prompt blocked due to: %s", response.prompt_feedback.block_reason)
#                     return "Sorry, your request was blocked due to safety concerns."
#                 elif response.candidates:
#                     # Check if any candidate was blocked by safety settings
#                     for candidate in response.candidates:
#                         if candidate.finish_reason:
#                             logging.warning("Candidate finish reason: %s", candidate.finish_reason)
#                         if candidate.safety_ratings:
#                             for rating in candidate.safety_ratings:
#                                 if rating.blocked:
#                                     logging.error("Candidate blocked by safety rating: Category=%s, Probability=%s", rating.category, rating.probability)
#                                     return "Sorry, the model's response was blocked due to safety concerns."
#                 logging.warning("No text response and no clear block/finish reason. Full API output: %s", response)
#                 return "I didn't receive a valid response from the AI model."
#             # --- End Debugging specific response issues ---

#             else:
#                 return response.text

#         except Exception as e:
#             logging.exception("Error generating response for query '%s':", user_input) # Use logging.exception to get full traceback
#             return "Sorry, I encountered an error. Please try again."

#     def update_dataset(self, new_data):
#         """Update dataset with validation"""
#         try:
#             if not isinstance(new_data.get('tools', []), list):
#                 raise ValueError("Data must contain 'tools' array")

#             with open(DATASET_PATH, 'w') as f:
#                 json.dump(new_data, f, indent=2)
#             self.dataset = new_data
#             logging.info("Dataset updated successfully.")
#             return True

#         except Exception as e:
#             logging.error("Error updating dataset: %s", str(e))
#             # FIX: Ensure a boolean is returned for update_dataset consistency
#             return False

import json
import time
import google.generativeai as genai
import logging
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
                    "temperature": 0.0,
                    "max_output_tokens": 10000
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
        for tool in self.dataset['tools'][:500]:
            tools_info.append(
                # f"Tool ID: {tool.get('TLMS_TOOL_ID', 'N/A')}\n"
                # f"- Part: {tool.get('TLMS_PRC_PART', 'N/A')}\n"
                # f"- Category: {tool.get('TLMS_CHILD_PART_CATEGORY', 'N/A')}\n"
                # f"- Status: {tool.get('TLMS_TOOL_STATUS', 'N/A')}"
                f"🔧 Tool Summary\n"
                f"Tool ID: {tool.get('TLMS_TOOL_ID', 'N/A')}\n"
                f"Part No: {tool.get('TLMS_PRC_PART', 'N/A')}\n"
                f"Child Part No: {tool.get('TLMS_CHILD_PART_NO', 'N/A')}\n"
                f"Category: {tool.get('TLMS_CHILD_PART_CATEGORY', 'N/A')} ({tool.get('TLMS_CHILD_PART_CATEGORY_DET', 'N/A')})\n"
                f"Quantity: {tool.get('TLMS_CHILD_PART_QTY', 'N/A')}\n"
                f"Tool Status: {tool.get('TLMS_TOOL_STATUS', 'N/A')} ({tool.get('TLMS_ACTIVE_FLAG', 'N/A')})\n"
                f"Ownership Code: {tool.get('TLMS_TOOL_OWNERSHIP', 'N/A')}\n"
                f"Operation No: {tool.get('TLMS_TOOL_OPERATION_NO', 'N/A')}\n"
                f"Tool Has Detail: {tool.get('TLMS_TOOL_HAS_TOOL_DET', 'N/A')}\n"
                f"Asset No: {tool.get('TLMS_MSIL_ASSET_NO', 'N/A')} | Flag: {tool.get('TLMS_ASSET_NO_FLG', 'N/A')}\n"
                f"Defined Tool Life: {tool.get('TLMS_MSIL_DEFINED_TOOLLIFE', 'N/A')}\n"
                f"System Cal Stroke: {tool.get('TLMS_SYS_CAL_STROKE', 'N/A')} (Date: {tool.get('TLMS_SYS_CAL_STROKE_DT', 'N/A')})\n"
                f"Duplicate Set Tooling: {tool.get('TLMS_DUPLICATE_SET_TOOLING', 'N/A')}\n"
                f"Retooling Status: {tool.get('TLMS_RETOOLING_STS', 'N/A')}\n"
                f"Vendor Code: {tool.get('TLMS_VEND_CODE', 'N/A')} | Mail: {tool.get('TLMS_VENDOR_MAIL_ID', 'N/A')}\n"
                f"Tool Vend Date: {tool.get('TLMS_TOOL_VEND_DATE', 'N/A')}\n"
                f"Approved During RFQ: {tool.get('TLMS_TOOLS_APPROVED_DURING_RFQ', 'N/A')}\n"
                f"Close Date: {tool.get('TLMS_CLOSE_DATE', 'N/A')}\n"
                f"Created By: {tool.get('TLMS_CREATED_BY', 'N/A')} on {tool.get('TLMS_CREATED_ON', 'N/A')}\n"
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
