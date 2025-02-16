from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from models import db, Message
from config import Config

app = Flask(__name__)
app.config.from_object("config.Config")  # Load existing config

# Initialize database and migrations
db.init_app(app)
migrate = Migrate(app, db)
CORS(app)

@app.route('/messages', methods=['GET'])
def get_messages():
    messages = Message.query.order_by(Message.created_at.asc()).all()
    return jsonify([msg.to_dict() for msg in messages]), 200

@app.route('/messages', methods=['POST'])
def create_message():
    data = request.get_json()
    if not data.get("body") or not data.get("username"):
        return jsonify({"error": "Missing required fields"}), 400

    new_message = Message(
        body=data["body"],
        username=data["username"]
    )
    db.session.add(new_message)
    db.session.commit()
    
    return jsonify(new_message.to_dict()), 201

@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    message = db.session.get(Message, id)  # Instead of Message.query.get(id)
    
    if not message:
        return jsonify({"error": "Message not found"}), 404
    
    data = request.get_json()
    if "body" in data:
        message.body = data["body"]

    db.session.commit()
    
    return jsonify(message.to_dict()), 200

@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    message = db.session.get(Message, id)

    if not message:
        return jsonify({"error": "Message not found"}), 404

    db.session.delete(message)
    db.session.commit()
    return '', 204  # No content

if __name__ == '__main__':
    app.run(debug=True)
