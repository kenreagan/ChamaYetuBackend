from flask_smorest import Blueprint
from flask.views import MethodView
from src.contextmanager import DatabaseContextManager
from src.schema import (
	UserCreateSchema,
	EmploymentInfoSchema,
	GuarantorsSchema,
	ContributionFrequencySchema,
	UserListDisplay,
	LoginSchema,
	UserDisplaySchema,
	PersonalInfoSchema
)
import uuid
import threading
from src.models import User, Guarantors
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import (
	insert,
	update,
	select
)
from src.utils import verify_authentication_headers
from src import mpesa

users_router = Blueprint('users', __name__)


@users_router.route('/')
class UserManager(MethodView):
	@users_router.response(schema=UserListDisplay, status_code=200)
	def get(self):
		with DatabaseContextManager() as context:
			users = context.session.query(User).all()
		return {
			'subscribers': [
					client.to_json() for client in users
			]
		} 

	# step one
	@users_router.arguments(schema=UserCreateSchema)
	@users_router.response(schema=UserCreateSchema, status_code=201)
	def post(self, payload):
		payload['password'] = generate_password_hash(payload['password'])
		payload['uuid'] = uuid.uuid4().hex
		with DatabaseContextManager() as context:
			statement = insert(
				User
			).values(
				**payload
			)
			context.session.execute(statement)
			context.session.commit()
		return payload

	def put(self, payload):
		pass

	def update(self, payload):
		pass

	def delete(self, payload):
		pass


@users_router.route('/get/details/<userid>')
@users_router.response(schema=PersonalInfoSchema, status_code=200)
def get_details(userid):
	with DatabaseContextManager() as context:
		user = context.session.query(
				User
			).filter(
				User.uuid==userid
			).first()
		guarantors = context.session.query(
			Guarantors
		).filter(
			Guarantors.user_id == userid
		).all()
	payload = user.to_json()
	payload['guarantors'] = []
	for results in guarantors:
		payload['guarantors'].append(results.to_json())
	return payload


# Step two -> Employment Status
@users_router.route('/add/employmentinfo', methods=['POST'])
@users_router.arguments(schema=EmploymentInfoSchema)
@users_router.response(schema=UserDisplaySchema, status_code=201)
@verify_authentication_headers
def add_employment_info(current_user, payload):
	statement = update(User).values(
		payload
	).where(
		User.uuid == current_user.uuid
	)
	with DatabaseContextManager() as context:
		context.session.execute(statement)
		context.session.commit()
	return current_user.to_json()


# Step three -> guarantors
@users_router.route('/add/guarantors', methods=['POST'])
@users_router.arguments(schema=GuarantorsSchema)
@verify_authentication_headers
def add_guarantors(current_user, payload):
	payload['user_id'] = current_user.uuid
	statement = insert(Guarantors).values(
		**payload
	)
	print(statement)
	with DatabaseContextManager() as context:
		context.session.execute(statement)
		context.session.commit()
	return payload


# Login endpoint
@users_router.route('/login', methods=['POST'])
@users_router.arguments(schema=LoginSchema)
def login(payload):
	with DatabaseContextManager() as context:
		user = context.session.query(User).filter(
			User.email==payload['email']
		).first()
		if user:
			if check_password_hash(user.password, payload['password']):
				return {
					"auth": user.generate_token(user.uuid)
				}
			return {
				"Error": "Wrong password"
			}
		return {
			"Error": "user does not exist"
		}

# Step 4 -> Contribution Frequency
@users_router.route('/add/contribution/frequency', methods=['POST'])
@users_router.arguments(schema=ContributionFrequencySchema)
@users_router.response(schema=UserDisplaySchema, status_code=201)
@verify_authentication_headers
def add_contribution_frequency(current_user, payload):
	statement = update(User).values(
		**payload
	).where(
		User.uuid == current_user.uuid
	)
	with DatabaseContextManager() as context:
		context.session.execute(statement)
		context.session.commit()			
	return current_user.to_json()

# add admin priviledges to add members to groups
@users_router.route('/join/chama', methods=['POST'])
@verify_authentication_headers
def join_chama():
	return {
		'': ''
	}

# Add profile picture
@users_router.route('/add/profile', methods=['POST'])
@verify_authentication_headers
def add_profile():
	pass


# Add mpesarest configurations
@users_router.route('/pay/chama', methods=['POST'])
@verify_authentication_headers
def pay_chama(current_user):
	if current_user.contribution_frequency:
		# mpesarest configuration
		res =mpesa.prompt_payment_for_service(
			{
				'phone': str(current_user.phone),
				'amount': current_user.contribution_frequency,
				'description': 'Payment for chama'
			}
		)
		return res
	return {

	}

@users_router.route('/payment/callback', methods=['POST', 'GET'])
def callback_url(payload):
	return