"""The service index, which lists what this deployment shares with other services.

A resource here is addressed by its ansible id, a UUID, and a resource type by
its name, so neither detail path takes the integer id the rest of the API uses.
"""

from ascenderkit.api.resources import resources
from . import base
from . import page


class ServiceIndexResource(base.Base):
    pass


page.register_page(resources.service_index_resource, ServiceIndexResource)


class ServiceIndexResources(page.PageList, ServiceIndexResource):
    pass


page.register_page(resources.service_index_resources, ServiceIndexResources)


class ServiceIndexResourceType(base.Base):
    pass


page.register_page(resources.service_index_resource_type, ServiceIndexResourceType)


class ServiceIndexResourceTypes(page.PageList, ServiceIndexResourceType):
    pass


page.register_page(resources.service_index_resource_types, ServiceIndexResourceTypes)
