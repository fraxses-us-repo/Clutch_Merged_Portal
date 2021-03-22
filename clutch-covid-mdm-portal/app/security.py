from flask_appbuilder.security.sqla.manager import SecurityManager
from .models import CustomUser, CustomRegisterUser
from .user_view import CustomUserDBModelView
from flask_appbuilder.security.views import UserInfoEditView
from .user_form import UserInfoEdit
from .user_register import CustomRegisterUserDBView
#from .index import MyIndexView
from werkzeug.security import check_password_hash, generate_password_hash
import uuid
import logging

log = logging.getLogger(__name__)

class CustomUserInfoEditView(UserInfoEditView):
    form = UserInfoEdit

class CustomSecurityManager(SecurityManager):

    def add_register_user(
                    self, username, first_name, last_name, email, gender, street_address, street_address_line_2, suite_apt_number, city, state, country, phone_number, date_of_birth, general_informed_consent, hipaa_authorization, employer_code, password="", hashed_password=""
                        ):
        register_user = self.registeruser_model()
        register_user.username = username
        register_user.email = email
        register_user.first_name = first_name
        register_user.last_name = last_name
        register_user.gender = gender
        register_user.street_address = street_address
        register_user.street_address_line_2 = street_address_line_2
        register_user.suite_apt_number = suite_apt_number
        register_user.city = city
        register_user.state = state
        register_user.country = country
        register_user.phone_number = phone_number
        register_user.date_of_birth = date_of_birth
        register_user.general_informed_consent_id = general_informed_consent
        register_user.hipaa_authorization_id = hipaa_authorization
        register_user.employer_code = employer_code
        if hashed_password:
            register_user.password = hashed_password
        else:
            register_user.password = generate_password_hash(password)
        register_user.registration_hash = str(uuid.uuid1())
        try:
            self.get_session.add(register_user)
            self.get_session.commit()
            return register_user
        except Exception as e:
            log.error(str(e))
            self.appbuilder.get_session.rollback()
            return None
    # index_view = MyIndexView
    registeruser_model = CustomRegisterUser
    user_model = CustomUser
    userdbmodelview = CustomUserDBModelView
    userinfoeditview = CustomUserInfoEditView
    registeruserdbview = CustomRegisterUserDBView
