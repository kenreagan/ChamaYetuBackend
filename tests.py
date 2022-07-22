import unittest
from flask import current_app
from src.contextmanager import DatabaseContextManager
from src.models import Base, User
from src import create_app
import os
from sqlalchemy import create_engine


class TestChamaApp(unittest.TestCase):
	def setUp(self) -> None:
		self.app = create_app(config_class='config.TestingConfig')
		self.app.context = self.app.app_context()
		Base.metadata.create_all(
			create_engine(
				'sqlite:///test.sqlite'
			)
		)
		self.app.context.push()
		self.client = self.app.test_client(use_cookies=True)

	def tearDown(self) -> None:
		self.app.context.pop()
		Base.metadata.drop_all(
			create_engine(
				'sqlite:///test.sqlite'
			)
		)
		os.unlink(os.path.join(os.getcwd(), 'test.sqlite'))

	def testAppCreation(self):
		self.assertIsNotNone(self.app)
	
	def testAppenvironment(self):
		self.assertIn('test.sqlite', os.listdir(os.getcwd()))
		self.assertEqual(current_app.config['ENV'], 'testing')

	def testUserEndpoints(self):
		response = self.client.get('/users/')
		self.assertEqual(response.status_code, 200)

		client_data = {
			'first_name': "test",
			'last_name': "tester",
			'middle_name': "master",
			'phone': 254794784462,
			'email': 'test@gmail.com',
			'password': 'test@gmail.com',
			'id_number': 38448952,
			'date_of_birth': '2001-03-21',
			'gender': "male",
			'marital_status': 'single',
			'education_level': 'graduate',
		}

		req = self.client.post('/users/', data=client_data)
		self.assertEquals(response.status_code, 201)

		userid = req.json()['uuid']

		res = self.client.get(f'/get/details/{userid}')
		self.assertIsNotNone(res.json())
		self.assertIsInstance(res.json(), dict)
		
		# test login
		log: Response = self.client.post('/users/login', data={
			'email': 'test@gmail.com',
			'password': 'test@gmail.com'
		})

		self.assertEqual(req.status_code, 200)
		self.assertIsInstance(req.json(), dict)
		self.assertIn('auth', req.json())
		
		token: str = req.json()['auth']
		self.assertNotEqual(token, None)

		step_two = self.client.post(
			'/users/add/employmentinfo',
			authentication = 'Bearer %s'%token,
			data = {
				'employment': 'unemployed',
				'monthly_income': 'less than 5000',
				'salary_per_day':10
			}
		)

		self.assertEqual(step_two.status_code, 201)
		
		step_three = self.client.post(
			'/users/add/guarantors',
			authentication = 'Bearer %s'%token,
			data = {
				'relationship': 'mother',
				'phone': 254710850362,
				'email': 'testparent@gmail.com',
				'name': 'testparent'
			}
		)
	
		self.assertEqual(step_three.status_code, 201)

		step_four = self.client.post(
			'/users/add/guarantors',
			authentication = 'Bearer %s'%token,
			data = {
				'contribution_frequency': 3000
			}
		)
		self.assertEqual(step_four.status_code, 201)
	
		with DatabaseContextManager() as context:
			user = context.session.query(
				User
			).filter(
				User.uuid == userid
			).first()
		
		self.assertIsNotNone(user)
		self.assertEqual(user.first_name, 'test')
		self.assertIsNone(user.chama_id)

		add_user_chama = self.client.post(
			'/users/add/chama',
			data = {
				'userid': userid
			}
		)

		self.assertEqual(add_user_chama.status_code, 201)

		self.assertIsInstance(add_user_chama.json(), dict)

	def testChamaEndpoints(self):
		resp = self.client.get('/chama/')
		self.assertEqual(resp.status_code, 200)
		self.assertIn('chama', resp.json())
	
	def testPaymentService(self):
		pass

	def testUtilsFunctionality(self):
		pass


if __name__ == '__main__':
	unittest.main()
