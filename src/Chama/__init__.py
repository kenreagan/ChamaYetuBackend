from flask_smorest import Blueprint
from flask.views import MethodView
from src.contextmanager import DatabaseContextManager
from src.models import Chama
import uuid
from src.schema import (
    ChamaSchema,
    ChamaDisplaySchema,
    ChamaCreateSchema
)

chama_router = Blueprint('chama endpoints', __name__)

@chama_router.route('/')
class ChamaRoutes(MethodView):
    @chama_router.response(schema=ChamaDisplaySchema, status_code=200)
    def get(self):
        with DatabaseContextManager() as context:
            chama = context.session.query(Chama).filter_by().all()

        return {
            "chama": [
                chamas.to_json() for chamas in chama
            ]
        }

    @chama_router.arguments(schema=ChamaCreateSchema)
    @chama_router.response(schema=ChamaCreateSchema, status_code=200)
    def post(self, payload):
        payload['chama_name'] = uudi.uuid4().hex
        with DatabaseContextManager() as context:
            statement = insert(
                Chama
            ).values(
                **payload
            )

            context.session.execute(statement)
            context.session.commit()
        return payload
    
    def update(self, payload):
        # Update chama member
        with DatabaseContextManager() as context:
            statement = update(
                Chama
            ).values(
                **payload
            ).where(
                Chama.chama_id == payload['chama_id']
            )

            context.session.execute(statement)
            context.session.commit()
        return payload
    
    def delete(self, payload):
        with DatabaseContextManager() as context:
            statement = delete(
                Chama
            ).where(
                Chama.chama_id == payload['chama_id']
            )

            context.session.execute(statement)
            context.session.commit()
    
