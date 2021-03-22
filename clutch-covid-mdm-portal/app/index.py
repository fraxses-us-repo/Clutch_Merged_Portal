from flask_appbuilder import IndexView
#from .views import EmployeeModelView
#from .user_register import CustomRegisterUserDBView
#from flask_appbuilder.security.views import UserDBModelView


class MyIndexView(IndexView):
    index_template = 'index.html'
        
    #def usersubscribe(self, item):
    #    return redirect(
    #        url_for(
    #            "SubscribeFormView.this_form_get",
    #            pk=item.id
    #                )
    #            )
                    

#class MyIndexView(EmployeeModelView):
#    pass

#class MyIndexView(CustomRegisterUserDBView):
#    pass
