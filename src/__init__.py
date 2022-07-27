from flask import Flask
from flask_smorest import Api
from MpesaRest import Mpesa
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os

api = Api()

admin = Admin(name="ChamaYettu", template_mode='bootstrap3')

mpesa = Mpesa(
    consumer_key= os.environ.get('CONSUMER_KEY'),
    consumer_secret=os.environ.get('CONSUMER_SECRET'),
    business_code=os.environ.get('BUSINESS_CODE'),
    passcode= os.environ.get('PASSCODE'),
    call_back=os.environ.get('CALL_BACK_URL'),
    environment=os.environ.get('MPESA_ENVIRONMENT'),
    phone_number=os.environ.get('CUSTOMER_PHONE'),
    BusinessShortCode=os.environ.get('SHORT_CODE'),
    Accountreference=os.environ.get('MYCOMPANY')
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
