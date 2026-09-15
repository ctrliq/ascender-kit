from ascenderkit.api.resources import resources
from . import base
from . import page


class Config(base.Base):
    pass


page.register_page(resources.config, Config)
