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
from .mixins import FraxsesMixin

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

class CustomRegisterUser(Model, FraxsesMixin, AuditMixin):
    __tablename__ = "ab_register_user"

    id = Column(Integer, Sequence("ab_register_user_id_seq"), primary_key=True)
    first_name = Column(String(64), nullable=False)
    last_name = Column(String(64), nullable=False)
    username = Column(String(64), unique=True, nullable=False)
    password = Column(String(256))
    email = Column(String(64), nullable=False)
    phone_number = Column(String(256))
    registration_date = Column(DateTime, default=datetime.datetime.now, nullable=True)
    registration_hash = Column(String(256))
    date_of_birth = Column(String(256))
    sex_id = Column(Integer)
    address_line1 = Column(String(256))
    address_line2 = Column(String(256))
    unit_number = Column(String(256))
    city_id = Column(Integer)
    state_id = Column(Integer)
    country_id = Column(Integer)
    hipaa_authorization_id = Column(Integer)
    general_informed_consent_id = Column(Integer)

class LabCorpFile(Model, FraxsesMixin, AuditMixin):
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

class LabCorpFileDetail(Model, FraxsesMixin, AuditMixin):
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

class LabCorpOrderDetails(Model, FraxsesMixin, AuditMixin):
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

class Country(Model, FraxsesMixin, AuditMixin): 
    __tablename = 'country'

    id = Column(Integer, primary_key=True)
    country = Column(String(256), unique=True)
    country_abbreviation = Column(String(20))

    def __repr__(self):
       return self.country
        
        


class State(Model, FraxsesMixin, AuditMixin): 
    __tablename__ = 'state'

    id = Column(Integer, primary_key=True)
    state_abbreviation = Column(String(256))
    state = Column(String(256))
    fips_code = Column(String(256))
    country_id =  Column(Integer, ForeignKey("country.id"))
    country = relationship('Country')

    def state_province(self, country_id):
        if country_id == None:
            return ''
        elif country_id == 1:
            return ' - US'
        else:
            return ' - Canada'

    def __repr__(self):
        return self.state_abbreviation + self.state_province(self.country_id)

class City(Model, FraxsesMixin, AuditMixin): #id, name, state_id
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

assoc_employer_address = Table(
    "ab_employer_address",
    Model.metadata,
    Column("id", Integer, primary_key=True),
    Column("employer_id", Integer, ForeignKey("employer.id")),
    Column("address_id", Integer, ForeignKey("address.id")),
                        )

class Employer(Model, FraxsesMixin, AuditMixin): # not there
    __tablename__ = 'employer'

    id = Column(Integer, primary_key=True)
    employer_name = Column(String(100), nullable=False)
    employer_code = Column(String(100), nullable=False, unique=True)

    @classmethod
    def employer_lookup(cls, employer_code):
        try:
            return Session.query(Employer).filter(Employer.employer_code==employer_code).first()
        except Exception as e:
            return False

    def __repr__(self):
        return self.employer_name

assoc_user_result = Table(
    "ab_user_result",
    Model.metadata,
    Column("id", Integer, primary_key=True),
    Column("labcorp_order_details_id", Integer, ForeignKey("labcorp_order_details.id"), unique=True),
    Column("custom_user_id", Integer, ForeignKey("ab_user.id")),
    )

class UserResult(Model):
    __tablename__ = 'ab_user_result'

    id = Column(Integer, primary_key=True)
    labcorp_order_details_id = Column("labcorp_order_details_id", Integer, ForeignKey("labcorp_order_details.id"), unique=True)
    custom_user_id = Column("custom_user_id", Integer, ForeignKey("ab_user.id"))

    def __repr__(self):
        return str(self.id)

class CustomUser(User, FraxsesMixin):
    __tablename__ = 'ab_user'

    employer_code = Column(String(256))
    #address_line1 = Column(String(256))
    #address_line2 = Column(String(256))
    #suite_apt_number = Column(String(256))
    #city = Column(String(256))
    #state = Column(String(256))
    #zip_code = Column(String(256))
    #country = Column(String(256))
    date_of_birth = Column(Date)
    phone_number = Column(String(20))
    labcorp_id_number = Column(String(150))
    employee_id_number = Column(String(150))

    results = relationship("LabCorpOrderDetails", secondary=assoc_user_result, backref="CustomUser")

    address_id = Column(Integer, ForeignKey('address.id'))
    address = relationship('Address', backref='ab_user',  foreign_keys=[address_id])

    employer_id = Column(Integer, ForeignKey('employer.id'))
    employer = relationship('Employer', primaryjoin='CustomUser.employer_id==Employer.id', backref='ab_user')

    hipaa_authorization_id = Column(Integer, ForeignKey('hipaa_authorization.id'))
    hipaa_authorization = relationship('HipaaAuthorization', primaryjoin='CustomUser.hipaa_authorization_id==HipaaAuthorization.id', backref='ab_user')

    general_informed_consent_id = Column(Integer, ForeignKey('general_informed_consent.id'))
    general_informed_consent = relationship('GeneralInformedConsent', primaryjoin='CustomUser.general_informed_consent_id==GeneralInformedConsent.id', backref='ab_user')

    sex_id = Column(Integer, ForeignKey('sex.id'))
    sex = relationship("Sex", primaryjoin='CustomUser.sex_id==Sex.id', backref='ab_user')

    race_id = Column(Integer, ForeignKey('race.id'))
    race = relationship("Race", primaryjoin='CustomUser.race_id==Race.id', backref='ab_user')

    ethnicity_id = Column(Integer, ForeignKey('ethnicity.id'))
    ethnicity = relationship("Ethnicity", primaryjoin='CustomUser.ethnicity_id==Ethnicity.id', backref='ab_user')

    @renders('employee')
    def employee(self):
        return self.last_name + ', ' + self.first_name

    @renders('address')
    def address(self):
        return Markup(street_address + '<br>' + street_address_line_2 + '<br>' + suite_apt_number + '<br>' + city + ', ' + state + ' ' + zip_code )

class LabTests(Model, FraxsesMixin, AuditMixin):
    __tablename__ = 'lab_tests'

    id = Column(Integer, primary_key=True)
    lab_test = Column(String(100), unique=True, nullable=False)
    vendor_test_number = Column(String(50))

    def __repr__(self):
        return self.test

class ResultOptions(Model, FraxsesMixin, AuditMixin):
    __tablename__ = 'result_options'

    id = Column(Integer, primary_key=True)
    result_option = Column(String(50), unique=True, nullable=False)
    result_option_abbrev = Column(String(20), unique=True)
    result_status = Column(String(20))

    def __repr__(self):
        return self.result_option

class Ethnicity(Model, FraxsesMixin, AuditMixin):
    __tablename__ = 'ethnicity'

    id = Column(Integer, primary_key=True)
    ethnicity_code = Column(String(10), unique=True)
    description = Column(String(30), unique=True)

    def __repr__(self):
        return self.description

class Race(Model, FraxsesMixin, AuditMixin):
    __tablename__ = 'race'

    id = Column(Integer, primary_key=True)
    race_code = Column(String(10), unique=True)
    description = Column(String(100), unique=True)

    def __repr__(self):
        return self.description

class Sex(Model, FraxsesMixin, AuditMixin):
    __tablename__ = 'sex'

    id = Column(Integer, primary_key=True)
    sex_code = Column(String(5), unique=True)
    description = Column(String(20), unique=True)

    def __repr__(self):
        return self.description

class HipaaAuthorization(Model, FraxsesMixin, AuditMixin):
    __tablename__ = 'hipaa_authorization'

    id = Column(Integer, primary_key=True)
    hipaa_authorization = Column(String(100), unique=True)

    def __repr__(self):
        return self.hipaa_authorization

class GeneralInformedConsent(Model, FraxsesMixin, AuditMixin):
    __tablename = 'general_informed_consent'

    id = Column(Integer, primary_key = True)
    general_informed_consent = Column(String(100), unique=True)

    def __repr__(self):
        return self.general_informed_consent

def generate_uuid():
    return str(uuid.uuid4())

class Result(Model, FraxsesMixin, AuditMixin):
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
    fedex_tracking_number = Column(String(500))
    date_entered = Column(String(100))
    is_matched = Column(Boolean, default=0)
    is_sent_to_labcorp = Column(Boolean, default=0)

    outgoing_tracking_number = Column(String(256))
    outgoing_shipping_vendor_id = Column(Integer, ForeignKey('shipping_vendors.id'))
    outgoing_shipping_vendor = relationship('ShippingVendors', foreign_keys=[outgoing_shipping_vendor_id])
    incoming_tracking_number = Column(String(256))
    incoming_shipping_vendor_id = Column(Integer, ForeignKey('shipping_vendors.id'))
    incoming_shipping_vendor = relationship('ShippingVendors', foreign_keys=[incoming_shipping_vendor_id])

    address_id = Column(Integer, ForeignKey('address.id'))
    address = relationship('Address', backref='result',  foreign_keys=[address_id])

    lab_test_id = Column(Integer, ForeignKey('lab_tests.id'), default=1)
    lab_test = relationship("LabTests", backref='result')

    result_option_id = Column(Integer, ForeignKey('result_options.id'), default=5)
    result_option = relationship("ResultOptions", backref="result")

    def __repr__(self):
        return self.requisition_number

class JobTitle(Model, FraxsesMixin, AuditMixin):
    __tablename__ = 'job_title',

    id = Column(Integer, nullable = False, autoincrement = True, primary_key=True)
    description = Column(String(250))

    def __repr__(self):
        return str(self.description)

class Language(Model, FraxsesMixin, AuditMixin):
    __tablename__ = 'language'

    id = Column(Integer, nullable = False, autoincrement = True, primary_key=True)
    description = Column(String(250))

    def __repr__(self):
        return str(self.description)


class Suffix(Model, FraxsesMixin, AuditMixin):
    __tablename__ = 'suffix'

    id = Column(Integer, nullable = False, autoincrement = True, primary_key=True)
    code = Column(String(50))
    description = Column(String(250))

    def __repr__(self):
        return str(self.description)


class IdentityType(Model, FraxsesMixin, AuditMixin):
    __tablename__ = 'identity_type'

    id = Column(Integer, nullable = False, autoincrement = True, primary_key=True)
    description = Column(String(250))

    def __repr__(self):
        return str(self.description)



class MaritalStatus(Model, FraxsesMixin, AuditMixin):
    __tablename__ = 'marital_status'

    id = Column(Integer, nullable = False, autoincrement = True, primary_key=True)
    description = Column(String(250))

    def __repr__(self):
        return str(self.description)


class Title(Model, FraxsesMixin, AuditMixin):
    __tablename__ = 'title'

    id = Column(Integer, nullable = False, autoincrement = True, primary_key=True)
    description = Column(String(250))

    def __repr__(self):
        return str(self.description)


class PersonNote(Model, FraxsesMixin, AuditMixin):
    __tablename__ = 'person_note'

    id = Column(Integer, nullable = False, autoincrement = True, primary_key=True)
    person_id = Column(Integer)
    note_text = Column(String(8000))

    def __repr__(self):
        return str(self.note_text)


#class Sex(Model, FraxsesMixin, AuditMixin):
#    __tablename__ = 'sex'
#
#    id = Column(Integer, nullable = False, autoincrement = True)
#    description = Column(String(250))
#    code = Column(String(5), unique=True)
#
#    def __repr__(self):
#        return str(self.description)


#class Race(Model, FraxsesMixin, AuditMixin):
#    __tablename__ = 'race'
#
#    id = Column(Integer, nullable = False, autoincrement = True)
#    description = Column(String(250))
#
#    def __repr__(self):
#        return str(self.description)


#class Ethnicity(Model, FraxsesMixin, AuditMixin):
#    __tablename__ = 'ethnicity'
#
#    id = Column(Integer, nullable = False, autoincrement = True)
#    description = Column(String(250))
#
#    def __repr__(self):
#        return str(self.description)


class PersonNotification(Model, FraxsesMixin, AuditMixin):
    __tablename__ = 'person_notification'

    id = Column(Integer, nullable = False, autoincrement = True, primary_key=True)
    person_id = Column(Integer)
    notification_date = Column(DateTime)
    notification_type_id = Column(Integer)
    notification_address = Column(String(250))
    message = Column(Text)

    def __repr__(self):
        return str(self.id)


class NotificationType(Model, FraxsesMixin, AuditMixin):
    __tablename__ = 'notification_type'

    id = Column(Integer, nullable = False, autoincrement = True, primary_key=True)
    description = Column(String(50))

    def __repr__(self):
        return str(self.description)


class PersonHash(Model, FraxsesMixin, AuditMixin):
    __tablename__ = 'person_hash'

    id = Column(Integer, nullable = False, autoincrement = True, primary_key=True)
    person_id = Column(Integer)
    hash = Column(Text)
    date = Column(DateTime)
    first_name = Column(String(250))
    last_name = Column(String(250))
    phone_number = Column(String(50))
    date_of_birth = Column(Date)
    address = Column(String(1000))

    def __repr__(self):
        return str(self.hash)


class ClutchMember(Model, FraxsesMixin, AuditMixin): #privacy_accepted, terms_accepted, current_location_longitude, current_location_latitude (all integers)
    __tablename__ = 'clutch_member'

    id = Column(Integer, nullable = False, autoincrement = True, primary_key=True)
    person_id = Column(Integer)
    fraxses_user_code = Column(String(50))
    member_code = Column(String(50))
    dependancy_member_code = Column(String(50))
    clutch_member_type_id = Column(Integer)
    clutch_member_relationship_type_id = Column(Integer)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    clutch_member_status_id = Column(Integer)
    terms_accept_date = Column(DateTime)
    phone_verification = Column(Integer)
    email_verification = Column(Integer)
    receive_push_notifications = Column(Integer)
    receive_sms_notifications = Column(Integer)
    receive_email_notifications = Column(Integer)
    application_preferences = Column(JSONB)
    total_points = Column(Integer)
    total_spend = Column(Integer)

    def __repr__(self):
        return str(self.person_id)


class ClutchMemberType(Model, FraxsesMixin, AuditMixin):
    __tablename__ = 'clutch_member_type'

    id = Column(Integer, nullable = False, autoincrement = True, primary_key=True)
    description = Column(String(250))
    rx_bin = Column(String(50))
    rx_group = Column(String(50))
    rx_pcn = Column(String(50))

    def __repr__(self):
        return str(self.description)


class ClutchMemberStatus(Model, FraxsesMixin, AuditMixin):
    __tablename__ = 'clutch_member_status'

    id = Column(Integer, nullable = False, autoincrement = True, primary_key=True)
    description = Column(String(250))

    def __repr__(self):
        return str(self.description)


class ClutchMemberRelationshipType(Model, FraxsesMixin, AuditMixin):
    __tablename__ = 'clutch_member_relationship_type'

    id = Column(Integer, nullable = False, autoincrement = True, primary_key=True)
    description = Column(String(250))

    def __repr__(self):
        return str(self.description)

class AddressType(Model, FraxsesMixin, AuditMixin):
    __tablename__ = 'address_type'

    id = Column(Integer, primary_key = True)
    location_type = Column(String(100))

    def __repr__(self):
        return str(self.location_type)

class Address(Model, FraxsesMixin, AuditMixin):
    __tablename__ = 'address'

    id = Column(Integer, primary_key=True)
    address_line1 = Column(String(250))
    address_line2 = Column(String(250))
    address_line3 = Column(String(250))
    address_line4 = Column(String(250))
    address_line5 = Column(String(250))
    unit_number = Column(String(250))
#    state_id = Column(Integer, ForeignKey('state.id'))
#    state = relationship('State')
#    state = relationship('State')
    city_id = Column(Integer, ForeignKey("city.id"))
#    , ForeignKey('city.id'))
    city = relationship('City')
    zip_code = Column(String(50))
    country_id = Column(Integer, ForeignKey("country.id"))
#    , ForeignKey('country.id'))
    country = relationship('Country')
    county_fips_code = Column(String(50))
    zip_code = Column(String(256))
    latitude = Column(Integer)
    longitude = Column(Integer)
#    address_type_id = Column(Integer, ForeignKey('address_type.id'))
#    address_type = relationship('AddressType')

    def __repr__(self):
        return self.description


class CountyFips(Model, FraxsesMixin, AuditMixin):
    __tablename__ = 'county_fips'

    id = Column(Integer, primary_key=True)    
    code = Column(String(50), nullable = False)
    place_name = Column(String(250))

    def __repr__(self):
        return str(self.place_name)


class PersonAddress(Model, FraxsesMixin, AuditMixin):
    __tablename__ = 'person_address'
    
    id = Column(Integer, nullable = False, autoincrement = True, primary_key=True)
    person_id = Column(Integer, ForeignKey("person.id"))
    person = relationship('Person')
    address_type_id = Column(Integer, ForeignKey("address_type.id"))
    address_type = relationship('AddressType')
    address_id = Column(Integer, ForeignKey("address.id"))
    address = relationship('Address')
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    preferred_address_indicator = Column(Integer)
    
    def __repr__(self):
        return str(self.id)



class PharmacyAddress(Model, FraxsesMixin, AuditMixin):
    __tablename__ = 'pharmacy_address'

    id = Column(Integer, nullable = False, autoincrement = True, primary_key=True)
    pharmacy_id = Column(Integer, ForeignKey("pharmacy.id"))
    pharmacy = relationship('Pharmacy')
    address_type_id = Column(Integer, ForeignKey("address_type.id"))
    address_type = relationship('AddressType')
    address_id = Column(Integer, ForeignKey("address.id"))
    address = relationship('Address')
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    preferred_address_indicator = Column(Integer)

    def __repr__(self):
        return str(self.id)

#class Prescription(Model):
##    __bind_key__ = 'person'
#    __tablename__ = Table('prescription',
#                      metadata,
##                      Column('id', Integer, primary_key=True),
#                      extend_existing=True,
#                      autoload=True)
#    def __repr__(self):
#        return str(self.id)
#

class PrescriptionStatus(Model, FraxsesMixin, AuditMixin):
    __tablename__ = 'prescription_status'

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    description = Column(String(250))

    def __repr__(self):
        return str(self.description)


class PrescriptionPharmacyPrices(Model, FraxsesMixin, AuditMixin):
    __tablename__ = 'prescription_pharmacy_prices'

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    prescription_id = Column(Integer, ForeignKey("prescription.id"))
    prescription = relationship('Prescription')
    pharmacy_id = Column(Integer, ForeignKey("pharmacy.id"))
    pharmacy = relationship('Pharmacy')
    drug_id = Column(Integer, ForeignKey("drug.id"))
    drug = relationship('Drug')
    price = Column(Integer)
    distance = Column(Integer)
    unit_of_measure_id = Column(Integer)
    selected = Column(Integer)
    points = Column(Integer)
#    location_type_id = Column(Integer, nullable=False)
#    location_lookup_zip_code = Column(String(50))

    def __repr__(self):
        return str(self.price)


class ApiPricesChangeHealth(Model, FraxsesMixin, AuditMixin):
    __tablename__ = 'api_prices_change_health'

    id = Column(Integer, nullable = False, autoincrement = True, primary_key=True)
    prescription_id = Column(Integer)
#    payload = Column(JSONB)
    date = Column(DateTime)

    def __repr__(self):
        return str(self.prescription_id)

class UnitOfMeasure(Model, FraxsesMixin, AuditMixin):
    __tablename__ = 'unit_of_measure'

    id = Column(Integer, nullable = False, autoincrement = True, primary_key=True)
    description = Column(String(250))

    def __repr__(self):
        return str(self.description)


class Drug(Model, FraxsesMixin, AuditMixin):
    __tablename__ = 'drug'

    id = Column(Integer, nullable = False, autoincrement = True, primary_key=True)
    ndc = Column(String(12))
    drug_name = Column(String(1000))
    description = Column(String(8000))
    product_code = Column(String(250))
    qualifier = Column(String(250))
    strength_value = Column(String(250))
    strength_form_code = Column(String(250))
    strength_unit_of_measure_code = Column(String(250))
    controller_substance_class = Column(String(250))
    dea_schedule_code = Column(String(250))
    points = Column(Integer)
    brand_name = Column(String(250))
    
    def __repr__(self):
        return str(self.drug_name)

#class PharmacyDrug(Model):
#    __tablename__ = 'pharmacy_drug'

#    def __repr__(self):
#        return str('self.id)

class Pharmacy(Model, FraxsesMixin, AuditMixin):
    __tablename__ = 'pharmacy'

    id = Column(Integer, nullable = False, autoincrement = True, primary_key=True)
    pharmacy_group_id = Column(Integer, ForeignKey("pharmacy_group.id"))
    pharmacy_group = relationship('PharmacyGroup')
    npi = Column(String(250))
    ncpdp_id = Column(String(250))
    name = Column(String(250))
    primary_phone_number = Column(String(250))
    fax_number = Column(String(250))

    def __repr__(self):
        return str(self.name)


class PharmacyGroup(Model, FraxsesMixin, AuditMixin):
    __tablename__ = 'pharmacy_group'

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    group_name = Column(String(250))
    chain_code = Column(Text)
    
    def __repr__(self):
        return str(self.group_name)


class PharmacyMember(Model, FraxsesMixin, AuditMixin):
    __tablename__ = 'pharmacy_member'

    id = Column(Integer, nullable = False, autoincrement = True, primary_key=True)
    pharmacy_id = Column(Integer, ForeignKey("pharmacy.id"))
    pharmacy = relationship('Pharmacy')
    person_id = Column(Integer, ForeignKey("person.id"))
    person = relationship('Person')
    fraxses_user_code = Column(String(250))

    def __repr__(self):
        return str(self.id)


class NfiItg(Model, FraxsesMixin, AuditMixin):
    __tablename__ = 'nfi_itg'
    
    nfi_itg_nme = Column(String(50), nullable = False, primary_key=True)
    nfi_itg_des = Column(String(250))

    def __repr__(self):
        return str(self.nfi_itg_nme)

class NfiItgTrgReq(Model, FraxsesMixin, AuditMixin):
    __tablename__ = 'nfi_itg_trg_req'

    nfi_trg_nbr = Column(Integer, nullable = False, primary_key=True)
    nfi_itg_nme = Column(String(50))
    nfi_dta_src = Column(String(50))
    str_dte = Column(DateTime)
    end_dte = Column(DateTime)
    stt_cde = Column(String(50))
    req_met = Column(String(50))
    req_url = Column(String(8000))
    req_msg = Column(Text)
#    req_msg_json = Column(JSONB)
    rsp_msg = Column(Text)
#    rsp_msg_json = Column(JSONB)
    rsp_cde = Column(String(50))
#    req_hed = Column(JSONB)
#    req_par = Column(JSONB)
    ent_cde = Column(String(50))
    ent_id = Column(Integer)
    atm_cnt = Column(Integer)
    
    def __repr__(self):
        return str(self.nfi_trg_nbr)

class Person(Model, FraxsesMixin, AuditMixin):
    __tablename__ = 'person'

    id = Column(Integer, nullable = False, autoincrement = True, primary_key=True)
    title_id = Column(Integer, ForeignKey("title.id"))
    initials = Column(String(50))
    first_name = Column(String(250), nullable = False)
    middle_name = Column(String(250))
    last_name = Column(String(250), nullable = False)
    suffix_id = Column(Integer, ForeignKey("suffix.id"))
    preferred_name = Column(String(250))
    email_address = Column(String(250))
    home_telephone_number = Column(String(50))
    office_number = Column(String(50))
    office_extension = Column(String(50))
    fax_number = Column(String(50))
    mobile_number = Column(String(50))
    sex_id = Column(Integer, ForeignKey("sex.id"))
    race_id = Column(Integer, ForeignKey("race.id"))
    ethnicity_id = Column(Integer, ForeignKey("ethnicity.id"))
    marital_status_id = Column(Integer, ForeignKey("marital_status.id"))
    identity_type_id = Column(Integer, ForeignKey("identity_type.id"))
    identity_number = Column(String(250))
    date_of_birth = Column(Date)
#    job_title_id = Column(Integer, ForeignKey("job_title.id"))
    language_id = Column(Integer, ForeignKey("language.id"))
    weight_kg = Column(Integer)
    height_meter = Column(Integer)
    dependant = Column(Integer)


    title = relationship("Title", primaryjoin='Person.title_id==Title.id', backref="person")
    sex = relationship("Sex", primaryjoin='Person.sex_id==Sex.id', backref="person")
    suffix = relationship("Suffix", primaryjoin='Person.suffix_id==Suffix.id', backref="person")
    race = relationship("Race", primaryjoin='Person.race_id==Race.id', backref="person")
    ethnicity = relationship("Ethnicity", primaryjoin='Person.ethnicity_id==Ethnicity.id', backref="person")
    marital_status = relationship("MaritalStatus", primaryjoin='Person.marital_status_id==MaritalStatus.id', backref="person")
    identity_type = relationship("IdentityType", primaryjoin='Person.identity_type_id==IdentityType.id', backref="person")
#    job_title = relationship("JobTitle", primaryjoin='Person.job_title_id==JobTitle.id', backref="person")
    language = relationship("Language", primaryjoin='Person.language_id==Language.id', backref="person")
#    person_address = relationship("PersonAddress", primaryjoin='Person.id==PersonAddress.person_id', backref="person")

    def __repr__(self):
        return Markup(self.first_name + ' ' + self.last_name + ' ' + str(self.date_of_birth))


class Prescriber(Model, FraxsesMixin, AuditMixin):
    __tablename__ = 'prescriber'

    id = Column(Integer, nullable = False, autoincrement = True, primary_key=True)
    npi = Column(String(250))
    person_id = Column(Integer, ForeignKey("person.id"))
    dea_number = Column(String(50))
    speciality_code = Column(String(500))
    state_license_number = Column(String(50))

    person = relationship("Person", primaryjoin='Prescriber.person_id==Person.id', backref="prescriber")

    def __repr__(self):
        return str(self.id)



class Prescription(Model, FraxsesMixin, AuditMixin):
    __tablename__ = 'prescription'

    id = Column(Integer, nullable = False, autoincrement = True, primary_key=True)
    person_id = Column(Integer, ForeignKey("person.id"))
    prescriber_id = Column(Integer, ForeignKey("prescriber.id"))
    drug_id = Column(Integer, ForeignKey("drug.id"))
    rx_new_nfi_trg_nbr = Column(Integer)
    rx_transfer_nfi_trg_nbr = Column(Integer)
    rx_cancel_nfi_trg_nbr = Column(Integer)
    rx_new_message_id = Column(String(250))
    rx_transfer_message_id = Column(String(250))
    rx_cancel_message_id = Column(String(250))
    transferred_pharmacy_id = Column(Integer)
    prescription_status_id = Column(Integer, ForeignKey("prescription_status.id"))
    state_license_number = Column(String(250))
    prescriber_fax_number = Column(String(50))
    date_written = Column(Date)
    sig = Column(String(250))
    dosage_form = Column(String(250))
    quantity = Column(Integer)
    quantity_unit_of_measure_id = Column(Integer, ForeignKey("unit_of_measure.id"))
    refills_remaining = Column(Integer)
    refills_authorized = Column(Integer)
    day_supply = Column(Integer)

    prescriber = relationship("Prescriber", primaryjoin='Prescription.prescriber_id==Prescriber.id', backref="prescription")
    drug = relationship("Drug", primaryjoin='Prescription.drug_id==Drug.id', backref="prescription")
    person = relationship("Person", primaryjoin='Prescription.person_id==Person.id', backref="prescription")
    prescription_status = relationship("PrescriptionStatus", primaryjoin='Prescription.prescription_status_id==PrescriptionStatus.id', backref="prescription")
    unit_of_measure = relationship("UnitOfMeasure", primaryjoin='Prescription.quantity_unit_of_measure_id==UnitOfMeasure.id', backref="prescription")
#    prescription_pharmacy_prices = relationship("PrescriptionPharmacyPrices", primaryjoin='Prescription.id==PrescriptionPharmacyPrices.prescription_id', backref="prescription")

    def __repr__(self):
        return str(self.id)


class OrphanedPrescription(Model, FraxsesMixin, AuditMixin):
    __tablename__ = 'orphaned_prescription'

    id = Column(Integer, nullable = False, autoincrement = True, primary_key=True)
    nfi_trg_nbr = Column(Integer)
    person_id = Column(Integer)
    person_hash = Column(Text)
    prescriber_id = Column(Integer, ForeignKey("prescriber.id"))
    drug_id = Column(Integer, ForeignKey("drug.id"))
    matched_by_fraxses_user_code = Column(String(256))
    matched_date = Column(DateTime)

    prescriber = relationship("Prescriber", primaryjoin='OrphanedPrescription.prescriber_id==Prescriber.id', backref="orphaned_prescription")
    drug = relationship("Drug", primaryjoin='OrphanedPrescription.drug_id==Drug.id', backref="orphaned_prescription")

    def __repr__(self):
        return str(self.id)

