from flask import Flask,make_response, jsonify,request
from flask_migrate import Migrate
from models import db, Admin, Writer, AdminPrivilege, Assignment,PrivilegeConnector
from flask_restful import Api, Resource
from flask_jwt_extended import JWTManager,create_access_token

app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///academic_writing.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['JWT_SECRET_KEY'] = 'el.wan_x447'
app.json.compact=False
jwt = JWTManager(app)

migrate=Migrate(app, db)
db.init_app(app)

api=Api(app)


#/////login and register api


class Login(Resource):
    def post(self):
        work_id=request.form["work_id"]
        password=request.form["password"]
        
        
        admin=Admin.query.filter(Admin.work_id==work_id).first()
        writer=Writer.query.filter(Writer.work_id==work_id).first()
        response_dict=dict()
        
        if admin and admin.password==password:
            
            access_token = create_access_token(identity=admin.id)
            response_dict=dict(username=admin.username,work_id=admin.work_id,role=admin.role,access_token=access_token)
            status_code = 200
        elif writer and writer.password==password:
            
            access_token = create_access_token(identity=writer.id)
            response_dict=dict(username=writer.username,work_id=writer.work_id,role="Writer",access_token=access_token)
            status_code = 200
        else:
           response_dict=dict(error="Invalid credentials")  
           status_code = 401
                  
        response=make_response(jsonify(response_dict),status_code)
        return response
    
api.add_resource(Login,'/login')





# //////admins api
class Admins(Resource):
    def get(self):
        all_admins=Admin.query.all()
        
        response_list=list()
        for each_admin in all_admins:
            response_dict=each_admin.to_dict()
            response_list.append(response_dict)
            
        response=make_response(jsonify(response_list),200)
        return response
    def post(self):
        new_admin=Admin(work_id=request.form["work_id"],username=request.form["username"],
                        firstname=request.form["firstname"],lastname=request.form["lastname"],
                        email=request.form["email"],control_status="Admin",password=request.form["password"])
        db.session.add(new_admin)
        db.session.commit()
        response_dict=new_admin.to_dict()
        response=make_response(jsonify(response_dict),200)
        return response
        
api.add_resource(Admins,'/admins')



# ////////admins by id api
class AdminsById(Resource):
    
    def get(self,id):
        specific_admin=Admin.query.filter(Admin.id==id).first()
        
        if specific_admin:
            response_dict=specific_admin.to_dict()
            response=make_response(jsonify(response_dict),200)
        else:
            response_dict=dict(error="Admin not found")
            response=make_response(jsonify(response_dict),404)
        
        return response
    
    def delete(self,id):
        specific_admin=Admin.query.filter(Admin.id==id)
        if specific_admin:
            specific_admin.delete()
            db.session.commit()
            
            response_dict=dict(message="deleted successfully")
            response=make_response(jsonify(response_dict),200)
        else:
            response_dict=dict(error="Admin not found")
            response=make_response(jsonify(response_dict),404)
            
        return response
    
    def patch(self,id):
        specific_admin=Admin.query.filter(Admin.id==id).first()
        
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
    
api.add_resource(AdminsById,'/admins/<int:id>')



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



# ///////Writers api
class Writers(Resource):
    def get(self):
        all_writers=Writer.query.all()
        
        response_list=list()
        for each_writer in all_writers:
            response_dict=each_writer.to_dict()
            response_list.append(response_dict)
            
        response=make_response(jsonify(response_list),200)
        return response
    def post(self):
        new_writer=Writer(work_id=request.form["work_id"],username=request.form["username"],
                        firstname=request.form["firstname"],lastname=request.form["lastname"],
                        email=request.form["email"],account_status="Active",password=request.form["password"])
        db.session.add(new_writer)
        db.session.commit()
        response_dict=new_writer.to_dict()
        response=make_response(jsonify(response_dict),200)
        return response
        
api.add_resource(Writers,'/writers')


# //////writers by id api
class WritersById(Resource):
    
    def get(self,id):
        specific_writer=Writer.query.filter(Writer.id==id).first()
        
        if specific_writer:
            response_dict=specific_writer.to_dict()
            response=make_response(jsonify(response_dict),200)
        else:
            response_dict=dict(error="Writer not found")
            response=make_response(jsonify(response_dict),404)
        
        return response
    
    def delete(self,id):
        specific_writer=Writer.query.filter(Writer.id==id)
        if specific_writer:
            specific_writer.delete()
            db.session.commit()
            
            response_dict=dict(message="deleted successfully")
            response=make_response(jsonify(response_dict),200)
        else:
            response_dict=dict(error="Writer not found")
            response=make_response(jsonify(response_dict),404)
            
        return response
    
    def patch(self,id):
        specific_writer=Writer.query.filter(Writer.id==id).first()
        
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
    
api.add_resource(WritersById,'/writers/<int:id>')



if __name__ =='__main__':
    app.run(debug=True, port=5555)