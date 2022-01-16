"""Form object declaration."""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import Field, StringField, SubmitField, TextAreaField, BooleanField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, NumberRange
from wtforms.widgets import TextInput

from Model import *

from wtforms_sqlalchemy.orm import model_form, ModelConverter, converts

class IPv4Field(Field):
    widget = TextInput()
    def process_formdata(self, valuelist):
        if valuelist:
            self.data = ipv4_to_int(valuelist[0])

    def _value(self):
        return int_to_ipv4(self.data) if self.data is not None else ""

class HWAddrField(Field):
    widget = TextInput()

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = hwaddr_to_bin(valuelist[0])

    def _value(self):
        return bin_to_hwaddr(self.data) if self.data is not None else ""

class BinaryHexField(Field):
    widget = TextInput()

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = bytes.fromhex(valuelist[0])

    def _value(self):
        return self.data.hex() if self.data is not None else ""

class MyModelConverter(ModelConverter):

    @converts("Boolean", "dialects.mssql.base.BIT")
    def conv_Boolean(self, field_args, **extra):
        field_args["validators"] = []
        ret = BooleanField(**field_args)
        return ret

    @converts("IntEnum")
    def conv_Enum(self, column, field_args, **extra):
        field_args["choices"] = [(int(e), e) for e in column.type._enumtype]
        return SelectField(**field_args)

    @converts("Integer")  # includes BigInteger and SmallInteger
    def handle_integer_types(self, column, field_args, **extra):
        unsigned = getattr(column.type, "unsigned", False)
        if unsigned:
            field_args["validators"].append(NumberRange(min=0))
        if column.name in ['address']:
            return IPv4Field(**field_args)
        else:
            return IntegerField(**field_args)

    @converts("Text", "LargeBinary", "Binary")  # includes UnicodeText
    def conv_Text(self, field_args, **extra):
        column = extra.get('column')
        if column is not None and column.name in ['hwaddr']:
            return HWAddrField(**field_args)
        elif column is not None and column.name in ['client_id']:
            return BinaryHexField(**field_args)
        else:
            return ModelConverter.conv_Text(self, field_args=field_args, **extra)


Lease4Form = model_form(model=Lease4, base_class=FlaskForm, converter=MyModelConverter(), exclude_pk=False)
Lease4Form.fqdn_fwd.validators = []
Lease4Form.fqdn_rev.validators = []

k = 0;

class LeaseUploadForm(FlaskForm):
    file = FileField(validators=[FileRequired()])
    file_type = SelectField(
        'Type',
        [DataRequired()],
        choices=LeaseFileTypeEnum_choices
    )



class LeaseForm():
    """Contact form."""
    address = StringField(
        'Address',
        [DataRequired()]
    )
    hwaddr = StringField(
        'Hardware Address',
        [
                        DataRequired()
        ]
    )
    client_id = StringField(
        'Client Id',
        [DataRequired()]
    )
    valid_lifetime = StringField(
        'Life time',
        [DataRequired()]
    )
    expire = StringField(
        'Expire',
        [DataRequired()]
    )
    subnet_id = IntegerField(
        'Subnet',
        [DataRequired()]
    )
    fqdn_fwd = BooleanField(
        'Forward',
        []
    )
    fqdn_rev = BooleanField(
        'Forward',
        []
    )
    hostname = StringField(
        'Host name',
        [DataRequired()]
    )
    state = SelectField(
        'State',
        [DataRequired()],
        choices=LeaseStateEnum_choices
    )
    user_context = TextAreaField(
        'User context',
        [DataRequired()]
    )
    submit = SubmitField('Submit')
