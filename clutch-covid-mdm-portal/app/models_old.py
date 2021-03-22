from flask_appbuilder import Model
import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import Sequence, Column, Integer, String, ForeignKey, Date, Boolean, DateTime, Float, Text, Table, Date, UniqueConstraint
from sqlalchemy.orm import relationship
from flask_appbuilder.models.decorators import renders
from sqlalchemy.sql import func
from flask_appbuilder.models.mixins import AuditMixin
from flask import Markup
from flask_appbuilder.security.sqla.models import User
from sqlalchemy.ext.declarative import declared_attr
from flask_appbuilder.security.sqla.models import RegisterUser

def time_now():
    return datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

def generate_uuid():
    return str(uuid.uuid4())

def get_user_id(cls):
    try:
        return g.user.id
    except Exception:
        return None

mindate = datetime.date(datetime.MINYEAR, 1, 1)

class ShippingVendors(Model):
    __tablename__ = 'shipping_vendors'
    
    id = Column(Integer, primary_key=True)
    shipping_vendor = Column(String(256), unique=True)

    def __repr__(self):
        return self.shipping_vendor

class RequisitionManifest(Model):
    __tablename__ = 'requisition_manifest'

    id = Column(Integer, primary_key=True)
    requisition_number = Column(String(256), unique=True)
    tracking_number = Column(String(256))
    shipping_vendor_id = Column(Integer, ForeignKey("shipping_vendors.id"))
    shipping_vendor = relationship("ShippingVendors")

    def __repr__(self):
        return self.requisition_number

class CustomRegisterUser(RegisterUser):
    __tablename__ = "ab_register_user"
            
    id = Column(Integer, Sequence("ab_register_user_id_seq"), primary_key=True)
    first_name = Column(String(64), nullable=False)
    middle_name = Column(String(256))
    last_name = Column(String(64), nullable=False)
    username = Column(String(64), unique=True, nullable=False)
    password = Column(String(256))
    email = Column(String(64), nullable=False)
    registration_date = Column(DateTime, default=datetime.datetime.now, nullable=True)
    registration_hash = Column(String(256))
    date_of_birth = Column(String(256))
    gender = Column(String(256))
    street_address = Column(String(256))
    street_address_line_2 = Column(String(256))
    suite_apt_number = Column(String(256))
    city = Column(String(256))
    state = Column(String(256))
    country = Column(String(256))
    phone_number = Column(String(256))
    hipaa_authorization_id = Column(Integer)
    general_informed_consent_id = Column(Integer)

class LabCorpFile(Model):
    __tablename__ = 'labcorp_results_process_history_sftp_hl7'
    __table_args__ = (UniqueConstraint('file_name', 'message_number'),)
    
    id = Column(Integer, primary_key=True)
    file_name = Column(String(400))
    message_number = Column(Integer)
    updated_at = Column(DateTime(timezone=True), default=time_now(), onupdate=func.now())
    process_success = Column(Boolean)
    raw_hl7 = Column(Text)
    processed_hl7 = Column(Text)
    error = Column(Text)

    def __repr__(self):
        return self.file_name

class LabCorpFileDetail(Model, AuditMixin):
    __tablename__ = 'labcorp_hl7_results_detail'

    id = Column(Integer, primary_key=True)
    dfsid = Column(String(255))
    guid = Column(String(255))
    file_name = Column(String(400))
    dfsdate = Column(Date)
    dfsname = Column(String(255))
    dfsaddress = Column(String(255))
    dfsegmentsid = Column(String(255))
    dfsegmentsfc = Column(Integer)
    dfsegmentsrep = Column(Integer)
    dfsegmentsseq = Column(Integer)
    dfsegmentsvf = Column(Integer)
    dfsegmentsval = Column(Text)
    dfsegmentsfieldsid = Column(String(255))
    dfsegmentsfieldsval = Column(Text)

    def __repr__(self):
        return self.source

class LabCorpOrderDetails(Model, AuditMixin):
    __tablename__ = 'labcorp_order_details'

    id = Column(Integer, primary_key=True)
    guid = Column(String(255))
    file_name = Column(String(400))
    patient_id = Column(String(255))
    patient_id_2 = Column(String(255))
    control_number = Column(String(255))
    alt_control_number = Column(String(255))
    last_name = Column(String(255))
    middle_name = Column(String(255))
    first_name = Column(String(255))
    date_of_birth = Column(Date)
    patient_phone = Column(String(255))
    sex = Column(String(255))
    race = Column(String(255))
    ethnicity = Column(String(255))
    lab_test = Column(String(255))
    lab_test_code = Column(String(255))
    result = Column(String(255))
    specimen_number = Column(String(255))
    collection_date_and_time = Column(DateTime)
    reported_date_and_time = Column(DateTime)
    clinical_info = Column(String(255))
    fasting = Column(String(255))
    total_volume = Column(String(255))
    specimen_source = Column(String(255))
    abnormal_flag = Column(String(255))
    collection_units = Column(String(255))
    reference_range = Column(String(255))
    test_status = Column(String(255))
    lab = Column(String(255))
    patient_note = Column(Text)
    observation_note_1 = Column(Text)
    observation_note_2 = Column(Text)
    specimen_status = Column(String(255))
    ordering_provider_last_name = Column(String(255))
    ordering_provider_first_name = Column(String(255))
    provider_npi = Column(String(255))
    facility_id = Column(String(255))
    facility_name = Column(String(255))
    facility_street = Column(String(255))
    facility_city = Column(String(255))
    facility_state = Column(String(255))
    facility_zip = Column(String(255))
    facility_phone = Column(String(255))
    facility_director_prefix = Column(String(255))
    facility_director_last_name = Column(String(255))
    facility_director_first_name = Column(String(255))
    data = Column(Text)

    @renders('observation_notes')
    def observation_notes(self):
        if self.observation_note_1 is None and self.observation_note_2 is None:
            observation_notes = 'No Observation Notes'
        elif self.observation_note_1 is not None and self.observation_note_2 is None:
            observation_notes = self.observation_note_1
        else:
            observation_notes = self.observation_note_1 + '<br>' + self.observation_note_2
        return Markup(observation_notes)
    
    @renders('patient_notes')
    def patient_notes(self):
        return Markup(self.patient_note)
    
    @renders('data')
    def test_results_pdf(self):
        return Markup('''<a href="data:application/pdf;base64,{base64}" download="{file_name}.pdf">Download</a>'''.format(base64=self.data, file_name=self.guid))

    @classmethod
    def match_labtest_user(cls, requisition_number, first_name, last_name, date_of_birth):
        print(requisition_number, first_name, last_name, date_of_birth)
        try:
            print('Querying LabCorp Details Match')
            labcorp_order_details = Session.query(LabCorpOrderDetails).\
                    filter(LabCorpOrderDetails.control_number==str(requisition_number).upper(), 
                           LabCorpOrderDetails.first_name==first_name, 
                           LabCorpOrderDetails.last_name==last_name, 
                           LabCorpOrderDetails.date_of_birth==date_of_birth
                           )
            print(labcorp_order_details.id)

            print('Matching to User')
            user = Session.query(User).\
                    filter(CustomUser.first_name==str(first_name).upper(),
                           CustomUser.last_name==str(last_name).upper(),
                           CustomUser.date_of_birth
                           )
            
            print(user.id)
            return (labcorp_order_details.id, user.id)
        except Exception as e:
            return None

    def __repr__(self):
        return self.control_number

class Country(Model):
    __tablename = 'country'

    id = Column(Integer, primary_key=True)
    country = Column(String(256), unique=True)
    country_abbreviation = Column(String(20))
                        
    def __repr__(self):
        return self.country

class State(Model):
    __tablename__ = 'state'

    id = Column(Integer, primary_key=True)
    state_abbreviation = Column(String(256))
    state = Column(String(256))
    fips_code = Column(String(256))
    country_id =  Column(Integer, ForeignKey("country.id"))
    country = relationship('Country')

    def state_province(self, country_id):
        if country_id is None:
            return ''
        elif country_id is 1:
            return ' - US'
        else:
            return ' - Canada'

    def __repr__(self):
        return self.state

class City(Model):
    __tablename__ = 'city'

    id = Column(Integer, primary_key=True)
    state_id = Column(Integer, ForeignKey("state.id"))
    state = relationship('State')
    city = Column(String(256))
    county = Column(String(256))
    latitude = Column(Float)
    longitude = Column(Float)

    def __repr__(self):
        return self.city

assoc_employer_location = Table(
    "ab_employer_location",
    Model.metadata,
    Column("id", Integer, primary_key=True),
    Column("employer_id", Integer, ForeignKey("employer.id")),
    Column("location_id", Integer, ForeignKey("location.id")),
                        )

class Employer(Model):
    __tablename__ = 'employer'

    id = Column(Integer, primary_key=True)
    employer_name = Column(String(100), nullable=False)
    employer_code = Column(String(100), nullable=False, unique=True)
    parent_employer_id = Column(Integer, ForeignKey("parent_employer.id"))
    parent_employer = relationship('ParentEmployer')

    def __repr__(self):
        return self.employer_name

class ParentEmployer(Model):
    __tablename__ = 'parent_employer'

    id = Column(Integer, primary_key=True)
    parent_employer = Column(String(256))

    def __repr__(self):
        return self.parent_employer

assoc_user_result = Table(
    "ab_user_result",
    Model.metadata,
    Column("labcorp_order_details_id", Integer, ForeignKey("labcorp_order_details.id"), unique=True),
    Column("custom_user_id", Integer, ForeignKey("ab_user.id")),
    )

class UserResult(Model):
    __tablename__ = 'ab_user_result'

    id = Column(Integer, primary_key=True)
    labcorp_order_details_id = Column("labcorp_order_details_id", Integer, ForeignKey("labcorp_order_details.id"), unique=True),
    custom_user_id = Column("custom_user_id", Integer, ForeignKey("ab_user.id"))

    def __repr__(self):
        return str(self.id)

class CustomUser(User):
    __tablename__ = 'ab_user'

    middle_name = Column(String(256))
    employer_code = Column(String(256))
    street_address = Column(String(256))
    street_address_line_2 = Column(String(256))
    suite_apt_number = Column(String(256))
    city = Column(String(256))
    state = Column(String(256))
    zip_code = Column(String(256))
    country = Column(String(256))
    date_of_birth = Column(Date)
    phone_number = Column(String(20))
    labcorp_id_number = Column(String(150))
    employee_id_number = Column(String(150))

    results = relationship("LabCorpOrderDetails", secondary=assoc_user_result, backref="CustomUser")

    location_id = Column(Integer, ForeignKey('location.id'))
    location = relationship('Location')

    employer_id = Column(Integer, ForeignKey('employer.id'))
    employer = relationship('Employer')

    hipaa_authorization_id = Column(Integer, ForeignKey('hipaa_authorization.id'))
    hipaa_authorization = relationship('HipaaAuthorization')

    general_informed_consent_id = Column(Integer, ForeignKey('general_informed_consent.id'))
    general_informed_consent = relationship('GeneralInformedConsent')

    gender_id = Column(Integer, ForeignKey('gender.id'))
    gender = relationship("Gender")

    race_id = Column(Integer, ForeignKey('race.id'))
    race = relationship("Race")

    ethnicity_id = Column(Integer, ForeignKey('ethnicity.id'))
    ethnicity = relationship("Ethnicity")

    @renders('employee')
    def employee(self):
        return self.last_name + ', ' + self.first_name

    @renders('address')
    def address(self):
        return Markup(street_address + '<br>' + street_address_line_2 + '<br>' + suite_apt_number + '<br>' + city + ', ' + state + ' ' + zip_code )

class Tests(Model):
    __tablename__ = 'tests'

    id = Column(Integer, primary_key=True)
    test = Column(String(100), unique=True, nullable=False)
    vendor_test_number = Column(String(50))

    def __repr__(self):
        return self.test

class Options(Model):
    __tablename__ = 'options'

    id = Column(Integer, primary_key=True)
    result_option = Column(String(50), unique=True, nullable=False)
    result_option_abbrev = Column(String(20), unique=True)
    result_status = Column(String(20))

    def __repr__(self):
        return self.result_option

class Ethnicity(Model):
    __tablename__ = 'ethnicity'

    id = Column(Integer, primary_key=True)
    ethnicity_code = Column(String(10), unique=True)
    ethnicity_description = Column(String(30), unique=True)

    def __repr__(self):
        return self.ethnicity_description

class Race(Model):
    __tablename__ = 'race'

    id = Column(Integer, primary_key=True)
    race_code = Column(String(10), unique=True)
    race_description = Column(String(100), unique=True)

    def __repr__(self):
        return self.race_description

class Gender(Model):
    __tablename__ = 'gender'

    id = Column(Integer, primary_key=True)
    gender_code = Column(String(5), unique=True)
    gender_description = Column(String(20), unique=True)

    def __repr__(self):
        return self.gender_description

class HipaaAuthorization(Model):
    __tablename__ = 'hipaa_authorization'

    id = Column(Integer, primary_key=True)
    hipaa_authorization = Column(String(100), unique=True)

    def __repr__(self):
        return self.hipaa_authorization

class GeneralInformedConsent(Model):
    __tablename = 'general_informed_consent'

    id = Column(Integer, primary_key = True)
    general_informed_consent = Column(String(100), unique=True)

    def __repr__(self):
        return self.general_informed_consent

class LocationType(Model):
    __tablename__ = 'location_type'

    id = Column(Integer, primary_key = True)
    location_type = Column(String(100))

    def __repr__(self):
        return self.location_type

class Location(Model):
    __tablename__ = 'location'

    id = Column(Integer, primary_key=True)
    location_name = Column(String(150), unique=True, nullable=False)
    street_address = Column(String(150))
    street_address_line_2 = Column(String(150))
    suite_apt_number = Column(String(50))
    city = Column(String(256))
    state = Column(String(256))
    state_2 = Column(String(256))
    country = Column(String(256))
    zip_code = Column(String(256))
    latitude = Column(Float)
    longitude = Column(Float)

    location_type_id = Column(Integer, ForeignKey('location_type.id'), default = 1)
    location_type = relationship('LocationType')

    def __repr__(self):
        return self.location_name

def generate_uuid():
    return str(uuid.uuid4())

class Result(Model, AuditMixin):
    __tablename__ = 'result'

    id = Column(Integer, primary_key=True)
    date_of_birth = Column(Date)
    email = Column(String(100))
    submission_id = Column(String(100), unique=True, default=generate_uuid)
    test_batch_number = Column(String(30))
    comment_section = Column(String(500))
    is_valid_result = Column(Boolean)
    temperature = Column(Float)
    requisition_number = Column(String(200), nullable=False, unique=True)
    test_kit_sent = Column(Boolean, default=0)
    results_emailed = Column(Boolean, default=0)
    date_entered = Column(String(100))
    outgoing_tracking_number = Column(String(256))
    outgoing_shipping_vendor_id = Column(Integer, ForeignKey('shipping_vendors.id'))
    outgoing_shipping_vendor = relationship('ShippingVendors', foreign_keys=[outgoing_shipping_vendor_id])
    incoming_tracking_number = Column(String(256))
    incoming_shipping_vendor_id = Column(Integer, ForeignKey('shipping_vendors.id'))
    incoming_shipping_vendor = relationship('ShippingVendors', foreign_keys=[incoming_shipping_vendor_id])
    is_matched = Column(Boolean, default=0)
    is_sent_to_labcorp = Column(Boolean, default=0)

    location_id = Column(Integer, ForeignKey('location.id'))
    location = relationship('Location', backref='result')

    test_id = Column(Integer, ForeignKey('tests.id'))
    test = relationship("Tests", backref='result')

    result_option_id = Column(Integer, ForeignKey('options.id'))
    result_option = relationship("Options", backref="result")

    def __repr__(self):
        return self.requisition_number

