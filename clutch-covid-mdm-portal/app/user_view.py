from flask_appbuilder.security.views import UserDBModelView
from flask_babel import lazy_gettext
#from .views import ResultModelView

class CustomUserDBModelView(UserDBModelView):
#    related_views = [ResultModelView]

    show_template = "appbuilder/general/model/show_cascade.html"
    edit_template = "appbuilder/general/model/edit_cascade.html"

    show_fieldsets = [
        (lazy_gettext('User info'),
                     {'fields': ['username', 'active', 'roles', 'login_count','employer_code','employer']}),
        (lazy_gettext('Personal Info'),
                     {'fields': ['first_name', 'last_name', 'date_of_birth','email','phone_number','gender'], 'expanded': False}),
        (lazy_gettext('Address Info'),
                     {'fields': ['street_address','street_address_line_2','suite_apt_number','city','state','country'], 'expanded': False}),
        (lazy_gettext('Audit Info'),
                     {'fields': ['results','last_login', 'fail_login_count', 'created_on','created_by', 'changed_on', 'changed_by'], 'expanded': False}),
        ]
    user_show_fieldsets = [
        (lazy_gettext('User info'),
                     {'fields': ['username', 'active', 'roles', 'login_count','employer_code','employer']}),
        (lazy_gettext('Personal Info'),
                     {'fields': ['first_name', 'last_name', 'date_of_birth', 'email'], 'expanded': False}),
        (lazy_gettext('Address Info'),
                     {'fields':['street_address','street_address_line_2','suite_apt_number','city','state','country'], 'expanded':False})
        ]

    add_columns = [
                    'first_name',
                    'last_name',
                    'username',
                    'date_of_birth',
                    'active',
                    'email',
                    'roles',
                    'employer',
                    'employer_code',
                    'password',
                    'conf_password'
        ]

    list_columns = [
                    'first_name',
                    'last_name',
                    'username',
                    'date_of_birth',
                    'email',
                    'active',
                    'roles',
                    'employer',
                    'employer_code',
                    'results',
        ]

    edit_columns = [
                    'first_name',
                    'last_name',
                    'username',
                    'date_of_birth',
                    'active',
                    'email',
                    'roles',
                    'employer',
                    'employer_code',
                    'results',
        ]
