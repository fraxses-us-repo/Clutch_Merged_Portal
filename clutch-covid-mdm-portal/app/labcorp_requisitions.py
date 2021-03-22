from .models import LabCorpOrderDetails, Result, CustomUser, assoc_user_result
from . import appbuilder, db, app
#from . import appbuilder, db, mail, app
import logging
import io
import pysftp
import csv
from datetime import datetime

log = logging.getLogger(__name__)

def register_labtests():
    try:
        unregistered_labtests = [(r.requisition_number, r.created_by_fk) for r in db.session.query(Result).filter(Result.is_sent_to_labcorp==False).distinct()]
        print('Found {} unsent registrations'.format(len(unregistered_labtests)))
    except Exception as e:
        print(e, 'Failed to get unmatched requisitions')
        return []
    for labtest in unregistered_labtests:
        try:
            requisition_number = labtest[0]
            created_by_fk = labtest[1]
            user = db.session.query(CustomUser).get(created_by_fk)
            labtest_registration = [{
                        'last_name':user.last_name,
                        'first_name':user.first_name,
                        'middle_name':user.middle_name,
                        'date_of_birth':user.date_of_birth,
                        'gender':'N',
                        'street_address':user.street_address,
                        'city':user.city,
		             	'state':user.state,
                        'zip_code':user.zip_code,
                        'phone_number':user.zip_code,
                        'email':user.email,
                        'race':'X',
                        'ethnicity':'U',
                        'requisition_number':requisition_number,
                        'user_id':user.id,
                        'account_name':'Clutch Atlanta',
                        'account_number': '17006615', #'10002605',
                        'bill_type':'C',
                        'physician_first_name':'Robert',
                        'physician_last_name':'Kaufman',
                        'npi':'1376573147',
                        'order_code':'139900',
                        'order_name':'SARS-CoV-2, NAA',
                        'csid':'TA013783'
                        }]
            sftp_host = 'sftp.clutch.health'
            sftp_port = '22'
            sftp_user = 'labcorp'
            sftp_password = 'dd15fa1d7377a67f23a6715878480f95'
            cnopts = pysftp.CnOpts()
            cnopts.hostkeys = None
            try:
                with pysftp.Connection(host=sftp_host, username=sftp_user, password=sftp_password,cnopts=cnopts) as sftp:
                    print("Connection succesfully established ... ")
                    sftp.cwd('/sftp/outgoing/')
                    print("Changed directory to outgoing...")
                    with sftp.open("Orders_to_Process_" + str(datetime.utcnow().strftime("%Y_%m_%d_%H:%M:%S").replace(':','_')) + '.csv', mode='wb') as file:
                        stream = io.StringIO()
                        writer = csv.writer(file)
                        writer.writerow(labtest_registration[0].values())
                        stream.seek(0)
                        file.write(stream.read())
                        print("New record was written as a csv to the sftp site successfully")
            except Exception as e:
                print(e, 'Could not write to SFTP site')
                return False
            try:
                result = db.session.query(Result).filter(Result.requisition_number==requisition_number).update({'is_sent_to_labcorp':True, 'changed_by_fk':1})   
                db.session.commit()
            except Exception as e:
                print(e, 'Could not update sent registration')
                return False
        except Exception as e:
            print(e, 'No match found for {}'.format(labtest))
            return False


