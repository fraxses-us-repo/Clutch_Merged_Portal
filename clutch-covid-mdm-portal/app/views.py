from flask import flash, render_template
from flask_appbuilder.actions import action
from flask_babel import lazy_gettext as _
from . import appbuilder, db
from flask_appbuilder.api import BaseApi, expose
from .models import Employer, RequisitionManifest, ShippingVendors, Country, State, City, Result, ResultOptions, Sex, Ethnicity, Race, HipaaAuthorization, GeneralInformedConsent, Employer, CustomUser, LabCorpFile, LabCorpFileDetail, LabCorpOrderDetails, UserResult
from .models import JobTitle, Language, Suffix, IdentityType, MaritalStatus, Title, PersonNote, PersonNotification, NotificationType, PersonHash, ClutchMember, ClutchMemberType, ClutchMemberStatus, ClutchMemberRelationshipType, Address, CountyFips, PersonAddress, AddressType, PharmacyAddress, PrescriptionStatus, PrescriptionPharmacyPrices, ApiPricesChangeHealth, UnitOfMeasure, Drug, Pharmacy, PharmacyGroup, PharmacyMember, NfiItg, NfiItgTrgReq, Person, Prescriber, Prescription, OrphanedPrescription

from flask_appbuilder import ModelView, SimpleFormView, MasterDetailView, MultipleView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from sqlalchemy import create_engine
from wtforms.ext.sqlalchemy.orm import model_form
from flask_admin.contrib.sqla.filters import BaseSQLAFilter, FilterEqual
from flask import redirect, g
from flask_appbuilder.models.sqla.filters import FilterEqualFunction, BaseFilter, get_field_setup_query, FilterEqual, FilterInFunction
from .user_view import UserDBModelView
from .user_register import ClutchRegisterUserDBView
from flask_babel import lazy_gettext
from flask_appbuilder.widgets import ListBlock, ShowBlockWidget
from flask_appbuilder.fieldwidgets import Select2Widget
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from .geo_fill_view import countries_fill, geo_fill
from flask_appbuilder import  BaseView, expose, has_access
from sqlalchemy import func
from wtforms import ValidationError
from .kits import manifest_fill, kits_shipped_fill
from flask_appbuilder import Model
from sqlalchemy import Sequence, Column, Integer, String, ForeignKey, Date, Boolean, DateTime, Float, Text, Table, Date, UniqueConstraint


assoc_employer_address = Table(
    "ab_employer_address",
    Model.metadata,
    Column("id", Integer, primary_key=True),
    Column("employer_id", Integer, ForeignKey("employer.id")),
    Column("address_id", Integer, ForeignKey("address.id")),
    extend_existing=True,
                        )
                        

assoc_user_result = Table(
    "ab_user_result",
    Model.metadata,
    Column("id", Integer, primary_key=True),
    Column("labcorp_order_details_id", Integer, ForeignKey("labcorp_order_details.id"), unique=True),
    Column("custom_user_id", Integer, ForeignKey("ab_user.id")),
    extend_existing=True,
                        )

def get_user():
    return g.user.id

def get_user_dob():
    return g.user.date_of_birth

def get_user_role():
    return g.user.role

def get_employer():
    return g.user.employer_id

def get_parent_employer():
    parent_employer = db.session.query(Employer).filter(Employer.id == g.user.employer_id).first().parent_employer_id    
    employer = db.session.query(Employer).filter(Employer.parent_employer_id == parent_employer).all()
    print(parent_employer, employer)
    employer = [c.id for c in employer]
    return employer

def employer_location_query():
    employer_locations = db.session.query(assoc_employer_location.c.location_id).filter(assoc_employer_location.c.employer_id == g.user.employer_id).distinct()
    return employer_locations

class FilterInManyFunction(BaseFilter):
    name = "Filter view where field is in a list returned by a function"

    def apply(self, query, func):
        query, field = get_field_setup_query(query, self.model, self.column_name)
        return query.filter(field.any(Location.id.in_(func())))

def get_employer_by_user():
    return g.user.employer

def requisition_manifest_fill():
    manifest = db.session.query(func.count(RequisitionManifest.id)).scalar() 
    print(manifest)
    if manifest < 1000:
        print('Adding requisition manifest')
        try:
            letters = [chr(i) for i in range(65,69)]
            count = 0
            requisition_manifest = []
            for i in letters:
                for j in letters:
                    for k in letters:
                        for num in range(1, 1000):
                            requisition_manifest.append(i+j+k+str(num).zfill(4)+'10002605')
            requisition_manifest = [x for x in requisition_manifest if "Q" not in x or "I" not in x or "O" not in x or "V" not in x ]
            for i in requisition_manifest:
                db.session.add(RequisitionManifest(requisition_number=i))
            db.session.commit() 
        except Exception as e:
            print(e)
            db.session.rollback()
    else:
        print('Requisition Manifest already built')

def general_consent_fill():
    try:
        db.session.add(GeneralInformedConsent(general_informed_consent="No Status Supplied"))
        db.session.add(GeneralInformedConsent(general_informed_consent="I AGREE"))
        db.session.add(GeneralInformedConsent(general_informed_consent="I DO NOT AGREE"))
        db.session.commit()
    except Exception:
        db.session.rollback()

def test_fill():
    try:
        db.session.add(Tests(test="SARS-CoV-2, NAA", vendor_test_number="139900"))
        db.session.add(Tests(test="Rapid Test - IgG", vendor_test_number="1"))
        db.session.add(Tests(test="Rapid Test - IgA", vendor_test_number="2"))
        db.session.add(Tests(test="Rapid Test - IgM", vendor_test_number="3"))
        db.session.add(Tests(test="IgA antibody test for the COVID-19 virus", vendor_test_number="164072"))
        db.session.add(Tests(test="IgM antibody test for the COVID-19 virus", vendor_test_number="164034"))
        db.session.add(Tests(test="IgG antibody test for the COVID-19 virus", vendor_test_number="164055"))
        db.session.commit()
    except Exception:
        db.session.rollback()

def result_option_fill():
    try:
        db.session.add(Options(result_option="Positive (+)", result_option_abbrev="+", result_status="Resulted"))
        db.session.add(Options(result_option="Negative (-)", result_option_abbrev="-", result_status="Resulted"))
        db.session.add(Options(result_option="Inconclusive", result_option_abbrev="Incon.", result_status="Resulted"))
        db.session.add(Options(result_option="Not Resulted", result_option_abbrev="X", result_status="Not Resulted"))
        db.session.add(Options(result_option="Test Shipped", result_option_abbrev="O", result_status="Test Shipped"))
        db.session.commit()
    except Exception:
        db.session.rollback()

def hipaa_status_fill():
    try:
        db.session.add(HipaaAuthorization(hipaa_authorization="No Status Supplied"))
        db.session.add(HipaaAuthorization(hipaa_authorization="I AGREE"))
        db.session.add(HipaaAuthorization(hipaa_authorization="I DO NOT AGREE"))
        db.session.commit()
    except Exception:
        db.session.rollback()

def sex_fill():
    try:
        db.session.add(Sex(sex_code="X", sex_description="Not Indicated"))
        db.session.add(Sex(sex_code="M", sex_description="Male"))
        db.session.add(Sex(sex_code="F", sex_description="Female"))
        db.session.commit()
    except Exception:
        db.session.rollback()

def race_fill():
    try:
        db.session.add(Race(race_code="A", race_description="Asian"))
        db.session.add(Race(race_code="B", race_description="Black/African American"))
        db.session.add(Race(race_code="C", race_description="White/Caucasian"))
        db.session.add(Race(race_code="H", race_description="Hispanic"))
        db.session.add(Race(race_code="I", race_description="American Indian/Alaska Native"))
        db.session.add(Race(race_code="J", race_description="Ashkenazi Jewish"))
        db.session.add(Race(race_code="O", race_description="Other"))
        db.session.add(Race(race_code="P", race_description="Native Hispanic/Pacific Islander"))
        db.session.add(Race(race_code="S", race_description="Sephardic Jewish"))
        db.session.add(Race(race_code="X", race_description="Not Indicated"))
        db.session.commit()
    except Exception:
        db.session.rollback()

def ethnicity_fill():
    try:
        db.session.add(Ethnicity(ethnicity_code="N", ethnicity_description="Non-Hispanic"))
        db.session.add(Ethnicity(ethnicity_code="H", ethnicity_description="Hispanic/Latin"))
        db.session.add(Ethnicity(ethnicity_code="U", ethnicity_description="Unknown"))
        db.session.commit()
    except Exception:
        db.session.rollback()

def shipping_vendors_fill():
    try:
        db.session.add(ShippingVendors(shipping_vendor="UPS"))
        db.session.add(ShippingVendors(shipping_vendor="FedEx"))
    except Exception:
        db.session.rollback()


class Documentation(BaseView):
    default_view = 'erd'    
    
    @expose('/erd')
    @has_access
    def erd(self):
        self.update_redirect()
        return self.render_template('erd.html')


class LabCorpFileModelView(ModelView):
    datamodel = SQLAInterface(LabCorpFile)

    add_columns = ['file_name','message_number','updated_at','process_success','raw_hl7','processed_hl7','error']
    edit_columns = ['file_name','message_number','updated_at','process_success','raw_hl7','processed_hl7','error']
    show_columns = ['file_name','message_number','updated_at','process_success','raw_hl7','processed_hl7','error']
    list_columns = ['file_name','message_number','updated_at','process_success']
	
    show_fieldsets = [
                        ("HL7 Raw Process Logging", {"fields": ['file_name','updated_at','process_success','raw_hl7','processed_hl7','error']}),			
		    ] 
    
    @action("muldelete", "Delete", "Delete all Really?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
            return redirect(self.get_redirect())
        return redirect(self.get_redirect())

class LabCorpFileDetailModelView(ModelView):
    datamodel = SQLAInterface(LabCorpFileDetail)
    
    add_columns = ['guid','dfsid','file_name','dfsdate','dfsname','dfsaddress','dfsegmentsid','dfsegmentsfc','dfsegmentsrep','dfsegmentsseq','dfsegmentsvf','dfsegmentsval','dfsegmentsfieldsid','dfsegmentsfieldsval']
    edit_columns = ['guid','dfsid','file_name','dfsdate','dfsname','dfsaddress','dfsegmentsid','dfsegmentsfc','dfsegmentsrep','dfsegmentsseq','dfsegmentsvf','dfsegmentsval','dfsegmentsfieldsid','dfsegmentsfieldsval']
    show_columns = ['guid','dfsid','file_name','dfsdate','dfsname','dfsaddress','dfsegmentsid','dfsegmentsfc','dfsegmentsrep','dfsegmentsseq','dfsegmentsvf','dfsegmentsval','dfsegmentsfieldsid','dfsegmentsfieldsval']
    list_columns = ['guid','dfsid','file_name','dfsdate','dfsegmentsfieldsid','dfsegmentsfc','dfsegmentsrep']
	
    show_fieldsets = [
                        ("HL7 Summary", {"fields": ['guid','dfsid','file_name','dfsdate','dfsname','dfsaddress']}),
                        ("HL7 Segments", {"fields": ['dfsegmentsid','dfsegmentsfc','dfsegmentsrep','dfsegmentsseq','dfsegmentsvf','dfsegmentsval','dfsegmentsfieldsid','dfsegmentsfieldsval'], "expanded": False}),
                    ]
    @action("muldelete", "Delete", "Delete all Really?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
            return redirect(self.get_redirect())
        return redirect(self.get_redirect())

class LabCorpOrderDetailsModelView(ModelView):
    datamodel = SQLAInterface(LabCorpOrderDetails)
    
    label_columns = {'test_results_pdf':'Test Results PDF', 'observation_notes':'Observation Notes', 'patient_notes':'Patient Notes'}

    add_columns = ['guid','file_name','patient_id','patient_id_2','control_number','alt_control_number','last_name','middle_name','first_name','date_of_birth','patient_phone','sex','race','ethnicity','lab_test','lab_test_code','result','specimen_number','collection_date_and_time','reported_date_and_time','clinical_info','fasting','total_volume','specimen_source','abnormal_flag','collection_units','reference_range','test_status','lab','patient_note','observation_note_1','observation_note_2','specimen_status','ordering_provider_last_name','ordering_provider_first_name','provider_npi','facility_id','facility_name','facility_street','facility_city','facility_state','facility_zip','facility_phone','facility_director_prefix','facility_director_last_name','facility_director_first_name']
    edit_columns = ['guid','file_name','patient_id','patient_id_2','control_number','alt_control_number','last_name','middle_name','first_name','date_of_birth','patient_phone','sex','race','ethnicity','lab_test','lab_test_code','result','specimen_number','collection_date_and_time','reported_date_and_time','clinical_info','fasting','total_volume','specimen_source','abnormal_flag','collection_units','reference_range','test_status','lab','patient_note','observation_note_1','observation_note_2','specimen_status','ordering_provider_last_name','ordering_provider_first_name','provider_npi','facility_id','facility_name','facility_street','facility_city','facility_state','facility_zip','facility_phone','facility_director_prefix','facility_director_last_name','facility_director_first_name']
    show_columns = ['guid','file_name','patient_id','patient_id_2','control_number','alt_control_number','last_name','middle_name','first_name','date_of_birth','patient_phone','sex','race','ethnicity','lab_test','lab_test_code','result','specimen_number','collection_date_and_time','reported_date_and_time','clinical_info','fasting','total_volume','specimen_source','abnormal_flag','collection_units','reference_range','test_status','lab','patient_notes','observation_notes','specimen_status','ordering_provider_last_name','ordering_provider_first_name','provider_npi','facility_id','facility_name','facility_street','facility_city','facility_state','facility_zip','facility_phone','facility_director_prefix','facility_director_last_name','facility_director_first_name','test_results_pdf']
    list_columns = ['guid','file_name','patient_id','control_number','specimen_number','result','reported_date_and_time']
	
    show_fieldsets = [
                        ("Patient Summary", {"fields": ['patient_id','patient_id_2','last_name','middle_name','first_name','date_of_birth','patient_phone','sex','race','ethnicity']}),
                        ("Lab Test Details", {"fields": ['control_number','alt_control_number','lab_test','lab_test_code','result','specimen_number','collection_date_and_time','reported_date_and_time','clinical_info','fasting','total_volume','specimen_source','abnormal_flag','collection_units','reference_range','test_status','lab','patient_notes','observation_notes','specimen_status','test_results_pdf'], "expanded": False}),
			("Provider Details", {"fields": ['ordering_provider_last_name','ordering_provider_first_name','provider_npi'], "expanded": False}),
			("Facility Details", {"fields": ['facility_id','facility_name','facility_street','facility_city','facility_state','facility_zip','facility_phone','facility_director_prefix','facility_director_last_name','facility_director_first_name'], "expanded": False}),                   ("Audit", {"fields": ["guid","file_name","created_by", "created_on", "changed_by", "changed_on"],"expanded": False})
                    ]
    @action("muldelete", "Delete", "Delete all Really?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
            return redirect(self.get_redirect())
        return redirect(self.get_redirect())

class ClientLabCorpOrderDetailsModelView(ModelView):
    datamodel = SQLAInterface(LabCorpOrderDetails)
            
    label_columns = {'control_number':'Requisition Number','test_results_pdf':'Download Results', 'observation_notes':'Observation Notes', 'patient_notes':'Patient Notes','reported_date_and_time':'Reported Date','collection_date_and_time':'Collection Date'}

    show_columns = ['guid','file_name','patient_id','patient_id_2','control_number','alt_control_number','last_name','middle_name','first_name','date_of_birth','patient_phone','sex','race','ethnicity','lab_test','lab_test_code','result','specimen_number','collection_date_and_time','reported_date_and_time','clinical_info','fasting','total_volume','specimen_source','abnormal_flag','collection_units','reference_range','test_status','lab','patient_notes','observation_notes','specimen_status','ordering_provider_last_name','ordering_provider_first_name','provider_npi','facility_id','facility_name','facility_street','facility_city','facility_state','facility_zip','facility_phone','facility_director_prefix','facility_director_last_name','facility_director_first_name','test_results_pdf']
    list_columns = ['control_number','lab_test','result','test_results_pdf','collection_date_and_time','reported_date_and_time']

    show_fieldsets = [
                        ("Patient Summary", {"fields": ['patient_id','patient_id_2','last_name','middle_name','first_name','date_of_birth','patient_phone','sex','race','ethnicity']}),
                        ("Lab Test Details", {"fields": ['control_number','alt_control_number','lab_test','lab_test_code','result','specimen_number','collection_date_and_time','reported_date_and_time','clinical_info','fasting','total_volume','specimen_source','abnormal_flag','collection_units','reference_range','test_status','lab','patient_notes','observation_notes','specimen_status','test_results_pdf'], "expanded": False}),
                        ("Provider Details", {"fields": ['ordering_provider_last_name','ordering_provider_first_name','provider_npi'], "expanded": False}),
                        ("Facility Details", {"fields": ['facility_id','facility_name','facility_street','facility_city','facility_state','facility_zip','facility_phone','facility_director_prefix','facility_director_last_name','facility_director_first_name'], "expanded": False})
                        ]


class ResultModelView(ModelView):
    datamodel = SQLAInterface(Result)

    add_columns = ['date_of_birth','email','submission_id','test_batch_number','comment_section','is_valid_result','temperature','requisition_number','incoming_tracking_number','incoming_shipping_vendor','outgoing_tracking_number','outgoing_shipping_vendor','test_kit_sent','results_emailed','is_matched','is_sent_to_labcorp']
    edit_columns = ['date_of_birth','email','submission_id','test_batch_number','comment_section','is_valid_result','temperature','requisition_number','incoming_tracking_number','incoming_shipping_vendor','outgoing_tracking_number','outgoing_shipping_vendor','test_kit_sent','results_emailed','is_matched','is_sent_to_labcorp']
    show_columns = ['date_of_birth','email','submission_id','test_batch_number','comment_section','is_valid_result','temperature','requisition_number','incoming_tracking_number','incoming_shipping_vendor','outgoing_tracking_number','outgoing_shipping_vendor','test_kit_sent','results_emailed','is_matched','is_sent_to_labcorp']
    list_columns = ['submission_id','requisition_number','is_matched','is_sent_to_labcorp']
    
    @action("muldelete", "Delete", "Delete all Really?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
            return redirect(self.get_redirect())
        return redirect(self.get_redirect())

class ClientResultModelView(ResultModelView):
    # Test Registration View
    add_columns = ['requisition_number','comment_section']
    show_columns = ['requisition_number','comment_section']

    show_title = "Registered Test Kits"
    list_title = "Registered Test Kits"
    add_title = "Register Test Kit"
        
    def validate_requisition_number(form, field):
        requisition_number = db.session.query(RequisitionManifest).filter(RequisitionManifest.requisition_number==field.data).first()
    
        if requisition_number is None:
            raise ValidationError('Invalid requisition number. Please check that the requisition number matches the one received on the box.')

    validators_columns = {
                    'requisition_number':[validate_requisition_number]
                        }

#class ParentEmployerModelView(ModelView):
#    datamodel = SQLAInterface(ParentEmployer)
#    
#    add_columns = ['parent_employer']
#    edit_columns = ['parent_employer']
#    show_columns = ['parent_employer']
#    list_columns = ['parent_employer']
#
class EmployerModelView(ModelView):
    datamodel = SQLAInterface(Employer)
    related_views = [UserDBModelView]

    add_columns = ['employer_name','employer_code']
    edit_columns = ['employer_name','employer_code']
    show_columns = ['employer_name','employer_code']
    list_columns = ['employer_name','employer_code']

    @action("muldelete", "Delete", "Delete all Really?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
            return redirect(self.get_redirect())
        return redirect(self.get_redirect())

# EMPLOYEE & EMPLOYER VIEWS
class EmployeeModelView(MasterDetailView):
    datamodel = SQLAInterface(CustomUser)
    related_views = [ClientLabCorpOrderDetailsModelView]
    
    base_order = ("last_name", "asc")
    base_filters = [["id", FilterEqualFunction, get_user]]
    list_columns = ['employee']

    @action("muldelete", "Delete", "Delete all Really?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
            return redirect(self.get_redirect())
        return redirect(self.get_redirect())

class EmployeeDetailModelView(ModelView):
    datamodel = SQLAInterface(CustomUser)
    related_views = [LabCorpOrderDetailsModelView]
    
    list_columns = ["last_name","first_name","employer","date_of_birth","phone_number","email","results"]
    show_fieldsets = [
                ("Employee Summary", {"fields": ["last_name","first_name","employer","date_of_birth","phone_number","email"]}),
                ("Address Details", {"fields": ["street_address","street_address_line_2","suite_apt_number","city","state","zip_code"], "expanded": False}),
                ]

    base_filters = [["employer_id", FilterInFunction, get_parent_employer]]
    base_order = ("last_name", "asc")

    @action("muldelete", "Delete", "Delete all Really?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
            return redirect(self.get_redirect())
        return redirect(self.get_redirect())

class SupervisorModelView(EmployeeDetailModelView):
    datamodel = SQLAInterface(CustomUser)
    related_views = [LabCorpOrderDetailsModelView]

    base_filters = [["employer_id", FilterEqualFunction, get_employer]]
    base_order = ("last_name", "asc")

#class LocationModelView(ModelView):
#    datamodel = SQLAInterface(Location)
#
#    add_columns = ["location_name","street_address","street_address_line_2","suite_apt_number","city","state","zip_code","latitude","longitude"]
#    edit_columns = ["location_name","street_address","street_address_line_2","suite_apt_number","city","state","zip_code","latitude","longitude"]
#    show_columns = ["location_name","street_address","street_address_line_2","suite_apt_number","city","state","zip_code","latitude","longitude"]
#    list_columns = ["location_name","street_address","street_address_line_2","suite_apt_number","city","state","zip_code","latitude","longitude"]
#
#    @action("muldelete", "Delete", "Delete all Really?", "fa-rocket")
#    def muldelete(self, items):
#        if isinstance(items, list):
#            self.datamodel.delete_all(items)
#            self.update_redirect()
#        else:
#            self.datamodel.delete(items)
#            return redirect(self.get_redirect())
#        return redirect(self.get_redirect())

#class CountryModelView(ModelView):
#    datamodel = SQLAInterface(Country)
#    
#    add_columns = ['country']
#    edit_columns = ['country']
#    show_columns = ['country']
#    list_columns = ['country']

#class CityModelView(ModelView):
#    datamodel = SQLAInterface(City)
#    
#    add_columns = ['city', 'state','latitude','longitude']
#    edit_columns = ['city','state','latitude','longitude']
#    show_columns = ['city','state','latitude','longitude']
#    list_columns = ['city','state','latitude','longitude']

#class StateModelView(ModelView):
#    datamodel = SQLAInterface(State)
#
#    add_columns = ['state','state_abbreviation','country']
#    edit_columns = ['state','state_abbreviation','country']
#    show_columns = ['state','state_abbreviation','country']
#    list_columns = ['state','state_abbreviation','country']

class RequisitionManifestModelView(ModelView):
    datamodel = SQLAInterface(RequisitionManifest)
    
    add_columns = ['requisition_number','tracking_number','shipping_vendor']
    edit_columns = ['requisition_number','tracking_number','shipping_vendor']
    show_columns = ['requisition_number','tracking_number','shipping_vendor']
    list_columns = ['requisition_number','tracking_number','shipping_vendor']

    @action("muldelete", "Delete", "Delete all Really?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
            return redirect(self.get_redirect())
        return redirect(self.get_redirect())


# COX CUSTOM EMPLOYER VIEWS
class CoxResultModelView(ModelView):
    datamodel = SQLAInterface(Result)
    related_views = [EmployeeModelView]

    base_permissions = ["can_list", "can_show"]

    search_columns = ['requisition_number','submission_id']
    add_columns = ["is_valid_result","requisition_number","submission_id"]
    edit_columns = ["is_valid_result","requisition_number","submission_id"]
    show_columns = ["is_valid_result","requisition_number","submission_id","result.option.result_status"]
    list_columns = ["is_valid_result","requisition_number","submission_id","result_option.result_status"]

    #base_filters = [["location_id", FilterInFunction, employer_location_query]]
    #base_order = ("requisition_number", "asc")

class CoxEmployeeDetailModelView(ModelView):
    datamodel = SQLAInterface(CustomUser)
    related_views = [CoxResultModelView]

    base_permissions = ["can_list", "can_show"]

    search_columns = ['last_name','first_name','date_of_birth','phone_number','email']
    list_columns = ["last_name","first_name","employer_code","date_of_birth","phone_number","email","results"]
    show_fieldsets = [
                        ("Employee Summary", {"fields": ["last_name","first_name","employer","date_of_birth","phone_number","email"]}),
                        ("Address Details", {"fields": ["street_address","street_address_line_2","suite_apt_number","city","state","zip_code"], "expanded": False}),
                    ]
    
    base_filters = [["employer_id", FilterEqualFunction, get_employer]]
    #base_order = ("last_name", "asc")

class CoxSupervisorModelView(SupervisorModelView):
    related_views = [CoxResultModelView]
    
    base_permissions = ["can_list", "can_show"]

@appbuilder.app.errorhandler(404)
def page_not_found(e):
    return (
        render_template(
            "404.html", base_template=appbuilder.base_template, appbuilder=appbuilder
        ),
        404,
    )

db.create_all()

kits_shipped_fill()
manifest_fill()
countries_fill()
requisition_manifest_fill()
shipping_vendors_fill()
geo_fill()
test_fill()
result_option_fill()
sex_fill()
race_fill()
ethnicity_fill()
hipaa_status_fill()
general_consent_fill()

appbuilder.add_view(
    LabCorpFileModelView,
    "LabCorp File Model View",
    icon="fa-group",
    label=_("LabCorp - HL7"),
    category="Diagnostics",
    category_icon="fa-table"
)

appbuilder.add_view(
    LabCorpFileDetailModelView,
    'LabCorp File Detail Model View',
    icon='fa-group',
    label=_('LabCorp - HL7 Detail'),
    category='Diagnostics',
    category_icon='fa-table'
)

appbuilder.add_view(
    LabCorpOrderDetailsModelView,
    'LabCorp Order Details Model View',
    icon='fa-group',
    label=_('LabCorp - HL7 Order Details'),
    category='Diagnostics',
    category_icon='fa-table'
)

appbuilder.add_separator("Diagnostics")

#appbuilder.add_view(
#    CityModelView,
#    'City Model View',
#    icon='fa-group',
#    label=_('City'),
#    category='Diagnostics',
#    category_icon='fa-table'
#)

#appbuilder.add_view(
#    StateModelView,
#    'State Model View',
#    icon='fa-group',
#    label=_('State'),
#    category='Diagnostics',
#    category_icon='fa-table'
#)

#appbuilder.add_view(
#    CountryModelView,
#    'Country Model View',
#    icon='fa-group',
#    label=_('Country'),
#    category='Diagnostics',
#    category_icon='fa-table'
#)

#appbuilder.add_view(
#    LocationModelView,
#    "Location Model View",
#    icon="fa-group",
#    label=_("Locations"),
#    category="Diagnostics",
#    category_icon="fa-table",
#)

#appbuilder.add_view(
#    ParentEmployerModelView,
#    'Parent Employer Model View',
#    icon="fa-group",
#    label=_("Parent Employers"),
#    category="Diagnostics",
#    category_icon="fa-cogs"
#)

appbuilder.add_view(
    EmployerModelView,
    "Employer Model View",
    icon="fa-group",
    label=_("Employers"),
    category="Diagnostics",
    category_icon="fa-table",
)

appbuilder.add_view(
    ResultModelView,
    'Result Model View',
    icon="fa-group",
    label=_("Results"),
    category="Diagnostics",
    category_icon="fa-table"
)

appbuilder.add_view(
    RequisitionManifestModelView,
    'Requisition Manifest Model View',
    icon="fa-group",
    label=_('Requisition Manifest'),
    category="Diagnostics",
    category_icon="fa-table"
)

appbuilder.add_view(
    ClientResultModelView,
    'Test Registration',
    icon="fa-group",
    label=_("Register Test"),
    category="Diagnostics",
    category_icon="fa-table"
)

appbuilder.add_separator("Diagnostics")

appbuilder.add_view(
    SupervisorModelView,
    'Supervisor Model View',
    icon="fa-group",
    label=_("View Employee Results"),
    category="Diagnostics",
    category_icon="fa-cogs"
)

appbuilder.add_view(
    EmployeeModelView,
    'Employee Model View',
    icon="fa-group",
    label=_("View Your Results"),
    category="Diagnostics",
    category_icon="fa-cogs"
)

appbuilder.add_view(
    EmployeeDetailModelView,
    'Employee Detail Model View',
    icon="fa-group",
    label=_("Employee Detail Results"),
    category="Diagnostics",
    category_icon="fa-cogs"
)

appbuilder.add_separator('Diagnostics')

appbuilder.add_view(
    CoxSupervisorModelView,
    'Cox Supervisor Model View',
    icon="fa-group",
    label=_("Cox Employer Results"),
    category="Diagnostics",
    category_icon="fa-cogs"
)

appbuilder.add_view(
    CoxEmployeeDetailModelView,
    'Cox Employee Detail Model View',
    icon='fa-group',
    label=_('Cox Employee Detail Results'),
    category="Diagnostics",
    category_icon="fa-cogs"
)

appbuilder.add_view(
    CoxResultModelView,
    'Cox Result Model View',
    icon='fa-group',
    label=_('Cox Results'),
    category="Diagnostics",
    category_icon="fa-cogs"
)

class JobTitleModelView(ModelView):
#             resource_name = "job_title"
    datamodel = SQLAInterface(JobTitle)
#             allow_browser_login = True

    show_fieldsets = [
            (
                'Job Title',
                {'fields': ['id','description']})
                
                ]
    list_columns = ['id','description']
    label_columns = {'id':'Id','description':'Description'}

    @action("muldelete", "Delete", "Delete all?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())

appbuilder.add_view(
    JobTitleModelView,
    "Job Title Model View",
    icon="fa-table",
    label=("Job Title"),
    category="Person",
    category_icon="fa-group",
)

class LanguageModelView(ModelView):
#             resource_name = "language"
    datamodel = SQLAInterface(Language)
#             allow_browser_login = True

    show_fieldsets = [
            (
                'Language',
                {'fields': ['id','description']})
        ]
    list_columns = ['id','description']
    label_columns = {'id':'Id','description':'Description'}


    @action("muldelete", "Delete", "Delete all?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())

appbuilder.add_view(
    LanguageModelView,
    "Language Model View",
    icon="fa-table",
    label=("Language"),
    category="Person",
    category_icon="fa-group",
)

class SuffixModelView(ModelView):
#             resource_name = "suffix"
    datamodel = SQLAInterface(Suffix)
#             allow_browser_login = True

    show_fieldsets = [
            (
                'Suffix',
                {'fields': ['id', 'code', 'description']})
        ]
    list_columns = ['id', 'code', 'description']
    label_columns = {'id':'Id', 'code':'Code', 'description':'Description'}


    @action("muldelete", "Delete", "Delete all?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())


appbuilder.add_view(
    SuffixModelView,
    "Suffix Model View",
    icon="fa-table",
    label=("Suffix"),
    category="Person",
    category_icon="fa-group",
)

class IdentityTypeModelView(ModelView):
#             resource_name = "identity_type"
    datamodel = SQLAInterface(IdentityType)
#             allow_browser_login = True

    show_fieldsets = [
            (
                'Identity Type',
                {'fields': ['id','description']})
        ]
    list_columns = ['id','description']
    label_columns = {'id':'Id','description':'Description'}


    @action("muldelete", "Delete", "Delete all?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
           self.datamodel.delete_all(items)
           self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())


appbuilder.add_view(
    IdentityTypeModelView,
    "Identity Type Model View",
    icon="fa-table",
    label=("Identity Type"),
    category="Person",
    category_icon="fa-group",
)

class MaritalStatusModelView(ModelView):
#             resource_name = "marital_status"
    datamodel = SQLAInterface(MaritalStatus)
#             allow_browser_login = True

    show_fieldsets = [
            (
                'Marital Status',
                {'fields': ['id','description']})
        ]
    list_columns = ['id','description']
    label_columns = {'id':'Id','description':'Description'}


    @action("muldelete", "Delete", "Delete all?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())


appbuilder.add_view(
    MaritalStatusModelView,
    "Marital Status Model View",
    icon="fa-table",
    label=("Marital Status"),
    category="Person",
    category_icon="fa-group",
)

class TitleModelView(ModelView):
#             resource_name = "title"
    datamodel = SQLAInterface(Title)
#             allow_browser_login = True

    show_fieldsets = [
            (
                'Title',
                {'fields': ['id','description']})
        ]
    list_columns = ['id','description']
    label_columns = {'id':'Id','description':'Description'}


    @action("muldelete", "Delete", "Delete all?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())


appbuilder.add_view(
    TitleModelView,
    "Title Model View",
    icon="fa-table",
    label=("Title"),
    category="Person",
    category_icon="fa-group",
)    

class PersonNoteModelView(ModelView):
#             resource_name = "person_note"
    datamodel = SQLAInterface(PersonNote)
#             allow_browser_login = True

    show_fieldsets = [
            (
                'Person Note',
                {'fields': ['id','person_id', 'note_text']})
        ]
    list_columns = ['id','person_id','note_text']
    label_columns = {'id':'Id','person_id':'Person ID', 'note_text':'Note Text'}


    @action("muldelete", "Delete", "Delete all?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())


appbuilder.add_view(
    PersonNoteModelView,
    "Person Note Model View",
    icon="fa-table",
    label=("Person Note"),
    category="Person",
    category_icon="fa-group",
)

class SexModelView(ModelView):
#             resource_name = "sex"
    datamodel = SQLAInterface(Sex)
#             allow_browser_login = True

    show_fieldsets = [
            (
                'Sex',
                {'fields': ['id','description']})
        ]
    list_columns = ['id','description']
    label_columns = {'id':'Id','description':'Description'}


    @action("muldelete", "Delete", "Delete all?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())


appbuilder.add_view(
    SexModelView,
    "Sex Model View",
    icon="fa-table",
    label=("Sex"),
    category="Person",
    category_icon="fa-group",
)

class RaceModelView(ModelView):
#             resource_name = "race"
    datamodel = SQLAInterface(Race)
#             allow_browser_login = True

    show_fieldsets = [
            (
                'Race',
                {'fields': ['id','description']})
        ]
    list_columns = ['id','description']
    label_columns = {'id':'Id','description':'Description'}

    @action("muldelete", "Delete", "Delete all?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())


appbuilder.add_view(
    RaceModelView,
    "Race Model View",
    icon="fa-table",
    label=("Race"),
    category="Person",
    category_icon="fa-group",
)

class EthnicityModelView(ModelView):
#             resource_name = "ethnicity"
    datamodel = SQLAInterface(Ethnicity)
#             allow_browser_login = True

    show_fieldsets = [
            (
                'Ethnicity',
                {'fields': ['id','description']})
        ]
    list_columns = ['id','description']
    label_columns = {'id':'Id','description':'Description'}

    @action("muldelete", "Delete", "Delete all?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())


appbuilder.add_view(
    EthnicityModelView,
    "Ethnicity Model View",
    icon="fa-table",
    label=("Ethnicity"),
    category="Person",
    category_icon="fa-group",
)

class PersonNotificationModelView(ModelView):
#             resource_name = "person_notification"
    datamodel = SQLAInterface(PersonNotification)
#             allow_browser_login = True

    show_fieldsets = [
            (
                'Person Notification',
                {'fields': ['id','person_id', 'notification_id', 'notification_type_id', 'notification_address', 'message']})
        ]
    list_columns = ['id','person_id', 'notification_id', 'notification_type_id', 'notification_address', 'message']
    label_columns = {'id':'Id','person_id':'Person ID', 'notification_id':'Notification ID', 'notification_type_id':'Notification Type ID', 'notification_address':'Notification Address', 'message':'Message'}

    @action("muldelete", "Delete", "Delete all?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())



appbuilder.add_view(
    PersonNotificationModelView,
    "Person Notification Model View",
    icon="fa-table",
    label=("Person Notification"),
    category="Person",
    category_icon="fa-group",
)

class NotificationTypeModelView(ModelView):
#             resource_name = "notification_type"
    datamodel = SQLAInterface(NotificationType)
#             allow_browser_login = True

    show_fieldsets = [
            (
                'Notification Type',
                {'fields': ['id','description']})
        ]
    list_columns = ['id','description']
    label_columns = {'id':'Id','description':'Description'}

    @action("muldelete", "Delete", "Delete all?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())


appbuilder.add_view(
    NotificationTypeModelView,
    "Notification Type Model View",
    icon="fa-table",
    label=("Notification Type"),
    category="Prescription/Drug",
    category_icon="fa-adjust",
)

class PersonHashModelView(ModelView):
#             resource_name = "person_hash"
    datamodel = SQLAInterface(PersonHash)
#             allow_browser_login = True

    show_fieldsets = [
            (
                'Person Hash',
                {'fields': ['id','person_id', 'hash', 'date', 'first_name', 'last_name', 'phone_number', 'date_of_birth', 'address']})
        ]
    list_columns = ['id','person_id','hash', 'date', 'first_name', 'last_name', 'phone_number', 'date_of_birth', 'address']
    label_columns = {'id':'Id','person_id':'Person ID','hash':'Hash','date':'Date','first_name':'First Name','last_name':'Last Name','phone_number':'Phone Number','date_of_birth':'Date of Birth','address':'Address'}

    @action("muldelete", "Delete", "Delete all?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())


appbuilder.add_view(
    PersonHashModelView,
    "Person Hash Model View",
    icon="fa-table",
    label=("Person Hash"),
    category="Person",
    category_icon="fa-group",
)

class ClutchMemberModelView(ModelView):
#             resource_name = "clutch_member"
    datamodel = SQLAInterface(ClutchMember)
#             allow_browser_login = True

    show_fieldsets = [
            (
                'Clutch Member',
                {'fields': ['id','person_id', 'fraxses_user_code', 'member_code', 'dependancy_member_code', 'clutch_member_type_id', 'clutch_member_relationship_type_id', 'start_date', 'end_date', 'clutch_member_status_id', 'terms_accept_date', 'phone_verification', 'email_verification', 'receive_push_notifications', 'receive_sms_notifications', 'receive_email_notifications', 'total_points', 'total_spend']})
        ]
    list_columns = ['id','person_id', 'fraxses_user_code', 'member_code', 'dependancy_member_code', 'clutch_member_type_id', 'clutch_member_relationship_type_id', 'start_date', 'end_date', 'clutch_member_status_id', 'terms_accept_date', 'phone_verification', 'email_verification', 'receive_push_notifications', 'receive_sms_notifications', 'receive_email_notifications', 'total_points', 'total_spend']
    label_columns = {'id':'Id','person_id':'Person Id', 'fraxses_user_code':'Fraxses User Code', 'member_code':'Member Code', 'dependancy_member_code':'Dependancy Member Code', 'clutch_member_type_id':'Clutch Member Type Id', 'clutch_member_relationship_type_id':'Clutch Member Relationship Type Id', 'start_date':'Start Date', 'end_date':'End Date', 'clutch_member_status_id':'Clutch Member Status Id', 'terms_accept_date':'Terms Accept Date', 'phone_verification':'Phone Verification', 'email_verification':'Email Verification', 'receive_push_notifications':'Receive Push Notifications', 'receive_sms_notifications':'Receive SMS Notifications', 'receive_email_notifications':'Receive Email Notifications', 'total_points':'Total Points', 'total_spend':'Total Spend'}
    
    add_exclude_columns = ['application_preferences']
    edit_exclude_columns = ['application_preferences']
    search_exclude_columns = ['application_preferences']


    @action("muldelete", "Delete", "Delete all?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())


appbuilder.add_view(
    ClutchMemberModelView,
    "Clutch Member Model View",
    icon="fa-table",
    label=("Clutch Member"),
    category="Person",
    category_icon="fa-group",
)

class ClutchMemberTypeModelView(ModelView):
#             resource_name = "clutch_member_type"
    datamodel = SQLAInterface(ClutchMemberType)
#             allow_browser_login = True
    
    show_fieldsets = [
            (
                'Clutch Member Type',
                {'fields': ['id','description', 'rx_bin', 'rx_group', 'rx_pcn']})
        ]
    list_columns = ['id','description', 'rx_bin', 'rx_group', 'rx_pcn']
    label_columns = {'id':'Id','description':'Description', 'rx_bin':'Rx Bin', 'rx_group':'Rx Group', 'rx_pcn':'Rx Pcn'}    
    
    @action("muldelete", "Delete", "Delete all?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())


appbuilder.add_view(
    ClutchMemberTypeModelView,
    "Clutch Member Type Model View",
    icon="fa-table",
    label=("Clutch Member Type"),
    category="Person",
    category_icon="fa-group",
)

class ClutchMemberStatusModelView(ModelView):
#             resource_name = "clutch_member_status"
    datamodel = SQLAInterface(ClutchMemberStatus)
#             allow_browser_login = True

    show_fieldsets = [
            (
                'Clutch Member Status',
                {'fields': ['id','description']})
        ]
    list_columns = ['id','description']
    label_columns = {'id':'Id','description':'Description'}

    @action("muldelete", "Delete", "Delete all?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())


appbuilder.add_view(
    ClutchMemberStatusModelView,
    "Clutch Member Status Model View",
    icon="fa-table",
    label=("Clutch Member Status"),
    category="Person",
    category_icon="fa-group",
)

class ClutchMemberRelationshipTypeModelView(ModelView):
#             resource_name = "clutch_member_relationship_type"
    datamodel = SQLAInterface(ClutchMemberRelationshipType)
#             allow_browser_login = True

    show_fieldsets = [
            (
                'Clutch Member Relationship Type',
                {'fields': ['id','description']})
        ]
    list_columns = ['id','description']
    label_columns = {'id':'Id','description':'Description'}

    @action("muldelete", "Delete", "Delete all?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())


appbuilder.add_view(
    ClutchMemberRelationshipTypeModelView,
    "Clutch Member Relationship Type Model View",
    icon="fa-table",
    label=("Clutch Member Relationship Type"),
    category="Person",
    category_icon="fa-group",
)

class AddressModelView(ModelView):
#             resource_name = "address"
    datamodel = SQLAInterface(Address)
#             allow_browser_login = True

    show_fieldsets = [
            (
                'Address',
                {'fields': ['id','address_line1','address_line2','address_line3','address_line4','address_line5','unit_number','city_id','county_fips_code','zip_code','country_id','longitude','latitude']})
        ]
    list_columns = ['id','address_line1','address_line2','address_line3','address_line4','address_line5','unit_number','city_id','county_fips_code','zip_code','country_id','longitude','latitude']
    label_columns = {'id':'Id','address_line1':'Address Line 1','address_line2':'Address Line 2','address_line3':'Address Line 3','address_line4':'Address Line 4','address_line5':'Address Line 5','unit_number':'Unit Number','city_id':'City Id','county_fips_code':'County Fips Code','zip_code':'Zip Code','country_id':'Country Id','longitude':'Longitude','latitude':'Latitude'}

    @action("muldelete", "Delete", "Delete all?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())


appbuilder.add_view(
    AddressModelView,
    "Address Model View",
    icon="fa-table",
    label=("Address"),
    category="Address",
    category_icon="fa-map-pin",
)

class StateModelView(ModelView):
#             resource_name = "state"
    datamodel = SQLAInterface(State)
#             allow_browser_login = True

    show_fieldsets = [
            (
                'State',
                {'fields': ['id','name','abbreviated_name','fips_code']})
        ]
    list_columns = ['id','name','abbreviated_name','fips_code']
    label_columns = {'id':'Id','name':'Name','abbreviated_name':'Abbreviated Name','fips_code':'Fips Code'}

    @action("muldelete", "Delete", "Delete all?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())


appbuilder.add_view(
    StateModelView,
    "State Model View",
    icon="fa-table",
    label=("State"),
    category="Address",
    category_icon="fa-map-pin",
)

class CityModelView(ModelView):
#             resource_name = "city"
    datamodel = SQLAInterface(City)
#             allow_browser_login = True

    show_fieldsets = [
            (
                'City',
                {'fields': ['id','name','state_id']})
        ]
    list_columns = ['id','name','state_id']
    label_columns = {'id':'Id','name':'Name','state_id':'State Id'}

    @action("muldelete", "Delete", "Delete all?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())


appbuilder.add_view(
    CityModelView,
    "City Model View",
    icon="fa-table",
    label=("City"),
    category="Address",
    category_icon="fa-map-pin",
)

class CountryModelView(ModelView):
#             resource_name = "country"
    datamodel = SQLAInterface(Country)
#             allow_browser_login = True

    show_fieldsets = [
            (
                'Country',
                {'fields': ['id','description']})
        ]
    list_columns = ['id','description']
    label_columns = {'id':'Id','description':'Description'}

    @action("muldelete", "Delete", "Delete all?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())


appbuilder.add_view(
    CountryModelView,
    "Country Model View",
    icon="fa-table",
    label=("Country"),
    category="Address",
    category_icon="fa-map-pin",
)

class CountyFipsModelView(ModelView):
#             resource_name = "county_fips"
    datamodel = SQLAInterface(CountyFips)
#             allow_browser_login = True

    show_fieldsets = [
            (
                'County Fips',
                {'fields': ['code','place_name']})
        ]
    list_columns = ['code','place_name']
    label_columns = {'code':'Code','place_name':'Place Name'}

    @action("muldelete", "Delete", "Delete all?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())

appbuilder.add_view(
    CountyFipsModelView,
    "County Fips Model View",
    icon="fa-table",
    label=("County Fips"),
    category="Address",
    category_icon="fa-map-pin",
)

class PersonAddressModelView(ModelView):
#             resource_name = "person_address"
    datamodel = SQLAInterface(PersonAddress)
#             allow_browser_login = True

    show_fieldsets = [
            (
                'Person Address',
                {'fields': ['id','person_id','address_type_id', 'address_id','start_date','end_date','preferred_address_indicator']})
        ]
    list_columns = ['id','person_id','address_type_id', 'address_id','start_date','end_date','preferred_address_indicator']
    label_columns = {'id':'Id','person_id':'Person Id','address_type_id':'Address Type Id','address_id':'Address Id', 'start_date':'Start Date','end_date':'End Date','preferred_address_indicator':'Preferred Address Indicator'}
    add_columns = ['person_id','address_type_id', 'address_id','start_date','end_date','preferred_address_indicator']
    edit_columns = ['person_id','address_type_id', 'address_id','start_date','end_date','preferred_address_indicator']
    
    @action("muldelete", "Delete", "Delete all?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())

appbuilder.add_view(
    PersonAddressModelView,
    "Person Address Model View",
    icon="fa-table",
    label=("Person Address"),
    category="Address",
    category_icon="fa-map-pin",
)

class AddressTypeModelView(ModelView):
#             resource_name = "address_type"
    datamodel = SQLAInterface(AddressType)
#             allow_browser_login = True

    show_fieldsets = [
            (
                'Address Type',
                {'fields': ['id','description']})
        ]
    list_columns = ['id','description']
    label_columns = {'id':'Id','description':'Description'}

    @action("muldelete", "Delete", "Delete all?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())
        
appbuilder.add_view(
    AddressTypeModelView,
    "Address Type Model View",
    icon="fa-table",
    label=("Address Type"),
    category="Address",
    category_icon="fa-map-pin",
)

class PharmacyAddressModelView(ModelView):
#             resource_name = "pharmacy_address"
    datamodel = SQLAInterface(PharmacyAddress)
#             allow_browser_login = True

    show_fieldsets = [
            (
                'Pharmacy Address',
                {'fields': ['id','pharmacy_id','address_type_id','address_id','start_date','end_date','preferred_address_indicator']})
        ]
    list_columns = ['id','pharmacy_id','address_type_id','address_id','start_date','end_date','preferred_address_indicator']
    label_columns = {'id':'Id','pharmacy_id':'Pharmacy Id','address_type_id':'Address Type Id','address_id':'Address Id','start_date':'Start Date','end_date':'End Date','preferred_address_indicator':'Preferred Address Indicator'}

    @action("muldelete", "Delete", "Delete all?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())
        
appbuilder.add_view(
    PharmacyAddressModelView,
    "Pharmacy Address Model View",
    icon="fa-table",
    label=("Pharmacy Address"),
    category="Pharmacy",
    category_icon="fa-adjust",
)
#
#class PrescriptionModelView(ModelView):
##           resource_name = "prescription"
#             datamodel = SQLAInterface(Prescription)
##           allow_browser_login = True
#
#appbuilder.add_view(
#    PrescriptionModelView,
#    "Prescription Model View",
#    icon="fa-table",
#    label=("Prescription"),
#    category="Clutch",
#    category_icon="fa-cogs",
#)

class PrescriptionStatusModelView(ModelView):
#             resource_name = "prescription_status"
    datamodel = SQLAInterface(PrescriptionStatus)
#             allow_browser_login = True

    show_fieldsets = [
            (
                'Prescription Status',
                {'fields': ['id','description']})
        ]
    list_columns = ['id','description']
    label_columns = {'id':'Id','description':'Description'}

    @action("muldelete", "Delete", "Delete all?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())

appbuilder.add_view(
    PrescriptionStatusModelView,
    "Prescription Status Model View",
    icon="fa-table",
    label=("Prescription Status"),
    category="Prescription/Drug",
    category_icon="fa-adjust",
)

class PrescriptionPharmacyPricesModelView(ModelView):
#             resource_name = "prescription_pharmacy_prices"
    datamodel = SQLAInterface(PrescriptionPharmacyPrices)
#             allow_browser_login = True

    show_fieldsets = [
            (
                'Prescription Pharmacy Prices',
                {'fields': ['id','prescription_id','pharmacy_id','drug_id','price','distance','unit_of_measure_id','selected','points',]})
        ]
    list_columns = ['id','prescription_id','pharmacy_id','drug_id','price','distance','unit_of_measure_id','selected','points']
    label_columns = {'id':'Id','prescription_id':'Prescription Id','pharmacy_id':'Pharmacy Id','drug_id':'Drug Id','price':'Price','distance':'Distance','unit_of_measure_id':'Unit of Measure Id','selected':'Selected','points':'Points'}
    add_columns = ['prescription_id','pharmacy_id','drug_id','price','distance','unit_of_measure_id','selected','points']
    edit_columns = ['prescription_id','pharmacy_id','drug_id','price','distance','unit_of_measure_id','selected','points']

    @action("muldelete", "Delete", "Delete all?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())

appbuilder.add_view(
    PrescriptionPharmacyPricesModelView,
    "Prescription Pharmacy Prices Model View",
    icon="fa-table",
    label=("Prescription Pharmacy Prices"),
    category="Prescription/Drug",
    category_icon="fa-adjust",
)

class UnitOfMeasureModelView(ModelView):
#             resource_name = "unit_of_measure"
    datamodel = SQLAInterface(UnitOfMeasure)
#             allow_browser_login = True

    show_fieldsets = [
            (
                'Unit of Measure',
                {'fields': ['id','description']})
        ]
    list_columns = ['id','description']
    label_columns = {'id':'Id','description':'Description'}

    @action("muldelete", "Delete", "Delete all?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())
        
appbuilder.add_view(
    UnitOfMeasureModelView,
    "Unit of Measure Model View",
    icon="fa-table",
    label=("Unit of Measure"),
    category="Prescription/Drug",
    category_icon="fa-adjust",
)

class DrugModelView(ModelView):
#             resource_name = "drug"
    datamodel = SQLAInterface(Drug)
#             allow_browser_login = True
    show_fieldsets = [
            ('Drugs',
                {'fields': ['id','ndc','drug_name','description','product_code','qualifier','strength_value','strength_form_code', 'strength_unit_of_measure', 'controller_substance_class', 'dea_schedule_code']}
    
           )
        ]
    list_columns = ['id','ndc','drug_name','description','product_code','qualifier','strength_value','strength_form_code', 'strength_unit_of_measure', 'controller_substance_class', 'dea_schedule_code']
    #column_list = ['id','ndc','drug_name','description','product_code','qualifier','strength_value','strength_form_code', 'strength_unit_of_measure', 'controller_substance_class', 'dea_schedule_code']
    label_columns = {'id':'Id','ndc':'Ndc','drug_name':'Drug Name','description':'Description','product_code':'Product Code','qualifier':'Qualifier','strength_value':'Strength Value','strength_form_code':'Strength Form Code', 'strength_unit_of_measure':'Strength Unit of Measure', 'controller_substance_class':'Controller Substance Class', 'dea_schedule_code':'Dea Schedule Code'}
    @action("muldelete", "Delete", "Delete all?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())


appbuilder.add_view(
    DrugModelView,
    "Drug Model View",
    icon="fa-table",
    label=("Drug"),
    category="Prescription/Drug",
    category_icon="fa-adjust",
)

#class PharmacyDrugModelView(ModelView):
#             resource_name = "pharmacy_drug"
#             datamodel = SQLAInterface(PharmacyDrug)
#             allow_browser_login = True

#appbuilder.add_view(
#    PharmacyDrugModelView,
#    "Pharmacy Drug Model View",
#    icon="fa-table",
#    label=("Pharmacy Drug"),
#    category="Pharmacy",
#    category_icon="fa-cogs",
#)

#class OrphanedPrescriptionModelView(ModelView):
##           resource_name = "orphaned_prescription"
#             datamodel = SQLAInterface(OrphanedPrescription)
##           allow_browser_login = True
#
#appbuilder.add_view(
#    OrphanedPrescriptionModelView,
#    "Orphaned Prescription Model View",
#    icon="fa-table",
#    label=("Orphaned Prescription"),
#    category="Clutch",
#    category_icon="fa-cogs",
#)

#class PrescriberModelView(ModelView):
##           resource_name = "prescriber"
#             datamodel = SQLAInterface(Prescriber)
##           allow_browser_login = True
#
#appbuilder.add_view(
#    PrescriberModelView,
#    "Prescriber Model View",
#    icon="fa-table",
#    label=("Prescriber"),
#    category="Clutch",
#    category_icon="fa-cogs",
#)

class PharmacyModelView(ModelView):
#             resource_name = "pharmacy"
    datamodel = SQLAInterface(Pharmacy)
#             allow_browser_login = True
    show_fieldsets = [
            (
                'Pharmacies',
                {'fields': ['id','npi','ncpdp_id','name','primary_phone_number','fax_number']}
           
           )
        ]
    list_columns = ['npi','ncpdp_id','name','primary_phone_number','fax_number']
    #column_list = ['npi','ncpdp_id','name','primary_phone_number','fax_number']
    label_columns = {'id':'Id','npi':'Npi','ncpdp_id':'Ncpdp Id','name':'Name','primary_phone_number':'Primary Phone Number','fax_number':'Fax Number'}
    @action("muldelete", "Delete", "Delete all?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())


appbuilder.add_view(
    PharmacyModelView,
    "Pharmacy Model View",
    icon="fa-table",
    label=("Pharmacy"),
    category="Pharmacy",
    category_icon="fa-adjust",
)

class PharmacyGroupModelView(ModelView):
#             resource_name = "pharmacy_group"
    datamodel = SQLAInterface(PharmacyGroup)
#             allow_browser_login = True

    show_fieldsets = [
            (
                'Pharmacy Group',
                {'fields': ['id','group_name']})
        ]
    list_columns = ['id','group_name']
    label_columns = {'id':'Id','group_name':'Group Name'}

    @action("muldelete", "Delete", "Delete all?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())

appbuilder.add_view(
    PharmacyGroupModelView,
    "Pharmacy Group Model View",
    icon="fa-table",
    label=("Pharmacy Group"),
    category="Pharmacy",
    category_icon="fa-adjust",
)

class PharmacyMemberModelView(ModelView):
#             resource_name = "pharmacy_member"
    datamodel = SQLAInterface(PharmacyMember)
#             allow_browser_login = True

    show_fieldsets = [
            (
                'Pharmacy Member',
                {'fields': ['id','pharmacy_id','person_id','fraxses_user_code']})
        ]
    list_columns = ['id','pharmacy_id','person_id','fraxses_user_code']
    label_columns = {'id':'Id','pharmacy_id':'Pharmacy Id','person_id':'Person Id','fraxses_user_code':'Fraxses User Code'}

    @action("muldelete", "Delete", "Delete all?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())
        
appbuilder.add_view(
    PharmacyMemberModelView,
    "Pharmacy Member Model View",
    icon="fa-table",
    label=("Pharmacy Member"),
    category="Pharmacy",
    category_icon="fa-adjust",
)

class NfiItgModelView(ModelView):
#             resource_name = "nfi_itg"
    datamodel = SQLAInterface(NfiItg)
#             allow_browser_login = True

    show_fieldsets = [
            (
                'Nfi Itg',
                {'fields': ['nfi_itg_nme','nfi_itg_des']})
        ]
    list_columns = ['nfi_itg_nme','nfi_itg_des']
    label_columns = {'nfi_itg_nme':'Nfi Itg Name','nfi_itg_des':'Nfi Itg Description'}

    @action("muldelete", "Delete", "Delete all?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())
        
appbuilder.add_view(
    NfiItgModelView,
    "Nfi Itg Model View",
    icon="fa-table",
    label=("Nfi Itg"),
    category="Prescription/Drug",
    category_icon="fa-adjust",
)

class NfiItgTrgReqModelView(ModelView):
#             resource_name = "nfi_itg_trg_req"
    datamodel = SQLAInterface(NfiItgTrgReq)
#             allow_browser_login = True

    show_fieldsets = [
            (
                'Nfi Itg Trg Req',
                {'fields': ['nfi_trg_nbr','nfi_itg_nme','nfi_dta_src','str_dte','end_dte','stt_cde','req_met','req_url','req_msg','rsp_msg','rsp_cde','req_par','ent_cde','ent_id','atm_cnt']})
        ]
    list_columns = ['nfi_trg_nbr','nfi_itg_nme','nfi_dta_src','str_dte','end_dte','stt_cde','req_met','req_url','req_msg','rsp_msg','rsp_cde','req_par','ent_cde','ent_id','atm_cnt']
    label_columns = {'nfi_trg_nbr':'Nfi Trg Nbr','nfi_itg_nme':'Nfi Itg Name','nfi_dta_src':'Nfi Data Source','str_dte':'Start Date','end_dte':'End Date','stt_cde':'Stt Cde','req_met':'Request Met','req_url':'Request Url','req_msg':'Request Message','rsp_msg':'Response Message','rsp_cde':'Response Code','req_par':'Req Par','ent_cde':'Ent Cde','ent_id':'Ent Id','atm_cnt':'Atm Cnt'}

    add_exclude_columns = ['req_msg_json', 'rsp_msg_json', 'req_hed']
    edit_exclude_columns = ['req_msg_json', 'rsp_msg_json', 'req_hed']
    search_exclude_columns = ['req_msg_json', 'rsp_msg_json', 'req_hed']

    @action("muldelete", "Delete", "Delete all?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())
        
appbuilder.add_view(
    NfiItgTrgReqModelView,
    "Nfi Itg Trg Req Model View",
    icon="fa-table",
    label=("Nfi Itg Trg Req"),
    category="Prescription/Drug",
    category_icon="fa-adjust",
)

#class PrescriptionFullViewModelView(ModelView):
#             datamodel = SQLAInterface(PrescriptionFullView)
#
#appbuilder.add_view(
#    PrescriptionFullViewModelView,
#    "Prescription Full View Model View",
#    icon="fa-table",
#    label=("Prescription Full View"),
#    category="Clutch",
#    category_icon="fa-cogs",
#)   
#
#class PrescriberFullViewModelView(ModelView):
#             datamodel = SQLAInterface(PrescriberFulView)
#
#appbuilder.add_view(
#    PrescriberFullViewModelView,
#    "Prescriber Full View Model View",
#    icon="fa-table",
#    label=("Prescriber Full View"),
#    category="Clutch",
#    category_icon="fa-cogs",
#)   

#class PersonModelView(ModelView):
#    datamodel = SQLAInterface(Person)
##           related_views = [EthnicityModelView]
#    show_fieldsets = [
#            (
#                'Person',
#                {'fields': ['title.description''first_name','middle_name','last_name','suffix.description','preferred_name','email_address','date_of_birth']}
#            ),
#            (
#                'Person Details', {'fields': ['home_telephone_number', 'office_number', 'office_extension', 'fax_number', 'mobile_number', 'identity_type.description', 'identity_number', 'weight_kg', 'height_meter', 'dependent']}),
#            (
#                'Person Demographics', {'fields': ['sex.description', 'race.description', 'ethnicity.description', 'marital_status.description', 'job_title.description', 'language.description']})
#        ]
#    list_columns = ['title.description', 'first_name','middle_name','last_name','suffix.description','preferred_name','email_address', 'date_of_birth']
#    #column_list = ['id','title.description','initials','first_name','middle_name','last_name','suffix.description','preferred_name','email_address', 'home_telephone_number', 'office_number', 'office_extension', 'fax_number', 'mobile_number', 'sex.description', 'race.description', 'ethnicity.description', 'marital_status.description', 'identity_type.description', 'identity_number', 'date_of_birth', 'job_title.description', 'language.description', 'weight_kg', 'height_meter', 'dependant']
#    label_columns = {'id':'Id','title.description':'Title','initials':'Initials','first_name':'First Name','middle_name':'Middle Name','last_name':'Last Name','suffix.description':'Suffix','preferred_name':'Preferred Name','email_address':'Email Address','home_telephone_number':'Home Telephone Number', 'office_number':'Office Number', 'office_extension':'Office Extension', 'fax_number':'Fax Number', 'mobile_number':'Mobile Number', 'sex.description':'Sex', 'race.description':'Race', 'ethnicity.description':'Ethnicity', 'marital_status.description':'Marital Status', 'identity_type.description':'Identity Type', 'identity_number':'Identity Number', 'date_of_birth':'Date of Birth', 'job_title.description':'Job Title', 'language.description':'Language', 'weight_kg':'Weight kg', 'height_meter':'Height meter', 'dependant':'Dependant'}
#    
#    #label_columns = {'id':'Company User Id','users.first_name':'First Name','users.last_name':'Last Name','users.date_of_birth':'Date of Birth','covid_risk_category':'Covid Risk Category'}
#    
#    @action("muldelete", "Delete", "Delete all?", "fa-rocket")
#    def muldelete(self, items):
#        if isinstance(items, list):
#            self.datamodel.delete_all(items)
#            self.update_redirect()
#        else:
#            self.datamodel.delete(items)
#        return redirect(self.get_redirect())
#
#
#
#appbuilder.add_view(
#    PersonModelView,
#    "Person Model View",
#    icon="fa-table",
#    label=("Person"),
#    category="MDM",
#    category_icon="fa-table",
#)    
#


class PrescriptionModelView(ModelView):
#             resource_name = "prescription"
    datamodel = SQLAInterface(Prescription)
#             allow_browser_login = True
    show_fieldsets = [
            (
                'Prescription Details',
                {'fields': ['id', 'rx_new_nfi_trg_nbr','rx_transfer_nfi_trg_nbr','rx_cancel_nfi_trg_nbr','rx_new_message_id','rx_transfer_message_id', 'rx_cancel_message_id', 'prescription_status.description', 'date_written']}
            ),
            (
                'Drug Details',
                {'fields': ['drug_id', 'prescription_pharmacy_prices.price', 'sig', 'dosage_form', 'quantity', 'unit_of_measure.description', 'refills_remaining', 'refills_authorized', 'day_supply', 'drug.ndc', 'drug.description']}
            ),
            (
               'Patient Info',
                {'fields': ['person_id', 'person.first_name', 'person.last_name', 'person.mobile_number', 'person.sex_id', 'person.date_of_birth', 'person.weight_kg', 'person.height_meter']}
            ),
            (
                'Prescriber Info',
                {'fields': ['prescriber_id', 'transferred_pharmacy_id', 'state_license_number', 'prescriber_fax_number','prescription_pharmacy_prices.pharmacy_id']}
            ),
        ]
    list_columns = ['prescription_status.description', 'date_written', 'drug.ndc', 'drug.drug_name', 'prescriber_id']
    #column_list = ['id','person_id','prescriber_id','rx_new_nfi_trg_nbr','rx_transfer_nfi_trg_nbr','rx_cancel_nfi_trg_nbr','rx_new_message_id','rx_transfer_message_id', 'rx_cancel_message_id', 'transferred_pharmacy_id', 'prescription_status.description', 'state_license_number', 'prescriber_fax_number', 'date_written', 'sig', 'dosage_form', 'quantity', 'unit_of_measure.description', 'refills_remaining', 'refills_authorized', 'day_supply', 'drug.ndc', 'drug.description', 'person.first_name', 'person.last_name', 'person.mobile_number', 'person.sex_id', 'person.date_of_birth', 'person.weight_kg', 'person.height_meter', 'prescription_pharmacy_prices.pharmacy_id']
    label_columns = {'id':'Id','person_id':'Person Id','prescriber_id':'Prescriber Id','rx_new_nfi_trg_nbr':'Rx New Nfi Trg Nbr','rx_transfer_nfi_trg_nbr':'Rx Transfer Nfi Trg Nbr','rx_cancel_nfi_trg_nbr':'Rx Cancel Nfi Trg Nbr','rx_new_message_id':'Rx New Message Id','rx_transfer_message_id':'Rx Transfer Message Id', 'rx_cancel_message_id':'Rx Cancel Message Id', 'transferred_pharmacy_id':'Transferred Pharmacy Id', 'prescription_status.description': 'Prescription Status', 'state_license_number':'State License Number', 'prescriber_fax_number':'Prescriber Fax Number', 'date_written':'Date Written', 'sig':'Sig', 'dosage_form':'Dosage Form', 'quantity':'Quantity', 'unit_of_measure.description':'Unit of Measure', 'refills_remaining':'Refills Remaining', 'refills_authorized':'Refills Authorized', 'day_supply':'Days Supply', 'drug.ndc':'Ndc', 'drug.description':'Drug Description', 'person.first_name':'Patient First Name', 'person.last_name':'Patient Last Name', 'person.mobile_number':'Patient Mobile Number', 'person.sex_id':'Patient Sex', 'person.date_of_birth':'Patient Date of Birth', 'person.weight_kg':'Patient Weight', 'person.height_meter':'Patient Height', 'prescription_pharmacy_prices.pharmacy_id':'Pharmacy Id'}
    
    related_views = [PrescriptionPharmacyPricesModelView]
    @action("muldelete", "Delete", "Delete all?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())    
  
appbuilder.add_view(
    PrescriptionModelView,
    "Prescription Model View",
    icon="fa-table",
    label=("Prescription"),
    category="MDM",
    category_icon="fa-table",
)



class OrphanedPrescriptionModelView(ModelView):
#             resource_name = "prescription"
    datamodel = SQLAInterface(OrphanedPrescription)
#
    show_fieldsets = [
            (
                'Prescription Details',
                {'fields': ['id','drug_id','nfi_trg_nbr','matched_date','matched_by_fraxses_user_code', 'drug.name']}
           
           ),
        (
                'Drug Details',
                {'fields': ['drug.ndc', 'drug.description', 'drug.product_code', 'drug.qualifier', 'drug.strength_value', 'drug.strength_form_code', 'drug.strength_unit_of_measure_code', 'drug.controller_substance_class', 'drug.dea_schedule_code']}
           
           ),
           (
                'Person Details',
                {'fields': ['person_id','person_hash']}
           
           ),
           (
                'Prescriber Details',
                {'fields': ['prescriber_id','prescriber.npi', 'prescriber.dea_number', 'prescriber.specialty_code', 'prescriber.state_license_number']}
           
           ),
        ]
    list_columns = ['id','person_id','prescriber_id','matched_date','matched_by_fraxses_user_code','drug.name', 'person.first_name', 'person.last_name']
    #column_list = ['id','person_id','person_hash','prescriber_id','drug_id','nfi_trg_nbr','matched_date','matched_by_fraxses_user_code', 'drug.ndc', 'drug.name', 'drug.description', 'drug.product_code', 'drug.qualifier', 'drug.strength_value', 'drug.strength_form_code', 'drug.strength_unit_of_measure_code', 'drug.controller_substance_class', 'drug.dea_schedule_code', 'prescriber.npi', 'prescriber.dea_number', 'prescriber.specialty_code', 'prescriber.state_license_number']
    label_columns = {'id':'Id','person_id':'Person Id','person_hash':'Person Hash','prescriber_id':'Prescriber Id','drug_id':'Drug Id','nfi_trg_nbr':'Nfi Trg Nbr','matched_date':'Matched Date','matched_by_fraxses_user_code':'Matched by Fraxses User Code', 'drug.ndc':'Ndc', 'drug.name':'Drug Name', 'drug.description':'Drug Description', 'drug.product_code':'Product Code', 'drug.qualifier':'Drug Qualifier', 'drug.strength_value':'Drug Strength Value', 'drug.strength_form_code':'Drug Strength Form Code', 'drug.strength_unit_of_measure_code':'Drug Unit of Measure', 'drug.controller_substance_class':'Drug Controller Substance Class','drug.dea_schedule_code':'Drug Dea Schedule', 'prescriber.npi':'Prescriber Npi', 'prescriber.dea_number':'Prescriber Dea', 'prescriber.specialty_code':'Prescriber Specialty', 'prescriber.state_license_number':'Prescriber State License Number'}
    @action("muldelete", "Delete", "Delete all?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())

appbuilder.add_view(
    OrphanedPrescriptionModelView,
    "Orphan Prescription Model View",
    icon="fa-table",
    label=("Orphan Prescription"),
    category="MDM",
    category_icon="fa-table",
)


class PersonModelView(ModelView):
    datamodel = SQLAInterface(Person)
#             related_views = [EthnicityModelView]
    show_fieldsets = [
            (
                'Person',
                {'fields': ['title.description''first_name','middle_name','last_name','suffix.description','preferred_name','email_address','date_of_birth']}
            ),
            (
                'Person Details', {'fields': ['home_telephone_number', 'office_number', 'office_extension', 'fax_number', 'mobile_number', 'identity_type.description', 'identity_number', 'weight_kg', 'height_meter', 'dependent']}),
            (
                'Person Demographics', {'fields': ['sex.description', 'race.description', 'ethnicity.description', 'marital_status.description', 'job_title.description', 'language.description']})
        ]
    list_columns = ['title.description', 'first_name','middle_name','last_name','suffix.description','preferred_name','email_address', 'date_of_birth']
    #column_list = ['id','title.description','initials','first_name','middle_name','last_name','suffix.description','preferred_name','email_address', 'home_telephone_number', 'office_number', 'office_extension', 'fax_number', 'mobile_number', 'sex.description', 'race.description', 'ethnicity.description', 'marital_status.description', 'identity_type.description', 'identity_number', 'date_of_birth', 'job_title.description', 'language.description', 'weight_kg', 'height_meter', 'dependant']
    label_columns = {'id':'Id','title.description':'Title','initials':'Initials','first_name':'First Name','middle_name':'Middle Name','last_name':'Last Name','suffix.description':'Suffix','preferred_name':'Preferred Name','email_address':'Email Address','home_telephone_number':'Home Telephone Number', 'office_number':'Office Number', 'office_extension':'Office Extension', 'fax_number':'Fax Number', 'mobile_number':'Mobile Number', 'sex.description':'Sex', 'race.description':'Race', 'ethnicity.description':'Ethnicity', 'marital_status.description':'Marital Status', 'identity_type.description':'Identity Type', 'identity_number':'Identity Number', 'date_of_birth':'Date of Birth', 'job_title.description':'Job Title', 'language.description':'Language', 'weight_kg':'Weight kg', 'height_meter':'Height meter', 'dependant':'Dependant'}
    
    #label_columns = {'id':'Company User Id','users.first_name':'First Name','users.last_name':'Last Name','users.date_of_birth':'Date of Birth','covid_risk_category':'Covid Risk Category'}
    
    related_views = [PrescriptionModelView]
    @action("muldelete", "Delete", "Delete all?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())


appbuilder.add_view(
    PersonModelView,
    "Person Model View",
    icon="fa-table",
    label=("Person"),
    category="MDM",
    category_icon="fa-table",
)


class PrescriberModelView(ModelView):
#             resource_name = "prescriber"
    datamodel = SQLAInterface(Prescriber)
#             allow_browser_login = True
    show_fieldsets = [
            (
                'Prescribers',
                {'fields': ['person.first_name','person.last_name','specialty_code','dea_number','npi','person.mobile_number', 'person.fax_number', 'state_license_number']}
            )
        ]
    list_columns = ['person.first_name','person.last_name','specialty_code','dea_number','npi','person.mobile_number', 'person.fax_number', 'state_license_number']
    column_list = ['person.first_name','person.last_name','specialty_code','dea_number','npi','person.mobile_number', 'person.fax_number', 'state_license_number']
    label_columns = {'person.first_name':'First Name','person.last_name':'Last Name','specialty_code':'Specialty','dea_number':'Dea Number','npi':'Npi','person.mobile_number':'Mobile Number', 'person.fax_number':'Fax Number','state_license_number':'State License Number'}
    related_views = [PrescriptionModelView]
    
    @action("muldelete", "Delete", "Delete all?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect()) 

appbuilder.add_view(
    PrescriberModelView,
    "Prescriber Model View",
    icon="fa-table",
    label=("Prescriber"),
    category="MDM",
    category_icon="fa-table",
)

appbuilder.add_view(Documentation, "erd", category='Documentation', icon="fa-cogs", category_icon="fa-cogs")
#appbuilder.add_link("Entity Relationship Diagram", href='/documentation/erd', category='Documentation')

appbuilder.add_view_no_menu(ClientLabCorpOrderDetailsModelView)
appbuilder.add_view_no_menu(ClutchRegisterUserDBView)
#appbuilder.add_view_no_menu(ClientResultModelView)
