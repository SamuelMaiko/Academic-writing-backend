from flask import Flask,make_response, jsonify,request
from flask_migrate import Migrate
from models import db, User, UserProfile, AdminPrivilege, Assignment,PrivilegeConnector
from flask_restful import Api, Resource
from flask_jwt_extended import JWTManager,create_access_token
from flask_cors import CORS
import os

app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///academic_writing.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['JWT_SECRET_KEY'] = "fehvgvhbchgvgvjhvygcvhc"
# os.environ.get("JWT_SECRET")
app.json.compact=False
jwt = JWTManager(app)
CORS(app, supports_credentials=True, origins=["http://localhost:5173","http://localhost:5174"])

migrate=Migrate(app, db)
db.init_app(app)

api=Api(app)


#/////login api____________________________________________________


class Login(Resource):
    def post(self):
        # work_id=request.form["work_id"]
        work_id=request.json.get("work_id",None)
        # password=request.form["password"]
        password=request.json.get("password",None)
        
        
        user=User.query.filter(User.work_id==work_id).first()
        # writer=Writer.query.filter(Writer.work_id==work_id).first()
        response_dict=dict()
        
        if user and user.password==password:
            
            access_token = create_access_token(identity=user.work_id)
            response_dict=dict(username=user.username,work_id=user.work_id,role=user.role,access_token=access_token)
            status_code = 200
        # elif writer and writer.password==password:
            
        #     access_token = create_access_token(identity=writer.id)
        #     response_dict=dict(username=writer.username,work_id=writer.work_id,role="Writer",access_token=access_token)
        #     status_code = 200
        else:
           response_dict=dict(error="Invalid credentials")  
           status_code = 401
                  
        response=make_response(jsonify(response_dict),status_code)
        return response
    
api.add_resource(Login,'/login')

# users ____________________________________________________
class Users(Resource):
    def get(self):
        all_users=User.query.all()
        response_list=list()
        for each_user in all_users:
            response_dict=each_user.to_dict()
            response_list.append(response_dict)
        
        response=make_response(jsonify(response_list),200)
        return response
    def post(self):
        new_user=User(work_id=request.json.get("work_id"),username=f"NewUser{request.json.get('email')}",
                        firstname=request.json.get("firstname"),lastname=request.json.get("lastname"),
                        email=request.json.get("email"),phone_number=request.json.get("phone_number"),role=request.json.get("role"),password=request.json.get("password"),
                        account_status="Active"
                        )
        new_profile=UserProfile(username=new_user.username, bio="I am a new user!", profile_url="https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_1280.png")
        db.session.add(new_user)
        new_user.user_profile=new_profile
        db.session.commit()
        response_dict=new_user.to_dict()
        response=make_response(jsonify(response_dict),200)
        return response
api.add_resource(Users,'/users')


# users by id ____________________________________________________

class UsersByID(Resource):
    def get(self,id):
        specific_user=User.query.filter(User.work_id==id).first()
        
        if specific_user:
            response_dict=specific_user.to_dict()
            status_code=200
        else:
            response_dict=dict(message="User not found")
            status_code=404
        response=make_response(jsonify(response_dict),status_code)
        return response
    def delete(self,id):
        specific_user=User.query.filter(User.work_id==id)
        specific_user2=User.query.filter(User.work_id==id).first()
        if specific_user:
            user_id = specific_user2.id
            specific_user.delete()
            
            privilege_connectors=PrivilegeConnector.query.filter(PrivilegeConnector.user_id==user_id).all()
            for each in privilege_connectors:
                db.session.delete(each)
                # each.delete()
            user_profiles=UserProfile.query.filter(UserProfile.user_id==user_id).all()
            for each in user_profiles:
                db.session.delete(each)
            
            db.session.commit()
            
            response_dict=dict(message="deleted successfully")
            response=make_response(jsonify(response_dict),200)
        else:
            response_dict=dict(error="Admin not found")
            response=make_response(jsonify(response_dict),404)
            
        return response
    
    def patch(self,id):
        specific_user=User.query.filter(User.work_id==id).first()
        
        if specific_user:
            for attr in request.json:
                setattr(specific_user,attr,request.json.get(attr))
            db.session.commit()
            response_dict=specific_user.to_dict()
            response=make_response(jsonify(response_dict),200)
        else:
            response_dict=dict(error="Admin not found")
            response=make_response(jsonify(response_dict),404)
            
        # return f"{request.json.get('phone_number')}"
        return response
api.add_resource(UsersByID,'/users/<string:id>')
        

# //////admins api____________________________________________________
class Admins(Resource):
    def get(self):
        all_admins=User.query.filter(db.or_(User.role == 'Admin', User.role == 'Main Admin')).all()
        
        response_list=list()
        for each_admin in all_admins:
            response_dict=each_admin.to_dict()
            response_list.append(response_dict)
            
        response=make_response(jsonify(response_list),200)
        return response
    def post(self):
        new_admin=User(work_id=request.form["work_id"],username=request.form["username"],
                        firstname=request.form["firstname"],lastname=request.form["lastname"],
                        email=request.form["email"],role="Admin",password=request.form["password"],
                        account_status=request.form["account_status"]
                        )
        db.session.add(new_admin)
        db.session.commit()
        response_dict=new_admin.to_dict()
        response=make_response(jsonify(response_dict),200)
        return response
        
api.add_resource(Admins,'/admins')



# ////////admins by id api__________________________________________
class AdminsById(Resource):
    
    def get(self,work_id):
        specific_admin=User.query.filter(db.and_(User.work_id==work_id,db.or_( User.role=="Main Admin",User.role=="Admin"))).first()
        
        if specific_admin:
            response_dict=specific_admin.to_dict()
            response=make_response(jsonify(response_dict),200)
        else:
            response_dict=dict(error="Admin not found")
            response=make_response(jsonify(response_dict),404)
        
        return response
    
    def delete(self,work_id):
        specific_admin=User.query.filter(db.and_(User.work_id==work_id,db.or_( User.role=="Main Admin",User.role=="Admin")))
        if specific_admin:
            specific_admin.delete()
            privilege_connectors=PrivilegeConnector.query.filter(PrivilegeConnector.user_id==work_id).all()
            for each in privilege_connectors:
                each.delete()
            db.session.commit()
            
            response_dict=dict(message="deleted successfully")
            response=make_response(jsonify(response_dict),200)
        else:
            response_dict=dict(error="Admin not found")
            response=make_response(jsonify(response_dict),404)
            
        return response
    
    def patch(self,work_id):
        specific_admin=User.query.filter(db.and_(User.work_id==work_id,db.or_( User.role=="Main Admin",User.role=="Admin"))).first()
        
        if specific_admin:
            for attr in request.form:
                setattr(specific_admin,attr,request.form[attr])
            db.session.commit()
            response_dict=specific_admin.to_dict()
            response=make_response(jsonify(response_dict),200)
        else:
            response_dict=dict(error="Admin not found")
            response=make_response(jsonify(response_dict),404)
            
        
        return response
    
api.add_resource(AdminsById,'/admins/<string:work_id>')



# ///////Admin privileges api__________________________________________ 
class AdminPrivileges(Resource):
    def get(self):
        all_admin_privileges=AdminPrivilege.query.all()
        
        response_list=list()
        for each_privilege in all_admin_privileges:
            response_dict=each_privilege.to_dict()
            response_list.append(response_dict)
            
            
        response=make_response(jsonify(response_list),200)
        return response
    def post(self):
        new_privilege=AdminPrivilege(privilege=request.form["privilege"],description=request.form["description"])
        
        db.session.add(new_privilege)
        db.session.commit()
        
        response_dict=new_privilege.to_dict()
        response=make_response(jsonify(response_dict),200)
        return response
    
api.add_resource(AdminPrivileges,'/admin_privileges')


# admin privileges ____________________________________________________
class AdminPrivilegesById(Resource):
    def get(self,id):
        specific_admin_privilege=AdminPrivilege.query.filter(AdminPrivilege.id==id).first()
        
        if specific_admin_privilege:
            response_dict=specific_admin_privilege.to_dict()
            response=make_response(jsonify(response_dict),200)
        else:
            response_dict=dict(error="Admin privilege not found")
            response=make_response(jsonify(response_dict),404)

        return response
    
    def delete(self,id):
        specific_admin_privilege=AdminPrivilege.query.filter(AdminPrivilege.id==id)
        
        if specific_admin_privilege:
            specific_admin_privilege.delete()
            db.session.commit()
            response_dict=dict(message="deleted successfully")
            response=make_response(jsonify(response_dict),200)
        else:
            response_dict=dict(error="Admin privilege not found")
            response=make_response(jsonify(response_dict),404)
            
        return response
    
    def patch(self,id):
        specific_admin_privilege=AdminPrivilege.query.filter(AdminPrivilege.id==id).first()
        
        if specific_admin_privilege:
            for attr in request.form:
                setattr(specific_admin_privilege,attr,request.form[attr])
                db.session.commit()
            response_dict=specific_admin_privilege.to_dict()
            response=make_response(jsonify(response_dict),200)
        else:
            response_dict=dict(error="Admin privilege not found")
            response=make_response(jsonify(response_dict),404)
        
        return response
            
        
        
api.add_resource(AdminPrivilegesById,'/admin_privileges/<int:id>')


# admin privileges ____________________________________________________
class AdminPrivilegeByUserId(Resource):
    def get(self, work_id):
        specific_user=User.query.filter(User.work_id==work_id).first()
        if specific_user:
            response_list=list()
            for each_privilege in specific_user.admin_privileges:
                response_dict=dict(id=each_privilege.id,privilege=each_privilege.privilege,description=each_privilege.description)
                response_list.append(response_dict)
            response=make_response(jsonify(response_list),200)
        else:
            response_dict=dict(error="User not found")
            response=make_response(jsonify(response_dict),404)
        
        return response
    
    def patch(self, work_id):
        privilege1=request.json.get("privilege1")
        privilege2=request.json.get("privilege2")
        privilege3=request.json.get("privilege3")
        privilege4=request.json.get("privilege4")
        privilege5=request.json.get("privilege5")
        specific_user=User.query.filter(User.work_id==work_id).first()
        
        if privilege1==True:
            admin_privilegeOne=AdminPrivilege.query.filter(AdminPrivilege.id==1).first()
            if admin_privilegeOne not in specific_user.admin_privileges:
                specific_user.admin_privileges.append(admin_privilegeOne)
                db.session.commit()
        if privilege2==True:
            admin_privilegeTwo=AdminPrivilege.query.filter(AdminPrivilege.id==2).first()
            if admin_privilegeTwo not in specific_user.admin_privileges:
                specific_user.admin_privileges.append(admin_privilegeTwo)
                db.session.commit()
        if privilege3==True:
            admin_privilegeThree=AdminPrivilege.query.filter(AdminPrivilege.id==3).first()
            if admin_privilegeThree not in specific_user.admin_privileges:
                specific_user.admin_privileges.append(admin_privilegeThree)
                db.session.commit()
        if privilege4==True:
            admin_privilegeFour=AdminPrivilege.query.filter(AdminPrivilege.id==4).first()
            if admin_privilegeFour not in specific_user.admin_privileges:
                specific_user.admin_privileges.append(admin_privilegeFour)
                db.session.commit()
        if privilege5==True:
            admin_privilegeFive=AdminPrivilege.query.filter(AdminPrivilege.id==5).first()
            if admin_privilegeFive not in specific_user.admin_privileges:
                specific_user.admin_privileges.append(admin_privilegeFive)
                db.session.commit()
            
        if privilege1==False:
            # admin_privilegeOne=AdminPrivilege.query.filter(AdminPrivilege.id==1).first()
            # for each_privilege in specific_user.admin_privileges:
                # if each_privilege.id==1:
            privilege_to_delete=PrivilegeConnector.query.filter(db.and_(PrivilegeConnector.adm_privilege_id==1,PrivilegeConnector.user_id==specific_user.id)).first()
            if privilege_to_delete:
                db.session.delete(privilege_to_delete)                
                db.session.commit()
        if privilege2==False:
            privilege_to_delete=PrivilegeConnector.query.filter(db.and_(PrivilegeConnector.adm_privilege_id==2,PrivilegeConnector.user_id==specific_user.id)).first()
            if privilege_to_delete:
                db.session.delete(privilege_to_delete)                
                db.session.commit()
        if privilege3==False:
            privilege_to_delete=PrivilegeConnector.query.filter(db.and_(PrivilegeConnector.adm_privilege_id==3,PrivilegeConnector.user_id==specific_user.id)).first()
            if privilege_to_delete:
                db.session.delete(privilege_to_delete)                
                db.session.commit()
        if privilege4==False:
            privilege_to_delete=PrivilegeConnector.query.filter(db.and_(PrivilegeConnector.adm_privilege_id==4,PrivilegeConnector.user_id==specific_user.id)).first()
            if privilege_to_delete:
                db.session.delete(privilege_to_delete)                
                db.session.commit()
        if privilege5==False:
            privilege_to_delete=PrivilegeConnector.query.filter(db.and_(PrivilegeConnector.adm_privilege_id==5,PrivilegeConnector.user_id==specific_user.id)).first()
            if privilege_to_delete:
                db.session.delete(privilege_to_delete)                
                db.session.commit()
        # else:
        response=make_response("",200)
        return response
        
    

api.add_resource(AdminPrivilegeByUserId,'/privilege_by_user_id/<string:work_id>')
# # ///////Writers api________________________________________________
class Writers(Resource):
    def get(self):
        all_writers=User.query.filter(User.role=="Writer").all()
        
        response_list=list()
        for each_writer in all_writers:
            response_dict=each_writer.to_dict()
            response_list.append(response_dict)
            
        response=make_response(jsonify(response_list),200)
        return response
    def post(self):
        new_writer=User(work_id=request.form["work_id"],username=request.form["username"],
                        firstname=request.form["firstname"],lastname=request.form["lastname"],
                        email=request.form["email"],account_status="Active",password=request.form["password"],
                        role="Writer"
                        )
        db.session.add(new_writer)
        db.session.commit()
        response_dict=new_writer.to_dict()
        response=make_response(jsonify(response_dict),200)
        return response
        
api.add_resource(Writers,'/writers')


# //////writers by id api___________________________________________
class WritersById(Resource):
    
    def get(self,work_id):
        specific_writer=User.query.filter(db.and_(User.work_id==work_id, User.role=="Writer")).first()
        
        if specific_writer:
            response_dict=specific_writer.to_dict()
            response=make_response(jsonify(response_dict),200)
        else:
            response_dict=dict(error="Writer not found")
            response=make_response(jsonify(response_dict),404)
        
        return response
    
    def delete(self,work_id):
        specific_writer=User.query.filter(db.and_(User.work_id==work_id, User.role=="Writer"))
        if specific_writer:
            specific_writer.delete()
            db.session.commit()
            
            response_dict=dict(message="deleted successfully")
            response=make_response(jsonify(response_dict),200)
        else:
            response_dict=dict(error="Writer not found")
            response=make_response(jsonify(response_dict),404)
            
        return response
    
    def patch(self,work_id):
        specific_writer=User.query.filter(db.and_(User.work_id==work_id, User.role=="Writer")).first()
        
        if specific_writer:
            for attr in request.form:
                setattr(specific_writer,attr,request.form[attr])
            db.session.commit()
            response_dict=specific_writer.to_dict()
            response=make_response(jsonify(response_dict),200)
        else:
            response_dict=dict(error="Writer not found")
            response=make_response(jsonify(response_dict),404)
            
      
        return response
    
api.add_resource(WritersById,'/writers/<string:work_id>')

# assignments ____________________________________________________
class Assignments(Resource):
    def get (self):
        all_assignments=Assignment.query.all()
        
        response_list=list()
        for each_assignment in all_assignments:
            response_dict=each_assignment.to_dict()
            response_list.append(response_dict)
        
        response=make_response(jsonify(response_list),200)
        return response
    
    def post (self):
        writer_id=request.json.get("assigned_writer")
        
        if writer_id:
            new_assignment=Assignment(
                assignment_id=request.json.get("assignment_id"), title=request.json.get("title"),
                additional_info=request.json.get("additional_info"),word_count=request.json.get("word_count"),
                deadline=request.json.get("deadline"),
                personnel_status="Assigned",assignment_status="In progress",
                writer_id=request.json.get("assigned_writer"), author_id=request.json.get("author_id")
                )
        elif not writer_id:
            new_assignment=Assignment(
                assignment_id=request.json.get("assignment_id"), title=request.json.get("title"),
                additional_info=request.json.get("additional_info"),word_count=request.json.get("word_count"),
                deadline=request.json.get("deadline"),
                personnel_status="Unassigned",assignment_status="In progress",
                writer_id=request.json.get("assigned_writer"), author_id=request.json.get("author_id")
                )
        
        db.session.add(new_assignment)
        db.session.commit()
        
        response_dict=new_assignment.to_dict()
        response=make_response(jsonify(response_dict),200)
        return response
    
api.add_resource(Assignments,'/assignments')

# unassigned assignments ____________________________________________________
class UnassignedAssignments(Resource):
    def get (self):
        unassigned_assignments=Assignment.query.filter(Assignment.personnel_status=="Unassigned").all()
        
        response_list=list()
        for each_assignment in unassigned_assignments:
            response_dict=each_assignment.to_dict()
            response_list.append(response_dict)
        
        response=make_response(jsonify(response_list),200)
        return response
    
api.add_resource(UnassignedAssignments,'/unassigned_assignments')

# assigned assignments ____________________________________________________
class AssignedAssignments(Resource):
    def get (self):
        assigned_assignments=Assignment.query.filter(Assignment.personnel_status=="Assigned").all()
        
        response_list=list()
        for each_assignment in assigned_assignments:
            response_dict=each_assignment.to_dict()
            response_list.append(response_dict)
        
        response=make_response(jsonify(response_list),200)
        return response
    
api.add_resource(AssignedAssignments,'/assigned_assignments')

class AllAssignmentIds(Resource):
    def get(self):
        all_assignments=Assignment.query.all()
        
        all_IDS=[each_assignment.assignment_id for each_assignment in all_assignments]
        
        response=make_response(jsonify(all_IDS),200)
        return response
    
api.add_resource(AllAssignmentIds,'/all_assignment_ids')
        
#  userprofiles by id ____________________________________________________
class UserProfilesById(Resource):
     def get(self,id):
        specific_user=User.query.filter(User.work_id==id).first()
        
        if specific_user:
            response_dict=dict(id=specific_user.user_profile.id, bio=specific_user.user_profile.bio,
                               profile_url=specific_user.user_profile.profile_url,username=specific_user.user_profile.username
                               )
            status_code=200
        else:
            response_dict=dict(message="Profile not found")
            status_code=404
            
        response=make_response(jsonify(response_dict),200)
        return response

api.add_resource(UserProfilesById,'/user_profiles/<string:id>')
        
                
# deactivate user account  ____________________________________________________

class UserDeactivation(Resource):
    def patch(self,work_id):
        specific_user=User.query.filter(User.work_id==work_id).first()
        
        if specific_user:
            setattr(specific_user,"account_status","Deactivated")
            db.session.commit()
            response_dict=""
            status_code=204
        else:
            response_dict=dict(error="User not found")
            status_code=404
            
        response=make_response(jsonify(response_dict),status_code)
        return response
    
api.add_resource(UserDeactivation,'/deactivate_user/<string:work_id>')
# activate user account  ____________________________________________________

class UserActivation(Resource):
    def patch(self,work_id):
        specific_user=User.query.filter(User.work_id==work_id).first()
        
        if specific_user:
            setattr(specific_user,"account_status","Active")
            db.session.commit()
            response_dict=dict(message="User activated",work_id=specific_user.work_id)
            status_code=200
        else:
            response_dict=dict(error="User not found")
            status_code=404
            
        response=make_response(jsonify(response_dict),status_code)
        return response

api.add_resource(UserActivation,'/activate_user/<string:work_id>')


if __name__ =='__main__':
    with app.app_context():
        app.run(debug=True, port=5555)