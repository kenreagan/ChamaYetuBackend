from flask import Flask
from flask_smorest import Api
from MpesaRest import Mpesa


api = Api()

mpesa = Mpesa(
	'x6GCRysuUJKUzyLZ2Ylujlb4fEbt882r',
	'QErq8SPCFBxwCDzK',
	174379,
	'254794784462',
	'0b2b4d8482fddaf34d7ea78b402c2b40ed0db4b101007b46a89d0b9cd12b3fb2',
	'https://taskwithmeke/users/payment/callback/'
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


	from src.users import users_router

	from src.Chama import chama_router


	api.register_blueprint(users_router, url_prefix='/users')

	api.register_blueprint(chama_router, url_prefix='/chama')

	return app
