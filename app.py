import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from chatbot import find_best_match, get_answer_for_question
from flask_cors import CORS
from pymongo import MongoClient

# Cargar variables de entorno
load_dotenv()
mongodb_uri = os.getenv("MONGODB_URI")

# conexion hacia mongo
myClient = MongoClient(mongodb_uri)
myDb = myClient['chatbotdb']
knowledge_base_collection = myDb['knowledge_base']
banned_words_collection = myDb['banned_words']

app = Flask(__name__)
cors = CORS(app)

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

    #* ==
    banned = banned_words_collection.find()
    banned_words = banned[0]['words']

    def findE(user_input):
       
        # Comprobar palabras bananadeas
        has_banned_words = any(ban.lower() in user_input.lower() for ban in banned_words)

        if has_banned_words:
            response = 'No puedo generar insultos ni contenido ofensivo. ¿En qué más puedo ayudarte?'
        else:

            if best_match:
                response = get_answer_for_question(best_match, knowledge_base_collection.find())
            else:
                response = "No sé la respuesta. ¿Puede enseñármela?"

        return response

    def learn(user_input, old_input):
       
        has_banned_words = any(ban.lower() in user_input.lower() for ban in banned_words)

        if has_banned_words:
            response = 'No puedo generar insultos ni contenido ofensivo. ¿En qué más puedo ayudarte?'
        else:
            knowledge_base_collection.insert_one({"question": old_input, "answer": user_input})  # Aquí es necesario ajustar la lógica para obtener la respuesta del usuario
            response = '¡Gracias! ¡He aprendido algo nuevo!'

        return response

    try:
        user_input = request.json['user_input']
        old_input = request.json['old_input'] or ''
        
        if not active_banned_words and old_input:
            response = learn(user_input, old_input)
            return jsonify({'response': response, 'active_banned_words': active_banned_words})

         # Lógica del chatbot
        best_match = find_best_match(user_input, [q["question"] for q in knowledge_base_collection.find()])
        response = findE(user_input)
        if not active_banned_words and response == "No sé la respuesta. ¿Puede enseñármela?":
            response = "No sé la respuesta. ¿Puede enseñármela?"

        return jsonify({'response': response, 'active_banned_words': active_banned_words})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/learnqa', methods=['POST'])
def learnQuestinAndAnswer():
    try:
        question = request.json['question']
        answer = request.json['answer']
        
        knowledge_base_collection.insert_one({"question": question, "answer": answer})

        return jsonify({'msg': "He aprendido algo nuevo"})

    except Exception as e:
        return jsonify({'error': str(e)}), 400



if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
