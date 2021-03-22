import gspread
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from datetime import date, datetime

SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://fraxses:fraxses@localhost:5432/clutch_diagnostics'

engine = create_engine(SQLALCHEMY_DATABASE_URI)

covid_test_kit = 'DEV COVID Testing Kit Form'

requisition_delta = list(pd.read_sql('SELECT requisition_number FROM result WHERE cast(test_kit_sent as boolean) = {}'.format(True), con=engine)['requisition_number'])
requisition_delta_matched = list(pd.read_sql('SELECT requisition_number FROM result WHERE cast(is_matched as boolean) = {}'.format(False), con=engine)['requisition_number'])
print("Requisition data to compute delta records")

location_delta = pd.read_sql_table('location', con=engine)
print("Location data to compute delta records")
location_delta = list(location_delta['location_name'])

employer_delta = pd.read_sql_table('employer', con=engine)
print("Employer data to compute delta records")
employer_delta = list(employer_delta['employer_name'])

gc = gspread.service_account(filename='/home/austinp/fraxses-dev00-f8b6bd731cb5.json')

column_mapping_form_responses = {       u'Results Emailed':'results_emailed',
                                        u'Result Date':'result_date',
					u'First Name':'first_name',
					u'Last Name':'last_name',
					u'Date of Birth':'date_of_birth',
					u'Gender':'gender',
					u'Street Address':'street_address',
					u'Street Address Line 2':'street_address_line_2',
					u'City':'city',
					u'State / Province':'state',
                                        u'State / Province 2':'state_2',
					u'Postal / Zip Code':'zip_code',
					u'Employer Name':'employer_name',
					u'Lab Requisition Number':'requisition_number',
					u'Email':'email',
					u'Phone Number':'phone_number',
					u'E-Signature':'e_signature',
					u'HIPAA AUTHORIZATION AND CONSENT AGREEMENT':'hipaa_agreement',
                                        u'GENERAL INFORMED CONSENT AGREEMENT':'general_informed',
					u'Submission ID':'submission_id',
					u'Test Kit Sent':'test_kit_sent',
					u'FedEx Tracking #':'fedex_tracking_number',
					u'RTN Tracking #':'rtn_tracking_number',
					u'Date Created':'date_created',
                                        u'Results Emailed':'results_emailed',
					u'Date Modified':'date_modified',
                                        u'Date Entered':'date_entered',
                                        u'Country':'country'
				}

column_mapping_kits_shipped = {
        'Req Number':'requisition_number',  
        'Customer':'employer_name',    
        'Location':'location_name',    
        'Supervisor':'supervisor',  
        'Date Entered':'date_entered'
        }

print('################# FORM RESPONSES ###################')
wks1 = gc.open(covid_test_kit).get_worksheet(0)
data = wks1.get_all_values()
headers = data.pop(0)

df_form_responses = pd.DataFrame(data, columns=headers)
df_form_responses = df_form_responses.rename(columns=column_mapping_form_responses)
print('Computing users and matching requisitions')
df_form_responses = df_form_responses[[ 'last_name'
                                       #,'middle_name'
                                       ,'first_name'
                                       ,'date_of_birth'
                                       #,'patient_phone'
                                       ,'street_address'
                                       ,'street_address_line_2'
                                       #,'suite_apt_number'
                                       ,'city'
                                       ,'state'
                                       ,'state_2'
                                       ,'zip_code'
                                       ,'country'
                                       ,'date_of_birth'
                                       ,'phone_number'
                                       ,'email'
                                       ,'submission_id'
                                       #,'test_batch_number'
                                       #,'comment_section'
                                       #,'is_valid_result'
                                       #,'temperature'
                                       ,'requisition_number'
                                       #,'tracking_number'
                                       ,'test_kit_sent'
                                       ,'results_emailed'
                                       ,'result_date' 
                                       ,'gender'
                                       ,'fedex_tracking_number'
                                       ,'rtn_tracking_number'
                                       #,'ups_tracking_number'
                                       #,'is_matched'
                                       #,'test_batch_number'
                                       ]]

print('################### KITS SHIPPED ###################')
wks2 = gc.open(covid_test_kit).get_worksheet(1)
requisition_data = wks2.get_all_values()
headers = requisition_data.pop(0)

df_kits_shipped = pd.DataFrame(requisition_data, columns=headers)
df_kits_shipped = df_kits_shipped.rename(columns=column_mapping_kits_shipped)

df_requisitions_1 = df_kits_shipped[['requisition_number','supervisor','date_entered']].drop_duplicates()
df_requisitions_1 = df_requisitions_1.loc[df_requisitions_1['requisition_number'] != '']
df_requisitons_1 = df_requisitions_1.loc[~df_requisitions_1['requisition_number'].str.upper().isin(requisition_delta_matched)]
print('Computing delta requisition shipments')
with engine.connect() as connection:
    for i in df_requisitions_1.itertuples(index=False, name='Requisitions'):
        try:
            connection.execute(
                '''
                    INSERT INTO result (requisition_number,
                                        supervisor,
                                        is_matched,
                                        date_entered,
                                        test_kit_sent,
                                        created_on,
                                        changed_on,
                                        is_valid_result,
                                        test_id,
                                        created_by_fk,
                                        changed_by_fk)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ''',
                (str(i.requisition_number).upper(), str(i.supervisor), False, str(i.date_entered), True, datetime.now(), datetime.now(), True, 1, 1, 1)
            )
        except Exception as e:
            print(e)


import uuid
print("Computing delta requisitions registered")
df_requisitions_2 = df_form_responses.drop_duplicates()
df_requisitions_2 = df_requisitions_2[df_requisitions_2['requisition_number'] != '']
df_requisitions_2 = df_requisitions_2[~df_requisitions_2['requisition_number'].isin(requisition_delta)] 

with engine.connect() as connection:
    for i in df_requisitions_2.itertuples(index=False, name='Requisition'):
        try:
            connection.execute(
                    '''
                       UPDATE result SET
                                         last_name = %s
                                        ,first_name = %s
                                        ,date_of_birth = %s
                                        ,street_address = %s
                                        ,street_address_line_2 = %s
                                        ,city = %s
                                        ,state = %s
                                        ,state_2 = %s
                                        ,zip_code = %s
                                        ,country = %s
                                        ,phone_number = %s
                                        ,email = %s
                                        ,submission_id = %s
                                        ,results_emailed = %s
                                        ,result_date = %s
                                        ,gender = %s
                                        ,fedex_tracking_number = %s
                                        ,rtn_tracking_number = %s
                                        
                            where requisition_number = '{}'
                    '''.format(str(i.requisition_number).upper()),
                        ('' if i.last_name is None else i.last_name,
                         '' if i.first_name is None else i.first_name,
                         '' if i.date_of_birth is None else i.date_of_birth,
                         i.street_address,
                         i.street_address_line_2,
                         i.city,
                         i.state,
                         i.state_2,
                         i.zip_code,
                         i.country,
                         i.phone_number,
                         i.email,
                         '' if i.submission_id is None else i.submission_id,
                         False,
                         i.result_date,
                         i.gender,
                         i.fedex_tracking_number,
                         i.rtn_tracking_number),
                    )
        except Exception as e:
            print(e)

df_employer = df_kits_shipped[['employer_name']].drop_duplicates()
df_employer = df_employer.loc[df_employer['employer_name'] != '']
df_employer = df_employer.loc[~df_employer['employer_name'].isin(employer_delta)]

print('Computing delta employers')
with engine.connect() as connection:
    for i in df_employer.itertuples(index=False, name='Employer'):
        try:
            connection.execute(
                    '''
                        INSERT INTO employer (employer_name, 
                                              employer_code)
                        VALUES (%s,%s)
                    ''',
                    (i.employer_name, str(hash(i.employer_name)))
                            )
        except Exception as e:
            print(e)

df_location = df_kits_shipped[['location_name']].drop_duplicates()
df_location = df_location.loc[df_location['location_name'] != '']
df_location = df_location.loc[~df_location['location_name'].isin(location_delta)]

print("Computing delta locations")
with engine.connect() as connection:
    for i in df_location.itertuples(index=False):
        try:
            connection.execute(
                '''
                    INSERT into location (location_name, 
                                          street_address, 
                                          street_address_line_2, 
                                          suite_apt_number, 
                                          city, 
                                          state, 
                                          zip_code, 
                                          latitude, 
                                          longitude)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ''',
                    (i.location_name, '', '', '', '', '', '', None, None)
                )
        except Exception as e:
            print(e)
    


