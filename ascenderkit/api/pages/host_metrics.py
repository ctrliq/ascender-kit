from ascenderkit.api.resources import resources
from . import base
from . import page


class HostMetric(base.Base):
    # This endpoint content-negotiates and will answer with CSV unless JSON is
    # asked for explicitly.
    get_headers = {'Accept': 'application/json'}


class HostMetrics(page.PageList, HostMetric):
    pass


page.register_page([resources.host_metric], HostMetric)

page.register_page([resources.host_metrics], HostMetrics)
