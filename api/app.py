import os
from datetime import timedelta
from flask import Flask, request, jsonify
from models import db,User
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from dotenv import load_dotenv

# pipenv install flask flask-sqlalchemy flask-migrate flask-cors flask-jwt-extended flask-bcrypt python-dotenv

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config["JWT_SECRET_KEY"] = os.getenv("SUPER_SECRET_KEY")  # Corregir el nombre de la clave
app.config["SECRET_KEY"] = os.getenv("PASS_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=3)
jwt = JWTManager(app) 
db.init_app(app)
migrate = Migrate(app, db)
CORS(app)
jwt = JWTManager(app)
bcrypt = Bcrypt(app)
expires = timedelta(minutes=2)

@app.route("/api/test", methods=["GET"])
def test_message():
  return jsonify({"msg":"Hello from the backend"})

@app.route("/api/register", methods=["POST"])
def register():
  user = User()
  email = request.json.get("email")
  username = request.json.get("username")
  user_exist = User.query.filter_by(username=username).first()
  email_exist = User.query.filter_by(email=email).first()
  if user_exist:
    return jsonify({"msg": "Nombre de usuario ya en uso"}), 400
  elif email_exist:
    return jsonify({"msg": "Email ya en uso"}), 400
  else:
    user.username = username
    user.active = True
    user.email = email
    password = request.json.get("password")
    password_hash = bcrypt.generate_password_hash(password)
    user.password = password_hash

    db.session.add(user)
    db.session.commit()

    return jsonify({"msg": "user created successfully!!!"}), 201
  
@app.route("/api/login", methods=["POST"])
def login():
  username = request.json.get("username")
  password = request.json.get("password")

  user_exist = User.query.filter_by(username=username).first()

  if user_exist is not None:
    if bcrypt.check_password_hash(user_exist.password, password):
      token = create_access_token(identity=username, expires_delta = expires)

      return jsonify({
        "token": token,
        "username": user_exist.username,
      }), 200
    else:
      return jsonify({"error": "Wrong credentials"}), 401
  else:
    return jsonify({"error": "User does not exists"}), 404
  
@app.route('/api/auth')
@jwt_required()
def auth():
    current_user = get_jwt_identity()
    return {'username':current_user},200


if __name__ == "__main__":
  app.run(host="localhost", port=5000)