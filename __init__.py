from flask import Flask, render_template, request, redirect, url_for, jsonify, abort, flash #, session

from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from datetime import datetime
from utils import *
from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy.orm import aliased 
from sqlalchemy import exists


login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.secret_key = 'quiz'
   
    app.config['LOGIN_VIEW'] = 'login'
    
    login_manager.init_app(app)

    return app

app = create_app()
SECRET_ADMIN_CODE = "123" 
@app.route('/home')

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@login_manager.user_loader
def load_user(user_id):
    with Session_SQLAlch() as sql_session:
        user = sql_session.query(User).get(int(user_id))
        print(user)
        return user

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')
        with Session_SQLAlch() as sql_session:
            user = sql_session.query(User).filter_by(username=username).first()
            if user and check_password_hash(user.password, password):
                if login_user(user): 
                    if user.is_admin():
                        return redirect(url_for('admin'))
                    else:
                        return redirect(url_for('user'))
            else:
                flash('Invalid username or password.', 'error')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        adminToggle = request.form.get('adminToggle', 'off') == 'on'
        secretCode = request.form.get('secretCode')

        with Session_SQLAlch() as sql_session:            
            try:
                existing_user = sql_session.query(User).filter_by(username=username).one()
                flash('Username already exists. Please choose a different one.')
                return redirect(url_for('register'))
            
            except Exception as e:
                if adminToggle and secretCode != SECRET_ADMIN_CODE:
                    flash('Invalid code for admin registration.')
                    return redirect(url_for('register'))

            hashed_password = generate_password_hash(password)

            if adminToggle:
                firstname = request.form['Firstname']
                lastname = request.form['Lastname']
                user = User(username=username, password=hashed_password, is_adminDB=adminToggle, first_name=firstname, last_name=lastname)
            else:
                user = User(username=username, password=hashed_password, is_adminDB=adminToggle, first_name=None, last_name=None)

            sql_session.add(user)
            sql_session.commit()
            return render_template('login.html')
    return render_template('register.html')

@app.route('/logout')
@login_required  
def logout():
    logout_user()  
    return redirect('/')

@app.route('/admin', methods=['GET', 'POST'])
@login_required 
def admin():
    if current_user.is_adminDB != True:
        flash("You don't have access here, you've been redirected to User page")
        return redirect(url_for('user'))
    else:
        with Session_SQLAlch() as sql_session:
            admin_name = request.args.get('admin_name', default=None) 

            questions = sql_session.query(Question).all()
            quizzes = sql_session.query(Quiz).all()

            selected_quiz_id = None

            if request.method == 'POST':
                selected_quiz_id = request.form.get('quiz-select')

                if 'edit_quiz' in request.form:
                    return redirect(url_for('edit_quiz', quiz_id=selected_quiz_id))
                elif 'delete_quiz' in request.form:
                    return redirect(url_for('delete_quiz', quiz_id=selected_quiz_id))
                elif 'review_quiz' in request.form:
                    return redirect(url_for('admin_quiz_review', quiz_id=selected_quiz_id))

        return render_template('admin.html', questions=questions, quizzes=quizzes, admin_name=admin_name)

@app.route('/user')
@login_required
def user():
    user_id = current_user.id
    username = current_user.username
    with Session_SQLAlch() as sql_session:
        quizzes = sql_session.query(Quiz).all()

        approved_quizzes = sql_session.query(Quiz, QuizResults).\
        join(QuizResults, Quiz.id == QuizResults.quiz_id).\
        filter(QuizResults.is_approved == True, QuizResults.user_id == user_id).all()
    return render_template('user.html', quizzes=quizzes, approved_quizzes = approved_quizzes, username = username)

@app.route('/create_quiz', methods=['POST'])
@login_required 
def create_quiz():
    with Session_SQLAlch() as sql_session:
        quiz_name = request.form.get('quizname')

        quiz_exists = sql_session.query(exists().where(Quiz.name == quiz_name)).scalar()
        if quiz_exists:
            flash('Quiz name already exists, please pick a different name.')
            return redirect(url_for('admin'))

        new_quiz = Quiz(quiz_name)
        sql_session.add(new_quiz)
        sql_session.commit()
        return redirect(url_for('quiz_maker', quiz_id=new_quiz.id))

@app.route('/quiz_maker/<quiz_id>')
@login_required
def quiz_maker(quiz_id):
    with Session_SQLAlch() as sql_session:
        quiz = sql_session.query(Quiz).get(quiz_id)
        questions = sql_session.query(Question).filter(Question.quiz_id == quiz_id).all()

        return render_template('quiz_maker.html', quiz=quiz, questions=questions)

@app.route('/edit_quiz', methods=['POST'])
@login_required 
def edit_quiz(): 
    if request.method == 'POST':
        quiz_id = request.form['quiz_id']
        with Session_SQLAlch() as sql_session:
            quiz = sql_session.query(Quiz).get(quiz_id)
            questions = sql_session.query(Question).filter_by(quiz_id=quiz_id).all()
            return render_template('quiz_maker.html', quiz=quiz, questions=questions)

@app.route('/create_essay_question/<quiz_id>', methods=['POST']) 
@login_required 
def create_essay_question(quiz_id): 
    with Session_SQLAlch() as sql_session:
        question_text = request.form.get('question_text')
        new_question = Question(quiz_id=quiz_id, question_text=question_text, question_type='essay', options=None)
        sql_session.add(new_question)
        sql_session.commit()
        return redirect(url_for('quiz_maker', quiz_id=quiz_id))

@app.route('/create_multiple_choice_question/<quiz_id>', methods=['POST']) 
@login_required
def create_multiple_choice_question(quiz_id):
    with Session_SQLAlch() as sql_session:
        sql_session = Session_SQLAlch()
        question_text = request.form.get('question_text')
        options_text = request.form.getlist('options')  
        options_str = ';;;'.join(options_text)

        new_question = Question(quiz_id=quiz_id, question_text=question_text, question_type='multiple_choice', options=options_str)
        sql_session.add(new_question)
        sql_session.commit()

        return redirect(url_for('quiz_maker', quiz_id=quiz_id))

@app.route('/create_choice_question/<quiz_id>', methods=['POST'])
@login_required 
def create_choice_question(quiz_id):
    with Session_SQLAlch() as sql_session:      
        question_text = request.form.get('question_text')
        options_text = request.form.getlist('options')  
        options_str = ';;;'.join(options_text)

        new_question = Question(quiz_id=quiz_id, question_text=question_text, question_type='choice', options=options_str)
        sql_session.add(new_question)
        sql_session.commit()
    return redirect(url_for('quiz_maker', quiz_id=quiz_id))

@app.route('/edit_question/<int:question_id>', methods=['POST'])
@login_required 
def edit_question(question_id):
    try:
        question_text = request.form.get('question_text')
        options = request.form.get('options')

        with Session_SQLAlch() as sql_session:
            question = sql_session.query(Question).filter_by(id=question_id).first()
            if question is None:
                return jsonify({'error': 'Question not found'}), 404

            question.question_text = question_text
            question.options = options
            quiz_id = question.quiz_id
            sql_session.commit()

        return redirect(url_for('quiz_maker', quiz_id=quiz_id))

    except Exception as e:
        app.logger.error(str(e))
        return jsonify({'error': 'An error occurred while processing your request'}), 500


@app.route('/delete_quiz', methods=['POST'])
@login_required 
def delete_quiz():
    quiz_id = request.form.get('quiz_id')
    with Session_SQLAlch() as sql_session:
        try:
            sql_session.query(UserAnswer).filter(UserAnswer.quiz_id == quiz_id).delete()
            # question_ids = [q.id for q in sql_session.query(Question).filter(Question.quiz_id == quiz_id).all()]
            sql_session.query(Question).filter(Question.quiz_id == quiz_id).delete()
            sql_session.query(QuizResults).filter(QuizResults.quiz_id == quiz_id).delete()
            sql_session.query(Quiz).filter(Quiz.id == quiz_id).delete()
            sql_session.commit()
        except:
            sql_session.rollback()
            raise
        finally:
            sql_session.close()
    return redirect(url_for('admin'))

@app.route('/delete_question/<int:question_id>', methods=['POST'])
@login_required 
def delete_question(question_id):
    with Session_SQLAlch() as sql_session:
        try:
            sql_session.query(UserAnswer).filter(UserAnswer.question_id == question_id).delete()
            
            question = sql_session.query(Question).get(question_id)
            if question:
                sql_session.delete(question)
                sql_session.commit()
                return jsonify({'message': 'Question deleted successfully.'}), 200
            else:
                return jsonify({'error': 'Question not found.'}), 404
        except Exception as e:
            sql_session.rollback()
            return jsonify({'error': str(e)}), 500

'''
@app.route('/start_quiz', methods=['POST'])
def start_quiz():
    quiz_id = request.form['quiz-select']   
    quiz_category = fetch_query_results("SELECT category FROM quizzes WHERE id=%s", (quiz_id,))[0][0]
    return redirect(url_for('display_quiz', quiz_id=quiz_id))
'''
@app.route('/quiz', methods=['POST'])
@login_required 
def display_quiz():
    quiz_id = request.form['quiz-select']
    # quiz_name = request.form['quiz-select']
    username = current_user.username
    with Session_SQLAlch() as sql_session:
        quiz_name = sql_session.query(Quiz).filter(Quiz.id == quiz_id).first()
        questions = sql_session.query(Question).filter(Question.quiz_id == quiz_id).all() 

    return render_template('quiz.html', questions=questions, quiz_id=quiz_id, \
                           quiz_name=quiz_name.name, username = username)

@app.route('/admin_quiz_review', methods=['GET', 'POST'])
@login_required 
def admin_quiz_review():
    if request.method == 'POST':
        quiz_id = request.form.get('quiz_id')
        approve_quiz = request.form.get('approve_quiz')
        if approve_quiz:
            try: 
                approve_quiz = int(approve_quiz)
            except ValueError:
                abort(400) 
            quiz_result = session_SQLALCH.query(QuizResults).filter(
                QuizResults.quiz_id == quiz_id,
                QuizResults.user_id == approve_quiz
            ).first()
            if quiz_result:
                quiz_result.is_approved = True
                session_SQLALCH.commit()
                     
        quiz_results = session_SQLALCH.query(QuizResults, User, Quiz).join(
            User, User.id == QuizResults.user_id
        ).join(
            Quiz, Quiz.id == QuizResults.quiz_id
        ).filter(
            QuizResults.quiz_id == quiz_id,
            QuizResults.is_approved == False
        ).all()

        if quiz_results:
            return render_template('admin_quiz_review.html', quiz_results=quiz_results)
        else:
            return render_template('empty_quiz.html') 

    return redirect(url_for('admin'))

@app.route('/approve_quiz/<int:quiz_id>/<int:user_id>', methods=['POST'])
@login_required 
def approve_quiz(quiz_id, user_id):

    quiz_result = session_SQLALCH.query(QuizResults).filter(
        QuizResults.quiz_id == quiz_id,
        QuizResults.user_id == user_id
    ).first()

    if quiz_result:
        quiz_result.is_approved = 1
        session_SQLALCH.commit()
        flash('Quiz has been approved!', 'success')
    else:
        flash('Quiz could not be found.', 'danger')

    return redirect(url_for('admin_quiz_review'))

@app.route('/review_answers/<int:quiz_id>/<int:user_id>', methods=['GET', 'POST'])
@login_required 
def review_answers(quiz_id, user_id):
    if request.method == 'POST':
        answer_id = request.form.get('answer_id')
        feedback = request.form.get('feedback')
        
        user_answer = session_SQLALCH.query(UserAnswer).filter(UserAnswer.id == answer_id).first()
        if user_answer:
            user_answer.comment = feedback
            session_SQLALCH.commit()
            flash('Feedback has been saved!', 'success')
        else:
            flash('Answer could not be found.', 'danger')
        
        return redirect(url_for('review_answers', quiz_id=quiz_id))

    else:
        Quiz_alias = aliased(Quiz)
        User_alias = aliased(User)
        Question_alias = aliased(Question)

        user_answers = session_SQLALCH.query(UserAnswer, Question_alias.question_text, Quiz_alias.name, User_alias.username).\
                join(Question_alias, UserAnswer.question_id == Question_alias.id).\
                join(Quiz_alias, UserAnswer.quiz_id == Quiz_alias.id).\
                join(User_alias, UserAnswer.user_id == User_alias.id).\
                filter(UserAnswer.quiz_id == quiz_id, UserAnswer.user_id == user_id).all()

        return render_template('review_answers.html', user_answers=user_answers, quiz_id=quiz_id)

@app.route('/submit_feedback/<int:quiz_id>', methods=['POST'])
@login_required 
def submit_feedback(quiz_id):
    feedback = request.form.get('feedback')
    answer_id = request.form.get('answer_id')

    # Retrieve the answer
    user_answer = session_SQLALCH.query(UserAnswer).filter(UserAnswer.id == answer_id).first()

    # Check if the answer exists
    if user_answer is None:
        flash('Answer not found.', 'danger')
        return redirect(url_for('review_answers', quiz_id=quiz_id))

    # Update the feedback
    user_answer.comment = feedback
    session_SQLALCH.commit()

    flash('Feedback has been submitted!', 'success')
    return redirect(url_for('review_answers', quiz_id=quiz_id, user_id=user_answer.user_id))

@app.route('/submit_quiz_feedback', methods=['POST'])
@login_required 
def submit_quiz_feedback():
    feedback = request.form.get('quiz_feedback')
    quiz_result_id = request.form.get('quiz_result_id')

    # Retrieve the quiz result
    quiz_result = session_SQLALCH.query(QuizResults).filter(QuizResults.id == quiz_result_id).first()

    # Check if the quiz result exists
    if quiz_result is None:
        flash('Quiz Result not found.', 'danger')
        return redirect(url_for('admin'))  # redirecting to admin as no quiz_id is available

    # Update the feedback
    quiz_result.comment = feedback
    session_SQLALCH.commit()

    flash('Quiz Feedback has been submitted!', 'success')
    return redirect(url_for('admin_quiz_review', quiz_id=quiz_result.quiz_id)) # Use quiz_id from quiz_result object

@app.route('/approve_answer/<int:answer_id>', methods=['POST'])
@login_required 
def approve_answer(answer_id):
    user_answer = session_SQLALCH.query(UserAnswer).filter(UserAnswer.id == answer_id).first()
    if user_answer:
        user_answer.is_approved = 1
        try:
            session_SQLALCH.commit()
            flash('Answer has been approved!', 'success')
        except Exception as e:
            # Log the exception and display an error message
            print(e)
            flash('An error occurred while trying to approve the answer.', 'danger')
    else:
        flash('Answer could not be found.', 'danger')

    return redirect(url_for('review_answers', user_id=user_answer.user_id,  quiz_id=user_answer.quiz_id if user_answer else 1))  # If user_answer is None, redirect to a default quiz_id or handle appropriately

'''@app.route('/get_user_answers', methods=['GET'])
@login_required 
def get_user_answers():
    quiz_result_id = request.args.get('quiz_result_id')

    user_answers = session_SQLALCH.query(
        UserAnswer.id,
        Question.question_text,
        UserAnswer.answer,
        Question.question_type,
        UserAnswer.created_at
    ).join(Question, UserAnswer.question_id == Question.id).filter(
        UserAnswer.quiz_id == quiz_result_id,
        UserAnswer.is_approved == 1
    ).all()

    # Transform user_answers into a list of dictionaries
    user_answers = [
        {
            'question_text': user_answer.question_text,
            'answer': user_answer.answer
        }
        for user_answer in user_answers
    ]

    return jsonify(user_answers=user_answers)
'''
@app.route('/submit_quiz', methods=['POST'])
@login_required 
def submit_quiz():
    quiz_id = request.form['quiz_id']
    user_id = current_user.id
    user_answers = []
    timestamp = datetime.now()

    for key, value in request.form.items():
        if key.startswith('answer_'):
            question_id = int(key[7:])
            user_answers.append((quiz_id, question_id, user_id, value, timestamp))

    ''' LEGACY: see and enjoy :) it works'''
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        # Insert user answers into user_answers table
        cursor.executemany("INSERT INTO user_answers (quiz_id, question_id, users_id, answer, created_at) VALUES (%s, %s, %s, %s, %s)", user_answers)
        # connection.commit()
        # Insert quiz result into quiz_result table
        cursor.execute("INSERT INTO quiz_results (quiz_id, users_id) VALUES (%s, %s)", (quiz_id, user_id))
        connection.commit()
        flash('Quiz submitted successfully')        
    except Exception as e:
        # Rollback the transaction in case of any error
        connection.rollback()
        flash('An error occurred while submitting the quiz: ' + str(e))
        cursor.close()
        connection.close()

    return redirect(url_for('user'))

@app.route('/user_answers', methods=['POST'])
@login_required
def user_answers():
    user_id = current_user.id 
    quiz_id = request.form['approved-quiz-select']
    if user_id:
        with Session_SQLAlch() as sql_session:
            # Query user_answers table to get the quizzes done by the current user
            # user_quizzes = sql_session.query(UserAnswer.quiz_id).filter(UserAnswer.user_id == user_id).all()
            # quiz_ids = [quiz_id for quiz_id, in user_quizzes]            
            # Query quizzes table to get the details of the quizzes
            # quizzes = sql_session.query(Quiz).filter(Quiz.id.in_(quiz_ids)).all()

            Quiz_alias = aliased(Quiz)
            User_alias = aliased(User)
            Question_alias = aliased(Question)

            user_answers = sql_session.query(UserAnswer, Question_alias.question_text, Quiz_alias.name, User_alias.username).\
                    join(Question_alias, UserAnswer.question_id == Question_alias.id).\
                    join(Quiz_alias, UserAnswer.quiz_id == Quiz_alias.id).\
                    join(User_alias, UserAnswer.user_id == User_alias.id).\
                    filter(UserAnswer.quiz_id == quiz_id, UserAnswer.user_id == user_id, UserAnswer.is_approved == True).all()

    return render_template('review_answers_user.html', user_answers=user_answers, quiz_id=quiz_id)

'''
def quiz_results(): #??????????????????????????????????????????????????????????????????????????????????????????????????????????
    user_id = session.get('user_id')
    if user_id:
        with Session_SQLAlch() as sql_session:            
            # Query quizzes table to get the details of the quizzes
            quizzes = sql_session.query(Quiz).filter(Quiz.id.in_(quiz_ids)).all()
        return render_template('user_quizzes.html', quizzes=quizzes)
'''
if __name__ == '__main__':
    app.run(debug=True)
