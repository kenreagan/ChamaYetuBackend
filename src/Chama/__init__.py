from flask_smorest import Blueprint
from flask.views import MethodView


chama_router = Blueprint('chama endpoints', __name__)

@chama_router.route('/')
class ChamaRoutes(MethodView):
    def get(self):
        # only accessible to super user and  the chama members.
        pass
    
    def post(self):
        # Add conditions for create=ing chama
        pass
    
    def update(self):
        # Update chama member
        pass
    
    def delete(self):
        pass
    
