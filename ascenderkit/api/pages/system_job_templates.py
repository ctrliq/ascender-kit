from ascenderkit.api.mixins import HasNotifications
from ascenderkit.api.pages import UnifiedJobTemplate
from ascenderkit.api.resources import resources
from . import page


class SystemJobTemplate(UnifiedJobTemplate, HasNotifications):
    NATURAL_KEY = ('name', 'organization')

    def launch(self, payload=None):
        """Launch the system_job_template using related->launch endpoint."""
        payload = {} if payload is None else payload
        result = self.related.launch.post(payload)

        # return job
        jobs_pg = self.get_related('jobs', id=result.json['system_job'])
        assert jobs_pg.count == 1, f"system_job_template launched (id:{result.json['system_job']}) but unable to find matching job at {self.url}/jobs/"
        return jobs_pg.results[0]


page.register_page(resources.system_job_template, SystemJobTemplate)


class SystemJobTemplates(page.PageList, SystemJobTemplate):
    pass


page.register_page(resources.system_job_templates, SystemJobTemplates)
