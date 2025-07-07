from config import GEMINI_API_KEY, GEMINI_MODEL
import google.generativeai as genai

def test_connection():
    print(f"Testing connection with model: {GEMINI_MODEL}")
try:
    import google.generativeai as genai
    from config import GEMINI_API_KEY
    print("All imports successful!")
    print(f"API Key: {'set' if GEMINI_API_KEY else 'not set'}")
except ImportError as e:
    print(f"Import error: {e}")

if __name__ == "__main__":
    test_connection()
