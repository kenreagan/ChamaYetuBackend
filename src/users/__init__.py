from flask_smorest import Blueprint
from flask.views import MethodView
from src.schema import UserCreateSchema, EmploymentInfoSchema, GuarantorsSchema, ContributionFrequencySchema
import uuid
import threading

users_router = Blueprint('users', __name__)


@users_router.route('/')
class UserManager(MethodView):
	def get(self):
		return

	# step one
	@users_router.arguments(schema=UserCreateSchema)
	@users_router.response(schema=UserCreateSchema, status_code=201)
	def post(self, payload):
		pass

	def put(self):
		pass

	def update(self):
		pass


# Step two -> Employment Status
@users_router.route('/add/employmentinfo')
@users_router.arguments(schema=EmploymentInfoSchema)
def add_employment_info():
	return


# Step three -> guarantors
@users_router.route('/add/guarantors', methods=['POST'])
@users_router.arguments(schema=GuarantorsSchema)
def add_guarantors():
	return 


# Step 4 -> Contribution Frequency
@users_router.route('/add/contribution/frequency', methods=['POST'])
@users_router.arguments(schema=ContributionFrequencySchema)
def add_contribution_frequency():
	return

# add admin priviledges to add members to groups
@users_router.route('/join/chama', methods=['POST'])
def join_chama():
	return {
		'': ''
	}

# Add profile picture
@users_router.route('/add/profile', methods=['POST'])

# Add mpesarest configurations
@users_router.route('/pay/chama', methods=['POST'])
def pay_chama():
	return {

	}