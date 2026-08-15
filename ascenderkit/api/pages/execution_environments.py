import logging

from ascenderkit.api.mixins import DSAdapter, HasCreate, HasCopy
from ascenderkit.api.pages import (
    Credential,
    Organization,
)
from ascenderkit.api.resources import resources
from ascenderkit.utils import random_title, PseudoNamespace, filter_by_class

from . import base
from . import page

log = logging.getLogger(__name__)


class ExecutionEnvironment(HasCreate, HasCopy, base.Base):
    dependencies = [Organization, Credential]
    NATURAL_KEY = ('name',)

    # fields are name, image, organization, managed, credential
    def create(self, name='', image='ghcr.io/ctrliq/ascender-ee:latest', organization=Organization, credential=None, pull='', **kwargs):
        # we do not want to make a credential by default
        payload = self.create_payload(name=name, image=image, organization=organization, credential=credential, pull=pull, **kwargs)
        ret = self.update_identity(ExecutionEnvironments(self.connection).post(payload))
        return ret

    def create_payload(self, name='', organization=Organization, credential=None, **kwargs):
        self.create_and_update_dependencies(*filter_by_class((credential, Credential), (organization, Organization)))

        credential = self.ds.credential if credential else None
        organization = self.ds.organization if organization else None

        payload = self.payload(name=name, organization=organization, credential=credential, **kwargs)
        payload.ds = DSAdapter(self.__class__.__name__, self._dependency_store)
        return payload

    def payload(self, name='', image=None, organization=None, credential=None, pull='', **kwargs):
        payload = PseudoNamespace(
            name=name or "EE - {}".format(random_title()),
            image=image or "example.invalid/component:tagname",
            organization=organization.id if organization else None,
            credential=credential.id if credential else None,
            pull=pull,
            **kwargs
        )

        return payload


page.register_page(
    [resources.execution_environment, (resources.execution_environments, 'post'), (resources.organization_execution_environments, 'post')], ExecutionEnvironment
)


class ExecutionEnvironments(page.PageList, ExecutionEnvironment):
    pass


page.register_page([resources.execution_environments, resources.organization_execution_environments], ExecutionEnvironments)
