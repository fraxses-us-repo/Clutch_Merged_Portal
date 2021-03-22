import logging
from flask import request, flash, Markup, url_for
from flask_appbuilder.security.registerviews import BaseRegisterUser
from flask_appbuilder.views import expose
from flask_appbuilder.security.forms import RegisterUserDBForm
import json
from flask_appbuilder.fields import AJAXSelectField
from flask_appbuilder.fieldwidgets import BS3TextFieldWidget, DatePickerWidget, Select2AJAXWidget, Select2SlaveAJAXWidget
from flask_appbuilder.forms import DynamicForm
from flask_babel import lazy_gettext
from wtforms import DateField, StringField, SelectField, RadioField
from flask_wtf.recaptcha import RecaptchaField
from wtforms.validators import DataRequired, Length
from wtforms import ValidationError
from flask_appbuilder._compat import as_unicode
from flask_appbuilder.security.decorators import has_access
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from .models import State, Country, City, Sex, HipaaAuthorization, GeneralInformedConsent
from sqlalchemy.orm import sessionmaker
import psycopg2
from sqlalchemy import create_engine
import codecs
from flask_appbuilder.models.sqla.interface import SQLAInterface
from config import SQLALCHEMY_DATABASE_URI

general_informed_consent_modal=codecs.open("app/templates/general_consent_modal.html", 'r')
hipaa_authorization_modal=codecs.open("app/templates/hipaa_authorization_modal.html", 'r')

log = logging.getLogger(__name__)

class CustomRegisterUserDBForm(RegisterUserDBForm):
   
    def states():
        engine = create_engine(SQLALCHEMY_DATABASE_URI)
        Session = sessionmaker(bind=engine)
        session = Session() 
        return session.query(State).all()
    
    def countries():
        engine = create_engine(SQLALCHEMY_DATABASE_URI)
        Session = sessionmaker(bind=engine)
        session = Session() 
        return session.query(Country).all()
    
    def cities():
        engine = create_engine(SQLALCHEMY_DATABASE_URI)
        Session = sessionmaker(bind=engine)
        session = Session()
        return session.query(City).all()

    def gender():
        engine = create_engine(SQLALCHEMY_DATABASE_URI)
        Session = sessionmaker(bind=engine)
        session = Session()
        return session.query(Gender).all()
    
    def general_informed_consent_options():
        engine = create_engine(SQLALCHEMY_DATABASE_URI)
        Session = sessionmaker(bind=engine)
        session = Session()
        return session.query(GeneralInformedConsent).all()

    def hipaa_authorization_options():
        engine = create_engine(SQLALCHEMY_DATABASE_URI)
        Session = sessionmaker(bind=engine)
        session = Session()
        return session.query(HipaaAuthorization).all()
        


    date_of_birth = DateField(
        lazy_gettext("Date of Birth"),
        validators=[DataRequired()],
        widget=DatePickerWidget(),
        description=lazy_gettext("yyyy-mm-dd")
        )

    gender = QuerySelectField( 
        lazy_gettext('Gender'),
        validators=[DataRequired()],
        query_factory=gender
        )
    
    street_address = StringField(
        lazy_gettext("Street Address"),
        validators=[DataRequired()],
        widget=BS3TextFieldWidget(),
        #description=lazy_gettext("Street Address"),
        )

    street_address_line_2 = StringField(
        lazy_gettext("Street Address Line 2"),
        widget=BS3TextFieldWidget(),
        #description=lazy_gettext("Street Address Line 2"),
        )

    suite_apt_number = StringField(
        lazy_gettext("Suite Apt. Number"),
        widget=BS3TextFieldWidget()
        )
    
    #state = AJAXSelectField('state',
    #    description='State',
    #    datamodel=SQLAInterface(State),
    #    col_name='State', 
    #    widget=Select2AJAXWidget(endpoint='/state/api/column/add/state')
    #    )

    #city = AJAXSelectField('city',
    #    description='City',
    #    datamodel=SQLAInterface(City),
    #    col_name='City',
    #    widget=Select2SlaveAJAXWidget(master_id='state', endpoint='/city/api/column/add/city?_flt_0_state_id={{ID}}')
    #    )
    
    city = StringField(
        lazy_gettext("City"),
        validators=[DataRequired()],
        widget=BS3TextFieldWidget(),
        #description=lazy_gettext("City"),
        )
        
    state = QuerySelectField(
        u"State / Province",
        validators=[DataRequired()],
        query_factory=states,
        )

    zip_code = StringField(
        lazy_gettext("Zip Code"),
        validators=[DataRequired(), Length(min=5, max=11)],
        widget=BS3TextFieldWidget(),
        #description=lazy_gettext("Zip Code"),
        )

    country = QuerySelectField(
        u"Country",
        validators=[DataRequired()],
        query_factory=countries  
        )

    phone_number = StringField(
        validators=[DataRequired(),
        Length(min=6, max=40)]
        )

    general_informed_consent = QuerySelectField(
        Markup("General Informed Consent " + general_informed_consent_modal.read()),
        validators=[DataRequired()],
        query_factory=general_informed_consent_options
            )

    hipaa_authorization = QuerySelectField(
        Markup("Hipaa Authorization " + hipaa_authorization_modal.read()),
        validators=[DataRequired()],
        query_factory=hipaa_authorization_options,
            )

    employer_code = StringField(
        u"Employer Code",
        widget=BS3TextFieldWidget(),
        description=lazy_gettext("Your employer code if provided. You can always add or revoke this from your profile page at any time.")
            )

    recaptcha = 1# RecaptchaField()

    def validate_phone(form, field):
        if len(field.data) > 16:
            raise ValidationError('Invalid phone number.')
        try:
            input_number = phonenumbers.parse(field.data)
            if not (phonenumbers.is_valid_number(input_number)):
                raise ValidationError('Invalid phone number.')
        except:
            input_number = phonenumbers.parse("+1"+field.data)
            if not (phonenumbers.is_valid_number(input_number)):
                raise ValidationError('Invalid phone number.')

class CustomRegisterUserDBView(BaseRegisterUser):
    form = CustomRegisterUserDBForm
    email_template = 'register_mail.html'

    def send_email(self, register_user):
        """
            Method for sending the registration Email to the user
        """
        try:
            from flask_mail import Mail, Message
        except Exception:
            log.error("Install Flask-Mail to use User registration")
            return False
        mail = Mail(self.appbuilder.get_app)
        msg = Message()
        msg.subject = self.email_subject
        url = url_for(
            ".activation",
            _external=True,
            activation_hash=register_user.registration_hash,
        )
        msg.html = self.render_template(
            self.email_template,
            url=url.replace('http://10.10.0.230:49002','https://diagnostics.clutch.health'),
            username=register_user.username,
            first_name=register_user.first_name,
            last_name=register_user.last_name,
        )
        msg.recipients = [register_user.email]
        try:
            mail.send(msg)
        except Exception as e:
            log.error("Send email exception: {0}".format(str(e)))
            return False
        return True

    def add_registration(self, username, first_name, last_name, email, gender, street_address, street_address_line_2, suite_apt_number, city, state, country, phone_number, date_of_birth, general_informed_consent, hipaa_authorization, employer_code, password=""):
        
        
        register_user = self.appbuilder.sm.add_register_user(
                username, first_name, last_name, email, gender, street_address, street_address_line_2, suite_apt_number, city, state, country, phone_number, date_of_birth, general_informed_consent, hipaa_authorization, employer_code, password
                                )

        if register_user:
            if self.send_email(register_user):
                flash(as_unicode(self.message), "info")
                return register_user
            else:
                flash(as_unicode(self.error_message), "danger")
                self.appbuilder.sm.del_register_user(register_user)
                return None
                                                                                                                                                                        
    def form_get(self, form):
        self.add_form_unique_validations(form)
    
    def form_post(self, form):
        print(form.state.data)
        engine = create_engine(SQLALCHEMY_DATABASE_URI)
        Session = sessionmaker(bind=engine)
        session = Session() 
        
        gender = session.query(Gender).filter(Gender.gender_description == str(form.gender.data)).first()
        general_informed_consent = session.query(GeneralInformedConsent).filter(GeneralInformedConsent.general_informed_consent == str(form.general_informed_consent.data)).first()
        hipaa_authorization = session.query(HipaaAuthorization).filter(HipaaAuthorization.hipaa_authorization == str(form.hipaa_authorization.data)).first()
        state = session.query(State).filter(State.state == str(form.state.data)).first()
        country = session.query(Country).filter(Country.country == str(form.country.data)).first()

        self.add_form_unique_validations(form)
        self.add_registration(
            username=form.username.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            date_of_birth=form.date_of_birth.data,
            email=form.email.data,
            password=form.password.data,
            gender=gender.id,
            street_address=form.street_address.data,
            street_address_line_2=form.street_address_line_2.data,
            suite_apt_number=form.suite_apt_number.data,
            city=form.city.data,
            state=state.id,
            country=country.id,
            phone_number=form.phone_number.data,
            general_informed_consent=general_informed_consent.id,
            hipaa_authorization=hipaa_authorization.id,
            employer_code=form.employer_code.data
        )


class ClutchRegisterUserDBForm(CustomRegisterUserDBForm):
    form_title = lazy_gettext("Clutch Diagnostics Lab Test Registration")

class ClutchRegisterUserDBView(CustomRegisterUserDBView):
    route_base = "/clutch-register"
    form_title = lazy_gettext('Clutch Diagnostics Lab Test Registration')
    #form_template = 'custom_form.html'
    form_template = 'custom_register_user.html'
    #form_template = 'multi_step_form.html'
    form = ClutchRegisterUserDBForm

    @expose("/form", methods=["GET"])
    def this_form_get(self):
        self._init_vars()
        form = self.form.refresh()

        self.form_get(form)
        widgets = self._get_edit_widget(form=form)
        self.update_redirect()
        return self.render_template(
                    self.form_template,
                    title=self.form_title,
                    form=form,
                    widgets=widgets,
                    appbuilder=self.appbuilder,
            )

    @expose("/form", methods=["POST"])
    def this_form_post(self):
        print(request.form)
        self._init_vars()
        form = self.form.refresh()
        if form.validate_on_submit():
            response = self.form_post(form)
            if not response:
                return redirect(self.get_redirect())
            return response
        else:
            widgets = self._get_edit_widget(form=form)
            return self.render_template(
                        self.form_template,
                        title=self.form_title,
                        form=form,
                        widgets=widgets,
                        appbuilder=self.appbuilder,
                )
