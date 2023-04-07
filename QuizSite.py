from flask import Flask, render_template, request, redirect, url_for

QuizSite = Flask(__name__)
QuizSite.config['APPLICATION_ROOT'] = '/templates'

QuizNamesList = []
QuizQuestionDictList = []

def authenticate(username, password, role):
    return username == "user" and password == "password"


@QuizSite.route('/')
def loginTemplate():
    return render_template('/login.html')

@QuizSite.route('/login', methods=['POST'])
def loginSubmit():
    selected_option = int(request.form.get('loginButtons'))
    if selected_option == 1:  # user
        return redirect(url_for('mainUser'))
    elif selected_option == 2:  # admin
        return redirect(url_for('mainAdmin'))
    else:
        return 'Invalid credentials. Please try again.', 401

@QuizSite.route('/mainAdmin')
def mainAdmin():
    return render_template('/mainAdmin.html')

@QuizSite.route('/mainUser')
def mainUser():
    return render_template('/mainUser.html')



@QuizSite.route('/addQuestionAdmin', methods=['POST'])
def create_quiz():
    quiz_name = request.form.get('quizName')
    if quiz_name not in QuizNamesList:
        QuizNamesList.append(quiz_name)
        QuizQuestionDictList.append({})
    else:
        quizIndex = QuizNamesList.index(quiz_name)
    
    if request.method == 'POST' and 'addQuestionAdmin' in request.form:
        return render_template('addQuestionAdmin.html', quiz_name=quiz_name)
    else:
        return render_template('addQuestionAdmin.html', quiz_name=quiz_name)

if __name__ == '__main__':
    QuizSite.run(debug=True)
