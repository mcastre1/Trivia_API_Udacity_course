import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app)

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response
    
    # Helper method for paginating questions
    def paginate_questions(request, selection):
        page = request.args.get("page", 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions = [question.format() for question in selection]
        current_questions = questions[start:end]

        return current_questions

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories', methods=['GET'])
    def get_categories():
        # Create data list of json objects with format method from Category class.
        data = [category.format() for category in Category.query.all()]

        # Return success and data.
        return jsonify({
            'success':True,
            'categories':data
        })
    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions', methods=['GET'])
    def get_questions():
        questions = paginate_questions(request, Question.query.all())
        categories = {category.id:category.type for category in Category.query.all()}

        return jsonify({
            'success':True,
            'questions':questions,
            'total_questions':len(Question.query.all()),
            'categories': categories,
            'current_category': None
        })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):
        question = Question.query.get(id)
        question.delete()

        return jsonify({
            'success':True
        })
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()

        if not 'searchTerm' in body:
            question = body.get('question')
            answer = body.get('answer')
            difficulty = body.get('difficulty')
            category = body.get('category')

            new_question = Question(question=question, answer=answer, difficulty=difficulty, category=category)
            new_question.insert()

            return jsonify({
                'success':True
            })
        else:
            searchTerm = body.get('searchTerm')
            questions = Question.query.filter(Question.question.ilike(f'%{searchTerm}%')).all()

            return jsonify({
                'success':True,
                'questions':[question.format() for question in questions],
                'totalQuestions': len(questions),
                'currentCategory': None
            })


    

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:id>/questions', methods=['GET'])
    def get_questions_by_category(id):
        questions = Question.query.filter(Question.category == id).all()

        return jsonify({
            'success': True,
            'questions': [question.format() for question in questions],
            'total_questions': len(questions),
            'current_category':id
        })
    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    app.route('/quizzes', methods=['POST'])
    def new_question():
        body = request.get_json()
        previous_questions = body.get('previous_questions')
        quiz_category = body.get('quiz_category')

        questionslist = []

        if(quiz_category == 0):
            questionslist = Question.query.all()
        else:
            questionslist = Question.get.filter(Question.category == quiz_category).all()

        next_question = questionslist[random.randint(0, len(questionslist) - 1)]

        while next_question.id in previous_questions:
            next_question = questionslist[random.randint(0, len(questionslist) - 1)]

        return ({
            'success':True,
            'question': next_question.format()
        })

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    return app

