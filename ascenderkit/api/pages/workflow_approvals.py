from ascenderkit.api.pages import UnifiedJob
from ascenderkit.api.resources import resources
from . import page
from ascenderkit import exceptions


class WorkflowApproval(UnifiedJob):
    def approve(self):
        try:
            self.related.approve.post()
        except exceptions.NoContent:
            pass

    def deny(self):
        try:
            self.related.deny.post()
        except exceptions.NoContent:
            pass


page.register_page(resources.workflow_approval, WorkflowApproval)


class WorkflowApprovals(page.PageList, WorkflowApproval):
    pass


page.register_page(resources.workflow_approvals, WorkflowApprovals)
