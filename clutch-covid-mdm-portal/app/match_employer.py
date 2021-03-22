from .models import CustomUser, Employer
from . import db

def flat_list(l):
    return ["%s" % v for v in l]

def add_matched_employee(user_id, employer_id):
    try:
        db.session.query(CustomUser).filter(CustomUser.id==user_id).update({CustomUser.employer_id:employer_id})
        db.session.commit()
        return True
    except Exception as e:
        print(e)
        db.session.rollback()
        return False

def match_employer():
    try:
        unmatched_employees = [(r.id, r.employer_code, r.employer_id, r.employee_id_number) for r in db.session.query(CustomUser.id, CustomUser.employer_code, CustomUser.employer_id, CustomUser.employee_id_number).filter(CustomUser.employer_id == None).distinct()]
        print('Found {} unmatched users'.format(len(unmatched_employees)))
    except Exception as e:
        print(e, 'Failed to get unmatched requisitions')
        return []

    for unmatched_employee in unmatched_employees:
        try:
            user_id = unmatched_employee[0]
            employer_code = unmatched_employee[1] 
            employer_id = unmatched_employee[2]
            employer_id_number = unmatched_employee[3]
            if employer_code is not None and user_id is not None: # and first_name is not None and last_name is not None and date_of_birth is not None:
                employer = db.session.query(Employer).filter(Employer.employer_code==employer_code).first()
                if employer is not None:
                    match = add_matched_employee(user_id, employer.id)
                    if match == True:
                        print(employer, 'matched.')
            else:
                print('Not enough information to match {}'.format(unmatched_employee))
                return False
        except Exception as e:
            print(e, 'No match found for {}'.format(unmatched_employee))
            return False


