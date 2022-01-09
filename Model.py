from flask import Flask
from marshmallow import Schema, fields, pre_load, validate, ValidationError
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import enum
import socket
import struct

ma = Marshmallow()
db = SQLAlchemy()
class IntEnum(db.TypeDecorator):
    impl = db.Integer()
    def __init__(self, enumtype, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._enumtype = enumtype

    def process_bind_param(self, value, dialect):
        if isinstance(value, enum.Enum):
            return value
        elif isinstance(value, enum.IntEnum):
            return int(value)
        elif isinstance(value, int):
            return value
        elif isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                pass
        return value.value
    def process_result_value(self, value, dialect):
        return self._enumtype(value)

class LeaseStateEnum(enum.IntEnum):
    default = 0
    declined = 1
    expired_reclaimed = 2

LeaseStateEnum_choices = \
    [(LeaseStateEnum.default, 'default'), (LeaseStateEnum.declined, 'declined'), (LeaseStateEnum.expired_reclaimed, 'expired') ]    
LeaseStateEnum_choices_dict = \
    { LeaseStateEnum.default: 'default', LeaseStateEnum.declined:'declined', LeaseStateEnum.expired_reclaimed:'expired' }   

def int_to_ipv4(addr):
    try:
        return socket.inet_ntoa(struct.pack("!I", addr))
    except OSError:
        return None

def ipv4_to_int(addr):
    try:
        return struct.unpack("!I", socket.inet_aton(addr))[0]
    except OSError:
        return None

def bin_to_hwaddr(addr, sep=':'):
    if addr is None:
        return None
    return sep.join('%02x' % b for b in addr)

def hwaddr_to_bin(addr):
    a = addr.replace(':', '').replace('-', '')
    try:
        return bytes.fromhex(a)
    except:
        return None

class Host(db.Model):
    __tablename__ = 'hosts'
    host_id = db.Column(db.Integer, primary_key=True)
    dhcp_identifier = db.Column(db.LargeBinary(128), nullable=False)
    dhcp_identifier_type = db.Column(db.Integer, nullable=False)
    dhcp4_subnet_id = db.Column(db.Integer)
    dhcp6_subnet_id = db.Column(db.Integer)
    ipv4_address = db.Column(db.Integer)
    hostname = db.Column(db.String(255))

    def __init__(self, *args):
        super(Host, self).__init__(*args)

class Lease4(db.Model):
    __tablename__ = 'lease4'
    address = db.Column(db.Integer, primary_key=True)
    hwaddr = db.Column(db.LargeBinary(20), nullable=False)
    client_id = db.Column(db.LargeBinary(128), nullable=False)
    valid_lifetime = db.Column(db.Integer, default=3600)
    expire = db.Column(db.DateTime, server_default=func.now())
    subnet_id = db.Column(db.Integer, nullable=True)
    fqdn_fwd = db.Column(db.Boolean, nullable=False, default=False)
    fqdn_rev = db.Column(db.Boolean, nullable=False, default=False)
    hostname = db.Column(db.String(255), nullable=False, default='')
    state = db.Column(
        IntEnum(LeaseStateEnum), 
        default=LeaseStateEnum.default,
        nullable=False
    )    
    user_context = db.Column(db.Text, nullable=False)

    def __init__(self, *args):
        super(Lease4, self).__init__(*args)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), unique=True, nullable=False)
    details = db.relationship('Detailes', backref=db.backref('user', lazy=True))

    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name


class Detailes(db.Model):
    __tablename__ = 'details'
    id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.Integer, unique=True, nullable=False)
    address = db.Column(db.String(150), unique=True, nullable=False)
    country_origin = db.Column(db.String(150), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def __init__(self, age, address, country_origin):
        self.age = age
        self.address = address
        self.country_origin = country_origin


class UserSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    first_name = fields.String(required=True)
    last_name  = fields.String(required=True)


class DetailesSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    age = fields.Integer(required=True)
    address = fields.String(required=True)
    country_origin = fields.String(required=True)
    user_id = fields.Integer(required=False)
