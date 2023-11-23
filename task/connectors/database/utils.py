from task import config
from task.connectors.database.json import JsonFileDatabaseConnector
from task.connectors.database.sqlite import SqliteDatabaseConnector
from task.utils import Mode
from task.validators import validate_config_attr


@validate_config_attr(Mode)
def get_db_connector_class():
    if config.RUN_CONFIG['MODE'] == Mode.DEV.value:
        return JsonFileDatabaseConnector

    return SqliteDatabaseConnector
