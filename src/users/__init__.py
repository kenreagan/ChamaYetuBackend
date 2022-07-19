from flask_smorest import Blueprint
from flask.views import MethodView


users_router = Blueprint('users', __name__)


@users_router.route('/')
class UserManager(MethodView):
	def get(self):
		pass

	def post(self):
		pass

	def put(self):
		pass

	def update(self):
		pass


@users_router.route('/join/chama', methods=['POST'])
def join_chama():
	return {
		'': ''
	}