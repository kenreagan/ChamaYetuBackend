from flask import Flask
from flask_smorest import Api


api = Api()


def create_app(config_class='config.Config') -> Flask:
	app = Flask(__name__)

	app.config.from_object(config_class)

	api.init_app(app)


	from src.users import users_router


	api.register_blueprint(users_router, url_prefix='/users')
	return app