from flask import Flask, render_template, request, redirect, url_for
import yaml
import os

app = Flask(__name__)

# Load questions from QA.yaml
def load_questions():
    yaml_path = os.path.join(os.path.dirname(__file__), 'QA.yaml')
    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)
    return data['questions']

questions = load_questions()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/quiz/<int:question_index>', methods=['GET', 'POST'])
def quiz(question_index):
    # Initialize score if not provided in POST request
    score = request.args.get('score', 0, type=int)

    # Ensure the question index is valid
    if question_index >= len(questions):
        return redirect(url_for('result', score=score))

    if request.method == 'POST':
        user_answer = request.form.get('answer')
        # Check if the answer is correct
        if user_answer == questions[question_index]['answer']:
            score += 1

        # Redirect to the next question or to the results
        if question_index + 1 < len(questions):
            return redirect(url_for('quiz', question_index=question_index + 1, score=score))
        else:
            return redirect(url_for('result', score=score))

    # Get the current question
    question = questions[question_index]
    return render_template('quiz.html', question=question, question_index=question_index, total=len(questions))

@app.route('/result', methods=['GET'])
def result():
    score = request.args.get('score', 0, type=int)  # Get the score from the query parameters
    total = len(questions)  # Total number of questions
    return render_template('result.html', score=score, total=total)  # Pass score and total to the results template

if __name__ == '__main__':
    app.run(debug=True)