import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format(
            'localhost:5432', self.database_name)
        # setup_db(self.app, self.database_path)

        # # binds the app to the current context
        # with self.app.app_context():
        #     self.db = SQLAlchemy()
        #     self.db.init_app(self.app)
        #     # create all tables
        #     self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test
    for successful operation and for expected errors.
    """

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        categories = {}

        for category in Category.query.all():
            categories[f'{category.id}'] = category.type

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['categories'], categories)

    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_get_paginated_questions_error(self):
        res = self.client().get('/questions?page=10')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)

    def test_delete_question(self):
        # we first create a temp question:
        question = Question(
            question="Test question",
            answer="test answer",
            category=2,
            difficulty=2)
        question.insert()

        res = self.client().delete(f'/questions/{question.id}')
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)

    def test_delete_question_error(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)

    def test_search_question(self):
        res = self.client().post('/questions', json={'searchTerm': 'in'})
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['totalQuestions'])

    def test_search_question_error(self):
        res = self.client().post('/questions', json={'searchTerm': '.'})
        data = json.loads(res.data)

        self.assertEqual(data['success'], False)

    def test_create_question(self):
        new_question = {
            'question': 'Whats the my name?',
            'answer': 'Miguel',
            'category': '1',
            'difficulty': 4,
        }

        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)

    def test_create_question_error(self):
        new_question = {
            'question': 'Whats the oposite of black?',
            'category': '...',
            'answer': '',
            'difficulty': '.',
        }

        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)

        self.assertEqual(data['success'], False)

    def test_question_by_category(self):
        res = self.client().get('categories/4/questions')
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)

    def test_question_by_category_error(self):
        # No category exists with id 1000
        res = self.client().get('categories/10000/questions')
        data = json.loads(res.data)

        self.assertEqual(data['success'], False)

    def test_play_quiz(self):
        input_data = {
            'previous_questions': [20, 21],
            'quiz_category': {
                'id': 1,
                'type': 'Science'
            }
        }

        res = self.client().post('/quizzes', json=input_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

        self.assertNotEqual(data['question']['id'], 24)
        self.assertNotEqual(data['question']['id'], 0)

        self.assertEqual(data['question']['category'], 1)

    def test_play_quiz_error(self):
        input_data = {
            'previous_questions': ['.', '2', '^'],
            'quiz_category': {
                'id': '5k',
                'type': 'Science'
            }
        }

        res = self.client().post('/quizzes', json=input_data)
        data = json.loads(res.data)

        self.assertEqual(data['success'], False)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
