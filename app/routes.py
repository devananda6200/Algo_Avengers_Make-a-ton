from flask import Flask, request, jsonify, render_template
from app.models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from app.agent import run_graph  # Import the run_graph function from your agent.py file

app = Flask(__name__)

# Configure your app here (database, etc.)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'your_database_uri'
# db.init_app(app)

@app.route('/')
def home():
    return render_template('index.html')  # Ensure you have an index.html in your templates folder

@app.route('/auth/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "User already exists!"}), 400

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(email=email, password=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created!"}), 201

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        return jsonify({"message": "Login successful!"}), 200
    else:
        return jsonify({"message": "Invalid email or password!"}), 401

@app.route('/generate_mcq', methods=['POST'])
def generate_mcq():
    data = request.get_json()
    if not data or 'input' not in data or 'num_questions' not in data:
        return jsonify({"error": "Missing 'input' or 'num_questions' in request body"}), 400

    input_text = data['input']
    num_questions = data['num_questions']

    try:
        result = run_graph(input_text, num_questions)
        return jsonify({
            "rag_result": result["rag_result"],
            "mcq_json": result["mcq_json"]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)