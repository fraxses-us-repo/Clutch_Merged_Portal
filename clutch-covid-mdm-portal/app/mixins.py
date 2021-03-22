import datetime
import logging
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declared_attr
import sqlalchemy.types as types


log = logging.getLogger(__name__)

class FraxsesMixin(object):

    @declared_attr
    def frx_rec_lck_ind(cls):
        return Column(Integer)

    @declared_attr
    def frx_rec_lck_dte (cls):
        return Column(DateTime)

    @declared_attr
    def frx_stt_cde(cls):
        return Column(String(50))

    @declared_attr
    def frx_hed_cde(cls):
        return Column(String(250))

    @declared_attr
    def frx_acs_org_cde(cls):
        return Column(String(50))

    @declared_attr
    def frx_acs_grp_cde(cls):
        return Column(String(50))

    @declared_attr
    def frx_acs_usr_cde(cls):
        return Column(String(50))

    @declared_attr
    def frx_rec_cre_dte(cls):
        return Column(DateTime)
        #, default=db.func.current_timestamp())

    @declared_attr
    def frx_lst_upd_dte(cls):
        return Column(DateTime)

    @declared_attr
    def acv_ind(cls):
        return Column(Integer)

