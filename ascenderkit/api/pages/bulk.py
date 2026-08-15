from ascenderkit.api.resources import resources
from . import base
from . import page


class Bulk(base.Base):
    # This endpoint content-negotiates and will answer with CSV unless JSON is
    # asked for explicitly.
    get_headers = {'Accept': 'application/json'}


page.register_page([resources.bulk, (resources.bulk, 'get')], Bulk)


class BulkJobLaunch(base.Base):
    def post(self, payload={}):
        result = self.connection.post(self.endpoint, payload)
        if 'url' in result.json():
            return self.walk(result.json()['url'])
        else:
            return self.page_identity(result, request_json={})


page.register_page(resources.bulk_job_launch, BulkJobLaunch)
