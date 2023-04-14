from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
from utils import *

app = Flask(__name__)
app.secret_key = 'quiz'
app.config['APPLICATION_ROOT'] = '/templates'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_type = request.form['user_type']
        admin_name = request.form.get('name', None)  
        if user_type == 'admin' and not admin_name:
            message = 'Name required for admin login'
            return render_template('index.html', message=message)
        elif user_type == 'admin':    
            return redirect(url_for('admin', admin_name=admin_name))
        else:
            return redirect(url_for('user'))
    return render_template('index.html')

@app.route('/admin')
def admin():
    admin_name = request.args.get('admin_name', default=None)

    questions_raw = fetch_query_results("SELECT * FROM questions")
    questions = [dict(id=row[0], quiz_id=row[1], question_text=row[2], answer=row[3], category=row[4]) for row in questions_raw]

    quizzes = fetch_query_results("SELECT * FROM quizzes")

    return render_template('admin.html', questions=questions, quizzes=quizzes, admin_name=admin_name)

@app.route('/user')
def user():
    quizzes = fetch_query_results("SELECT * FROM quizzes")
    return render_template('user.html', quizzes=quizzes)

@app.route('/create_question', methods=['POST'])
def create_question():
    category = request.form['category']
    question_text = request.form['question_text']
    answer = request.form['answer']

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT category FROM quizzes WHERE category=%s", (category,))
    cursor.fetchall()
    if cursor.rowcount == 0:
        cursor.execute("INSERT INTO quizzes (category) VALUES (%s)", (category,))
        connection.commit()
    cursor.execute("SELECT id FROM quizzes WHERE category=%s", (category,)) 
    quiz_id = cursor.fetchall()[0][0]
    cursor.close()
    connection.close()

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO questions (quiz_id, question_text, answer, category) VALUES (%s, %s, %s, %s)", 
                (quiz_id, question_text, answer, category))
    connection.commit()
    cursor.close()
    connection.close()

    flash('Question created successfully')
    return redirect(url_for('admin'))

@app.route('/edit_question/<int:question_id>', methods=['GET', 'POST'])
def edit_question(question_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    if request.method == 'POST':
        category = request.form['category']
        question_text = request.form['question_text']
        answer = request.form['answer']
        cursor.execute("UPDATE questions SET category=%s, question_text=%s, answer=%s WHERE id=%s", 
                       (category, question_text, answer, question_id))
        connection.commit()
        flash('Question updated successfully')
        return redirect(url_for('admin'))
    else:
        cursor.execute("SELECT * FROM questions WHERE id=%s", (question_id,))
        question = cursor.fetchone()
        question_dict = dict(id=question[0], quiz_id=question[1], question_text=question[2], answer=question[3], category=question[4]) 
        return render_template('edit_question.html', question=question_dict)

@app.route('/delete_question/<int:question_id>', methods=['GET', 'POST'])
def delete_question(question_id):
    execute_query("DELETE FROM user_answers WHERE question_id=%s", (question_id,))
    execute_query("DELETE FROM questions WHERE id=%s", (question_id,))
    flash('Question deleted successfully')
    return redirect(url_for('admin'))

@app.route('/start_quiz', methods=['POST'])
def start_quiz():
    quiz_id = request.form['quiz-select']
    
    quiz_category = fetch_query_results("SELECT category FROM quizzes WHERE id=%s", (quiz_id,))[0][0]
    
    return redirect(url_for('display_quiz', quiz_id=quiz_id))

@app.route('/quiz/<int:quiz_id>', methods=['GET'])
def display_quiz(quiz_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM questions WHERE quiz_id=%s", (quiz_id,))
    questions = cursor.fetchall()
    quiz_category_selected = questions[0][4]
    cursor.close()
    connection.close()
    return render_template('quiz.html', questions=questions, quiz_id=quiz_id, quiz_category_selected=quiz_category_selected)

@app.route('/admin_quiz_details', methods=['GET', 'POST'])
def admin_quiz_details():
    if request.method == 'POST':
        quiz_id = request.form['quiz-select']
    else:
        return redirect(url_for('admin'))

    user_answers = fetch_query_results("""SELECT ua.id, q.question_text, ua.answer, q.answer, ua.created_at  
                                          FROM user_answers ua 
                                          JOIN questions q ON ua.question_id = q.id 
                                          WHERE ua.quiz_id = %s""", (quiz_id,))

    return render_template('admin_quiz_details.html', user_answers=user_answers)

@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    quiz_id = request.form['quiz_id']
    user_answers = []
    timestamp = datetime.now()

    for key, value in request.form.items():
        if key.startswith('answer_'):
            question_id = int(key[7:])
            user_answers.append((quiz_id, question_id, value, timestamp))

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.executemany("INSERT INTO user_answers (quiz_id, question_id, answer, created_at) VALUES (%s, %s, %s, %s)", 
                       user_answers)
    connection.commit()
    cursor.close()
    connection.close()

    flash('Quiz submitted successfully')
    return redirect(url_for('user'))

if __name__ == '__main__':
    app.run(debug=True)
