from . import appbuilder, db
from .models import RequisitionManifest
import pandas as pd 

kits_not_shipped = pd.read_csv('app/kits.csv', header=None)

kits_shipped = pd.read_csv('app/kits_shipped.csv', header=None)

#db.session.execute('TRUNCATE TABLE requisition_manifest')

def kits_shipped_fill():
    for i in kits_shipped[0]:
        try:
            db.session.add(RequisitionManifest(requisition_number=i, tracking_number='KIT SHIPPED'))
            db.session.commit()
        except Exception as e:
            print(str(e))
            db.session.rollback()

def manifest_fill():
    for i in kits_not_shipped[0]:
        try:
            db.session.add(RequisitionManifest(requisition_number=i))
            db.session.commit()
        except Exception as e:
            print(str(e))
            db.session.rollback()
