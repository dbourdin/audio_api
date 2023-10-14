# Import all the models, so that Base has them before being
# imported by Alembic
# flake8: noqa

from audio_api.persistence.models.base_model import SqlAlchemyModel
from audio_api.persistence.models import RadioProgram
