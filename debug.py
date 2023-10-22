from models import db, User, AdminPrivilege, Assignment,PrivilegeConnector
from app import app

with app.app_context():
    # work=AdminPrivilege.query.filter(AdminPrivilege.id==1).first()
    # print(work.users)
    # main_admin=AdminPrivilege.query.filter(AdminPrivilege.id==5).first()
    # print(main_admin.users)
    # AdminPrivilege.query.filter(AdminPrivilege.id>5).delete()
    # PrivilegeConnector.query.filter(PrivilegeConnector.id==12).delete()
    # db.session.commit()
    # for each in main_admin.admin_privileges:
    #     print(each.to_dict())
    # new_privilege=PrivilegeConnector(id=11, adm_privilege_id=2,user_id=22)
    # db.session.add(new_privilege)
    PrivilegeConnector.query.filter(PrivilegeConnector.id>11).delete()
    db.session.commit()
    
   