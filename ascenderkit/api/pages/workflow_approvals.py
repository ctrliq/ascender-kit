from ascenderkit.api.pages import UnifiedJob
from ascenderkit.api.resources import resources
from . import base
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


page.register_page([resources.workflow_approvals, resources.workflow_approval_template_approvals], WorkflowApprovals)


class WorkflowApprovalVote(base.Base):
    pass


page.register_page(resources.workflow_approval_vote, WorkflowApprovalVote)


class WorkflowApprovalVotes(page.PageList, WorkflowApprovalVote):
    pass


page.register_page([resources.workflow_approval_votes, resources.workflow_approval_related_votes], WorkflowApprovalVotes)
