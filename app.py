from flask import Flask,make_response, jsonify
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
api.add_resource(Admins,'/admins')


if __name__ =='__main__':
    app.run(debug=True, port=5555)