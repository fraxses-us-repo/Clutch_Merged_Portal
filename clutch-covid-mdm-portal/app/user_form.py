from flask_appbuilder.fieldwidgets import BS3TextFieldWidget, DatePickerWidget
from flask_appbuilder.forms import DynamicForm
from flask_babel import lazy_gettext
from wtforms import StringField, DateField
from wtforms.validators import DataRequired

class UserInfoEdit(DynamicForm):
    first_name = StringField(
        lazy_gettext("First Name"),
        validators=[DataRequired()],
        widget=BS3TextFieldWidget(),
        description=lazy_gettext("Write the user first name or names"),
                            )
    
    last_name = StringField(
        lazy_gettext("Last Name"),
        validators=[DataRequired()],
        widget=BS3TextFieldWidget(),
        description=lazy_gettext("Write the user last name"),
                            )

    date_of_birth = DateField(
        lazy_gettext("Date of Birth"),
        validators=[DataRequired()],
        widget=DatePickerWidget(),
        description=lazy_gettext("Date of Birth"),
                            )
    employer_code = StringField(
        lazy_gettext("Employer Code"),
        validators=[DataRequired()],
        widget=BS3TextFieldWidget(),
        description=lazy_gettext("Your employer code"),
                            )
    employee_number = StringField(
        lazy_gettext("Employee Number"),
        validators=[DataRequired()],
        widget=BS3TextFieldWidget(),
        description=lazy_gettext("Your employee number"),
                            )

