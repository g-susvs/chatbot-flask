import difflib
import os
from flask import Flask, request, jsonify
from chatbot import get_answer_for_mistake, load_knowledge_base, find_best_match, get_answer_for_question, save_knowledge_base
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app)
knowledge_base_path = 'knowledge_base.json'
kb = load_knowledge_base(knowledge_base_path)

active_banned_words = False

@app.route('/', methods=['GET'])
def main_route():
    try:
        return jsonify({'GET': 'chatbot-server'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/chat', methods=['POST'])
def chat():
    global active_banned_words  # Indica que esta variable está en el ámbito global

    def findE(user_input):
        # Comprobar palabras bananadeas
        banned_words = kb.get("banned_words", [])
        has_banned_words = any(ban.lower() in user_input.lower() for ban in banned_words)

        if has_banned_words:
            response = 'No puedo generar insultos ni contenido ofensivo. ¿En qué más puedo ayudarte?'
            active_banned_words = True
        else:
            active_banned_words = False

            if any(ban["ban"] in user_input.lower() for ban in kb.get("ban", [])):
                response = get_answer_for_mistake(user_input, kb)
            elif best_match:
                response = get_answer_for_question(best_match, kb)
            else:
                response = "No sé la respuesta. ¿Puede enseñármela?"

        return response

    def learn(user_input):
        learn = False
        banned_words = kb.get("banned_words", [])
        has_banned_words = any(ban.lower() in user_input.lower() for ban in banned_words)

        if has_banned_words:
            response = 'No puedo generar insultos ni contenido ofensivo. ¿En qué más puedo ayudarte?'
            active_banned_words = True
        else:
            active_banned_words = False
            learn = True
            kb["question"].append({"question": user_input, "answer": ""})  # Aquí es necesario ajustar la lógica para obtener la respuesta del usuario
            save_knowledge_base('knowledge_base.json', kb)
            response = '¡Gracias! ¡He aprendido algo nuevo!'

        return response

    try:
        user_input = request.json['user_input']
        
        # Lógica del chatbot
        best_match = find_best_match(user_input, [q["question"] for q in kb["question"]])
        
        response = findE(user_input)
        
        if not active_banned_words and response == "No sé la respuesta. ¿Puede enseñármela?":
            Learn = True
            response = learn(user_input)

        return jsonify({'response': response, 'active_banned_words': active_banned_words})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
