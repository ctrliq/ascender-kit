from ascenderkit.api.resources import resources
from . import base
from . import page


class ReceptorAddress(base.Base):
    pass


page.register_page(resources.receptor_address, ReceptorAddress)


class ReceptorAddresses(page.PageList, ReceptorAddress):
    pass


page.register_page([resources.receptor_addresses, resources.instance_receptor_addresses], ReceptorAddresses)
