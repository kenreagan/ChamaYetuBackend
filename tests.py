import unittest
from flask import current_app
# from src.contextmanager import DatabaseContextManager
from src.models import Base
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

	def tearDown(self) ->None:
		self.app.context.pop()
		os.unlink(os.path.join(os.getcwd(), 'test.sqlite'))

	def testAppCreation(self):
		self.assertIsNotNone(self.app)
	
	def testAppenvironment(self):
		self.assertIn('test.sqlite', os.listdir(os.getcwd()))
		self.assertEqual(current_app.config['ENV'], 'testing')

	def testFunctionalityofApp(self):
		pass


if __name__ == '__main__':
	unittest.main()
