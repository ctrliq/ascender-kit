from ascenderkit.api.resources import resources
from . import base
from . import page


class Metrics(base.Base):
    # This endpoint content-negotiates and will answer with CSV unless JSON is
    # asked for explicitly.
    get_headers = {'Accept': 'application/json'}


page.register_page([resources.metrics, (resources.metrics, 'get')], Metrics)
