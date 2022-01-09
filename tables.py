# import things
from flask_table import Table, Col, DatetimeCol, LinkCol, BoolNaCol, OptCol

from Model import LeaseStateEnum_choices_dict, int_to_ipv4

class IPv4Col(Col):
    def td_format(self, content):
        return int_to_ipv4(content)

class BinaryCol(Col):
    def td_format(self, content):
        #return binascii.b2a_hex(content)
        if isinstance(content, str):
            return content
        else:
            return content.hex()

# Declare your table
class Lease4Table(Table):
    border = 1
    address = IPv4Col('address')
    hwaddr = BinaryCol('hwaddr')
    client_id = BinaryCol('client_id')
    valid_lifetime = Col('valid_lifetime')
    expire = DatetimeCol('expire')
    subnet_id = Col('subnet_id')
    fqdn_fwd = BoolNaCol('fqdn_fwd')
    fqdn_rev = BoolNaCol('fqdn_rev')
    hostname = Col('hostname')
    state = OptCol('state', choices=LeaseStateEnum_choices_dict)

    edit = LinkCol('Edit', 'lease4_edit', url_kwargs=dict(address='address'), anchor_attrs={'class': 'lease4'})
