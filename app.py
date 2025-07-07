from flask import Flask, render_template, request, jsonify
from chatbot import ToolChatbot
from config import STATIC_DIR, TEMPLATES_DIR

app = Flask(__name__, 
           static_folder=str(STATIC_DIR), 
           template_folder=str(TEMPLATES_DIR))
chatbot = ToolChatbot()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_input = request.form.get('message', '').strip()
        if not user_input:
            return jsonify({'error': 'Empty message'}), 400
        
        response = chatbot.generate_response(user_input)
        return jsonify({'response': response})
    
    except Exception as e:
        error_msg = str(e)
        if "quota" in error_msg.lower():
            return jsonify({'error': 'API quota exceeded. Please try again later.'}), 429
        elif "not found" in error_msg.lower():
            return jsonify({'error': 'Model unavailable. Contact support.'}), 503
        else:
            return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)