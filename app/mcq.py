from flask import Blueprint, request, jsonify
from app.agent import run_graph
from langchain_together import ChatTogether
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from config import Config
from langchain_core.prompts import ChatPromptTemplate
import json


# Initialize the Together AI model
llm = ChatTogether(
    together_api_key=Config.TOGETHER_API,
    model="meta-llama/Llama-3-70b-chat-hf",
)

# Create a ChatPromptTemplate
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert quiz evaluator. Your task is to evaluate quiz responses and provide feedback.
    You will receive a quiz response with the correct answers, the user's answers, and a list of topics covered.
    Evaluate the performance and provide:
    1. A comment on the overall performance.
    2. A list of topics where the performance was weak (if any). 
    If all questions were answered correctly, the list of weak topics should be empty.
    Format your response as a JSON with keys 'comment' and 'weak_topics'."""),

    ("human", """
Quiz_Response: {{
  "questions": {quiz_response}
}}
Topics_Covered: {topics_covered}
""")

])

# Create the LangChain
chain = prompt | llm

mcq = Blueprint('mcq', __name__)

@mcq.route('/generate', methods=['POST'])
def generate_mcq():
    data = request.get_json()
    if not data or 'topics' not in data or 'num_questions' not in data:
        return jsonify({"error": "Missing 'topics' or 'num_questions' in request body"}), 400

    topics = data['topics']
    num_questions = data['num_questions']

    if not isinstance(topics, list):
        return jsonify({"error": "Topics should be a list"}), 400

    try:
        all_questions = []
        for topic in topics:
            result = run_graph(topic, num_questions)
            
            # Assuming run_graph returns a dict with 'mcq_json' key containing the questions
            if 'mcq_json' in result and 'questions' in result['mcq_json']:
                questions = result['mcq_json']['questions']
                for question in questions:
                    question['topic'] = topic
                all_questions.extend(questions)
            else:
                # If the structure is different, you might need to adjust this part
                return jsonify({"error": f"Unexpected result structure for topic: {topic}"}), 500

        return jsonify({
            "questions": all_questions
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@mcq.route('/evaluate-quiz', methods=['POST'])
def evaluate_quiz():
    data = request.json
    
    if not data or 'quiz_response' not in data or 'topics_covered' not in data:
        return jsonify({"error": "Invalid input. Please provide quiz_response and topics_covered."}), 400

    # Convert quiz_response to a string representation
    quiz_response_str = "\n".join([f"{q}: {a}" for q, a in data['quiz_response'].items()])
    topics_covered_str = ", ".join(data['topics_covered'])

    # Run the LangChain
    try:
        result = chain.invoke({
            "quiz_response": quiz_response_str,
            "topics_covered": topics_covered_str
        })
        # Parse the result as JSON
        evaluation = json.loads(result.content)
    except Exception as e:
        return jsonify({"error": f"Error processing with LLM: {str(e)}"}), 500

    # Ensure the LLM response contains the required fields
    if 'comment' not in evaluation or 'weak_topics' not in evaluation:
        return jsonify({"error": "Invalid LLM response format"}), 500

    return jsonify(evaluation)