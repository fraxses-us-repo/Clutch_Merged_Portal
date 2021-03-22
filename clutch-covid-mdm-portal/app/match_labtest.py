from .models import LabCorpOrderDetails, Result, CustomUser, assoc_user_result
import logging
from flask import render_template

try :
    from . import appbuilder, db, mail, app
except:
    from . import appbuilder, db, app


log = logging.getLogger(__name__)

def flat_list(l):
    return ["%s" % v for v in l]

def send_email(user):
    #user = db.session.query(CustomUser).get(user)
    try:
        from flask_mail import Mail, Message
    except Exception:
        log.error("Install Flask-Mail to use User registration")
        return False
    mail = Mail(appbuilder.get_app)
    with app.app_context():
        msg = Message()
        msg.subject = 'Clutch Diagnostics Lab Test'
        msg.html = render_template('labtest_notification.html')
        msg.recipients = [user.email]
        try:
            mail.send(msg)
        except Exception as e:
            log.error("Send email exception: {0}".format(str(e)))
            return False
    return True



def add_matched_user(labcorp_order_details_id, created_by_fk, requisition_number):
    try:
        statement = assoc_user_result.insert().values(labcorp_order_details_id=labcorp_order_details_id, custom_user_id=created_by_fk)
        db.session.execute(statement)
        db.session.query(Result).filter(requisition_number==requisition_number).update({Result.is_matched: True, Result.changed_by_fk:created_by_fk})
        db.session.commit()
        match = True
    except Exception as e:
        print(e)
        db.session.rollback()
        return False
    if match:
        user = db.session.query(CustomUser).get(created_by_fk)
        return send_email(user)


def match_labtests():
    try:
        unmatched_requisitions = [(r.requisition_number, r.created_by_fk) for r in db.session.query(Result).filter(Result.is_matched==False).distinct()]
        print('Found {} unmatched requisitions'.format(len(unmatched_requisitions)))
    except Exception as e:
        print(e, 'Failed to get unmatched requisitions')
        return []

    for unmatched_requisition in unmatched_requisitions:
        try:
            requisition_number = unmatched_requisition[0]
            created_by_fk = unmatched_requisition[1]
            date_of_birth = db.session.query(CustomUser).get(created_by_fk).date_of_birth
            if requisition_number is not None and date_of_birth is not None: # and first_name is not None and last_name is not None and date_of_birth is not None:
                print('Looking for {},{}'.format(requisition_number, created_by_fk))
                unmatched_results = db.session.query(Result.requisition_number).\
                                            filter(Result.is_matched == False).subquery()
                if unmatched_results != None or unmatched_results != 'None':
                    labcorp_order_details = db.session.query(LabCorpOrderDetails).\
                                            filter(LabCorpOrderDetails.control_number==str(requisition_number).upper(),
                                                   LabCorpOrderDetails.control_number.in_(unmatched_results),
                                                   LabCorpOrderDetails.date_of_birth==date_of_birth
                                                  ).first()
                    if labcorp_order_details is not None:
                        print('Matching to User')
                        users = [(r.id, r.date_of_birth, r.first_name, r.last_name) for r in db.session.query(CustomUser).\
                                                                                        filter(CustomUser.id==created_by_fk,
                                                                                               CustomUser.date_of_birth==date_of_birth
                                                                                            ).all()]
                        for matched_user in users:
                            matched_result = add_matched_user(labcorp_order_details.id, matched_user[0], labcorp_order_details.control_number)
                        return True
                    else:
                        print('Requisition has been registered but no LabCorp detail match yet found')
                else:
                    print('Requisition not found in labcorp table')
            else:
                print('Not enough information to match {}'.format(unmatched_requisition))
                return False
        except Exception as e:
            print(e, 'No match found for {}'.format(requisition_number))
            return False


