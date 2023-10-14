from flask import Flask,make_response, jsonify,request
from flask_migrate import Migrate
from models import db, Admin, Writer, AdminPrivilege, Assignment,PrivilegeConnector
from flask_restful import Api, Resource

app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///academic_writing.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.json.compact=False

migrate=Migrate(app, db)
db.init_app(app)

api=Api(app)


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

class AdminsById(Resource):
    
    def get(self,id):
        specific_admin=Admin.query.filter(Admin.id==id).first()
        
        if specific_admin:
            response_dict=specific_admin.to_dict()
            response=make_response(jsonify(response_dict),200)
        else:
            response_dict=dict(message="Admin does not exist")
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
            response_dict=dict(message="Admin does not exist")
            response=make_response(jsonify(response_dict),404)
            
        return response
    
    def patch(self,id):
        specific_admin=Admin.query.filter(Admin.id==id).first()
        
        if specific_admin:
            for attr in request.form:
                setattr(specific_admin,attr,request.form[attr])
        else:
            response_dict=dict(message="Admin does not exist")
            response=make_response(jsonify(response_dict),404)
            
        db.session.commit()
        
        response_dict=specific_admin.to_dict()
        response=make_response(jsonify(response_dict),200)
        return response
    
api.add_resource(AdminsById,'/admins/<int:id>')


class AdminPrivileges(Resource):
    def get(self):
        all_admin_privileges=AdminPrivilege.query.all()
        
        response_list=list()
        for each_privilege in all_admin_privileges:
            response_dict=each_privilege.to_dict()
            response_list.append(response_dict)
            
            
        response=make_response(jsonify(response_list),200)
        return response
    
api.add_resource(AdminPrivileges,'/privileges')
        
        

if __name__ =='__main__':
    app.run(debug=True, port=5555)