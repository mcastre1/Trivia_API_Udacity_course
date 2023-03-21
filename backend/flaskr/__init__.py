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
    CORS(app, resources={"/": {"origins": "*"}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS,PATCH"
        )
        return response
    
    # Helper method for paginating questions
    def paginate_questions(request, selection):
        page = request.args.get('page', 1, type=int)

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
        #data = [category.format() for category in Category.query.all()]
        try:
            categories = {}
        
            for category in Category.query.all():
                categories[category.id] = category.type

            if len(categories) == 0:
                abort(404)
            

            # Return success and data.
            return jsonify({
                'success':True,
                'categories':categories
            })
        except:
            abort(400)
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
        try:
            #print(request.args)
            questions = paginate_questions(request, Question.query.all())
            categories = {category.id:category.type for category in Category.query.all()}

            if not questions:
                abort(404)

            return jsonify({
                'success':True,
                'questions':questions,
                'total_questions':len(Question.query.all()),
                'categories': categories
            })
        # Removed current_category:None
        except:
            abort(400)

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):
        # Send a request to delete a question with id.
        try:
            question = Question.query.get(id)

            if question == None:
                abort(404)

            question.delete()

            return jsonify({
            'success':True
            })
        except:
            abort(400)

        
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    # For the Post new question I decided to do both POST in the same route but check for the parameter 'search'
    # Please see the route below.
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    # For the Post new question I decided to do both POST in the same route but check for the parameter 'search'
    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()
        try:
        # Here is where we decide if we are searching or creating a new question
        # Here we create a new question
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
            else: # AND here is where we search for questions with a substring.
                searchTerm = body.get('searchTerm')
                questions = Question.query.filter(Question.question.ilike(f'%{searchTerm}%')).all()

                if questions == []:
                    abort(404)

                return jsonify({
                    'success':True,
                    'questions':[question.format() for question in questions],
                    'totalQuestions': len(questions),
                    'currentCategory': None
                })
        except:
            abort(400)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:id>/questions', methods=['GET'])
    def get_questions_by_category(id):
        # Get all questions with the given category id.
        try:
            questions = Question.query.filter(Question.category == id).all()

            if len(questions) == 0:
                abort(404)

            return jsonify({
                'success': True,
                'questions': [question.format() for question in questions],
                'total_questions': len(questions),
                'current_category':id
            })
        except:
            abort(400)
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

    @app.route('/quizzes', methods=['POST'])
    def new_question():
        try:
            body = request.get_json()
            previous_questions = body.get('previous_questions')
            quiz_category = body.get('quiz_category')

            # Id of zero means the user chose all in categories.
            if(quiz_category['id'] == 0):
                questionslist = Question.query.all()
            else: # Else we get all questions sharing the same category id as passed in
                questionslist = Question.query.filter(Question.category == quiz_category['id']).all()

            
            # We get a next question from the questionlist.
            next_question = random.choice(questionslist).format()

            # If the new question has already been chosen before, then we continue to request for a new one
            # until we have gone through all the questions in questionslist.
            while next_question['id'] in previous_questions:
                next_question = random.choice(questionslist).format()

                # If we have been through all questions then we can finish, and decide if we want to play again or not.
                if len(previous_questions) == len(questionslist):
                    return jsonify({
                        'success': True,
                        'message': 'done'
                    })
                
            return ({
                'success':True,
                'question': next_question
            })
        except:
            abort(400)

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
        'success': False,
        'error': 400,
        'message': 'Bad request'
        }), 400
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
        'success': False,
        'error': 404,
        'message': 'Not found.'
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
        'success': False,
        'error': 422, 
        'message': 'Syntax error.'
        }), 422
    
    @app.errorhandler(500)
    def internal_server(error):
        return jsonify({
        'success': False,
        'error': 500, 
        'message': 'Backedn error!.'
        }), 500

    return app

