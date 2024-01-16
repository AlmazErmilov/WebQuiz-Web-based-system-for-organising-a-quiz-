from db_connection_config import HOST, USER, PASSWORD, DATABASE
from flask_login import UserMixin
import mysql.connector

from sqlalchemy.sql import func
from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session 

Base = declarative_base()

DATABASE_URL = f"mysql+mysqlconnector://{USER}:{PASSWORD}@{HOST}/{DATABASE}"
engine = create_engine(DATABASE_URL, echo=True)
Base.metadata.create_all(bind=engine)

Session_SQLAlch = sessionmaker(bind=engine)
session_SQLALCH = scoped_session(Session_SQLAlch)

class Question(Base):
    __tablename__ = 'questions'

    id = Column('id', Integer, primary_key=True, autoincrement = True)
    quiz_id = Column('quiz_id', Integer, ForeignKey('quizzes.id')) 
    question_text = Column('text', String)
    question_type = Column('type', String) 
    options = Column('options', String)

    def __init__(self, quiz_id, question_text, question_type, options): 
        super().__init__(quiz_id=quiz_id, question_text=question_text, question_type=question_type, 
                         options=options) 
    
    def __repr__(self):
        return f"{self.id}; {self.quiz_id}; {self.question_text}; {self.question_type}"
    
class Quiz(Base):
    __tablename__ = 'quizzes'

    id = Column('id', Integer, primary_key=True, autoincrement = True)
    name = Column('name', String)

    def __init__(self, name):
        super().__init__(name=name)

    def __repr__(self): 
        return f"{self.id}; {self.name}"
    
class QuizResults(Base):
    __tablename__ = 'quiz_results'

    id = Column('id', Integer, primary_key=True, autoincrement = True)
    quiz_id = Column('quiz_id', Integer, ForeignKey('quizzes.id'))
    user_id = Column('users_id', Integer, ForeignKey('users.id')) 
    is_approved = Column('is_approved', Boolean)
    comment = Column('comment', String)

    def __init__(self, quiz_id, user_id, is_approved, comment): 
        super().__init__(quiz_id = quiz_id, user_id = user_id, is_approved = is_approved, 
                         comment = comment)

    def __repr__(self): 
        return f"{self.id}; {self.quiz_id}; {self.user_id}; {self.is_approved}"

class UserAnswer(Base):
    __tablename__ = 'user_answers'

    id = Column('id', Integer, primary_key=True, autoincrement = True)

    quiz_id = Column('quiz_id', Integer, ForeignKey('quizzes.id')) # FK
    question_id = Column('question_id', Integer, ForeignKey('questions.id')) # FK
    user_id = Column('users_id', Integer, ForeignKey('users.id')) # FK
    user = relationship("User", backref="answers") 

    answer = Column('answer', String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    comment = Column('comment', String)
    is_approved = Column('is_approved', Boolean)    

    def __init__(self, quiz_id, question_id, user_id, answer, created_at, comment, is_approved):
        super().__init__(quiz_id = quiz_id, question_id = question_id, 
                         user_id = user_id, answer = answer, created_at = created_at,
                         comment = comment, is_approved = is_approved)

    def __repr__(self):
        return f"{self.id}; {self.quiz_id}; {self.question_id}; {self.user_id}; {self.answer}; {self.created_at}; {self.comment}; {self.is_approved}"

class User(Base, UserMixin):
    __tablename__ = 'users'

    id = Column('id', Integer, primary_key=True, autoincrement = True)
    username = Column('username', String)
    password = Column('password', String)
    is_adminDB = Column('is_adminDB', Boolean)
    first_name = Column('Firstname', String)
    last_name = Column('Lastname', String)

    def __init__(self, username, password, is_adminDB, first_name, last_name):
        super().__init__(username = username, password = password, is_adminDB = is_adminDB, 
                         first_name = first_name, last_name = last_name)
        self.is_adminDB=is_adminDB

    def __repr__(self):
        return f"<User id={self.id}, username={self.username}, is_adminDB={self.is_adminDB}>"

    def to_dict(self):
        return {'id': self.id, 
                'username': self.username, 
                'password': self.password, 
                'is_adminDB': self.is_adminDB, 
                'first_name': self.first_name, 
                'last_name': self.last_name}

    def is_admin(self):
        return self.is_adminDB
    
    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.id

    def is_authenticated(self):
        return True 

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False

#LEGACY FUNKSJONER#
def get_db_connection():
    connection = mysql.connector.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=DATABASE)
    return connection

def fetch_query_results(query, params=None):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        return results
    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))

def execute_query(query, params=None):
    connection = get_db_connection()
    cursor = connection.cursor()
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()
#############################