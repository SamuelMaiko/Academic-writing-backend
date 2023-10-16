from flask import Flask,make_response, jsonify,request
from flask_migrate import Migrate
from models import db, User, AdminPrivilege, Assignment,PrivilegeConnector
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


#/////login and register api


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





# //////admins api
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



# ////////admins by id api
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



# ///////Admin privileges api 
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



# # ///////Writers api
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


# //////writers by id api
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
        
            



if __name__ =='__main__':
    app.run(debug=True, port=5555)