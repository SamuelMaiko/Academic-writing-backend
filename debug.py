from models import db, Admin, Writer, AdminPrivilege, Assignment,PrivilegeConnector
from app import app

with app.app_context():
    work=AdminPrivilege.query.filter(AdminPrivilege.id==1).first()
    print(work.admins)
    # AdminPrivilege.query.filter(AdminPrivilege.id>5).delete()
    # PrivilegeConnector.query.filter(PrivilegeConnector.id==12).delete()
    # db.session.commit()
    # for each in all_admins.admin_privileges:
    #     print(each.privilege)
    
   