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
	UserDisplaySchema
)
import uuid
import threading
from src.models import User, Guarantors
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import insert, update
from src.utils import verify_authentication_headers

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
@users_router.response(schema=UserDisplaySchema, status_code=200)
def get_details(userid):
	with DatabaseContextManager() as context:
		user = context.session.query(User).filter_by(uuid=userid).first()
	return user.to_json()


# Step two -> Employment Status
@users_router.route('/add/employmentinfo', methods=['POST'])
@users_router.arguments(schema=EmploymentInfoSchema)
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
	return payload


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
		user = context.session.query(User).first()
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
	return

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
def pay_chama():
	return {

	}