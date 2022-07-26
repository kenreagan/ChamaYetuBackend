from flask import Flask
from flask_smorest import Api
from MpesaRest import Mpesa
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

api = Api()

admin = Admin(name="ChamaYettu", template_mode='bootstrap3')

mpesa = Mpesa(
	'x6GCRysuUJKUzyLZ2Ylujlb4fEbt882r',
	'QErq8SPCFBxwCDzK',
	174379,
	'254794784462',
	'0b2b4d8482fddaf34d7ea78b402c2b40ed0db4b101007b46a89d0b9cd12b3fb2',
	'https://8b1f-41-81-82-230.in.ngrok.io/users/payment/callback/'
)

def create_app(config_class='config.Config') -> Flask:
	app = Flask(__name__)

	app.config.from_object(config_class)
	
	app.config['API_SPEC_OPTIONS'] = {
        'security': [
            {
                "bearerAuth": [

                ]
            }
        ],
        'components': dict(securitySchemes={
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            }
        })
    }

	api.init_app(app)

	admin.init_app(app)


	session = sessionmaker(bind=create_engine('sqlite:///main.sqlite', connect_args=dict(check_same_thread=False)))

	from src.users import users_router

	from src.Chama import chama_router

	# import db models
	from src.models import User, Transaction, Chama
	admin.add_view(ModelView(User, session()))
	admin.add_view(ModelView(Transaction, session()))
	admin.add_view(ModelView(Chama, session()))
	api.register_blueprint(users_router, url_prefix='/users')

	api.register_blueprint(chama_router, url_prefix='/chama')

	return app
