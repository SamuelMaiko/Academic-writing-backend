from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import validates
# from sqlalchemy_serializer import SerializerMixin
import re

db=SQLAlchemy()

class User(db.Model):
    
    __tablename__='users'
    
    
    id=db.Column(db.Integer, primary_key=True)
    work_id=db.Column(db.String(255), unique=True )
    username=db.Column(db.String(255), nullable=False, unique=True )
    firstname=db.Column(db.String(255), nullable=False )
    lastname=db.Column(db.String(255), nullable=False )
    email=db.Column(db.String(255), nullable=False, unique=True)
    password=db.Column(db.String(255), nullable=False )
    role=db.Column(db.Enum('Main Admin', 'Admin','Writer'), nullable=False )
    account_status=db.Column(db.Enum('Active', 'Deactivated'), nullable=False)
    
    created_at=db.Column(db.DateTime, server_default=db.func.now() )
    updated_at=db.Column(db.DateTime, onupdate=db.func.now() )
    

    
    _privileges=db.relationship('PrivilegeConnector', backref='user')
    admin_privileges=association_proxy(
        '_privileges','adm_privilege',
        creator=lambda pr:PrivilegeConnector(adm_privilege=pr)
        )
    
    
    @validates('password')
    def validate_password(self, key, value):
        if not (8 <= len(value) <= 12) or not re.match(r'^[A-Za-z0-9]*$', value):
            raise ValueError("Password must be between 8 and 12 characters long and contain only alphanumeric characters.")
        return value
    
    @validates('role')
    def validate_role(self,key,value):
        role_options=['Main Admin', 'Admin', 'Writer']
        if value not in role_options:
            raise ValueError("Only values accepted: 'Main Admin', 'Admin' and 'Writer' ")
        
        return value
    
    @validates('work_id')
    def validate_work_id(self, key, value):
        if not (re.match(r'^A\d{4}$', value) or re.match(r'^W\d{4}$', value)):
            raise ValueError("Work ID must be in the format 'AXXXX' for admins or 'WXXXX' for writers, where XXXX is a 4-digit number.")
        return value
    
    @validates('account_status')
    def validate_account_status(self,key,value):
        account_status_options=['Active', 'Deactivated']
        if value not in account_status_options:
            raise ValueError("Only values accepted: 'Active', 'Deactivated'")
        
        return value
    
    def to_dict(self):
        model_return={
            "id":self.id ,
            "work_id":self.work_id ,
            "username":self.username ,
            "firstname":self.firstname ,
            "lastname":self.lastname ,
            "email":self.email ,
            "role":self.role ,
            "account_status":self.account_status ,
            "created_assignments": [each.to_dict() for each in self.created_assignments] ,
            "admin_privileges":[dict(id=each.id,privilege=each.privilege, description=each.description) for each in self.admin_privileges] ,
            "assigned_assignments":[each.to_dict() for each in self.assigned_assignments] ,
        }
        return model_return
    


class Assignment(db.Model):
    
    __tablename__='assignments'
    
    
    id=db.Column(db.Integer, primary_key=True)
    assignment_id=db.Column(db.String(255), nullable=False)
    title=db.Column(db.String(255), nullable=False )
    additional_info=db.Column(db.String(255), nullable=False )
    word_count=db.Column(db.String(255), nullable=False )
    deadline=db.Column(db.String(255), nullable=False )
    personnel_status=db.Column(db.Enum('Assigned', 'Unassigned'), nullable=False)
    assignment_status=db.Column(db.Enum('In progress', 'Completed'), nullable=False)
    file_url=db.Column(db.String(255), nullable=True )
    
    writer_id=db.Column(db.Integer,db.ForeignKey('users.id'),nullable=True)
    author_id=db.Column(db.Integer,db.ForeignKey('users.id'))
    
    assignment_author = db.relationship('User', foreign_keys=[author_id], backref='created_assignments')
    assigned_writer = db.relationship('User', foreign_keys=[writer_id], backref='assigned_assignments')
    
    created_at=db.Column(db.DateTime, server_default=db.func.now() )
    updated_at=db.Column(db.DateTime, onupdate=db.func.now() )
    
    @validates('personnel_status')
    def validate_personnel_status(self,key,value):
        personnel_status_options=['Assigned', 'Unassigned']
        if value not in personnel_status_options:
            raise ValueError("Only values accepted: 'Assigned', 'Unassigned'")
        
        return value
    
    @validates('assignment_status')
    def validate_assignment_status(self,key,value):
        assignment_status_options=['In progress', 'Completed']
        if value not in assignment_status_options:
            raise ValueError("Only values accepted: 'In progress', 'Completed'")
        
        return value
    
    def to_dict(self):
        model_return={
            "id":self.id ,
            "assignment_id":self.assignment_id ,
            "title":self.title ,
            "additional_info":self.additional_info ,
            "word_count":self.word_count ,
            "deadline":self.deadline ,
            "personnel_status":self.personnel_status ,
            "assignment_status":self.assignment_status ,
            "file_url":self.file_url ,
            
        }
        if  self.assigned_writer:
            model_return["assigned_writer"]=dict(id=self.assigned_writer.id,username=self.assigned_writer.username,
                                   firstname=self.assigned_writer.firstname, lastname=self.assigned_writer.lastname,
                                   role=self.assigned_writer.role, email=self.assigned_writer.email
                                   )
            
        else:
            model_return["assigned_writer"]=None
        return model_return




class PrivilegeConnector(db.Model):
    
    __tablename__='privilegeconnector'
    
    
    id=db.Column(db.Integer, primary_key=True)
     
    user_id=db.Column(db.Integer, db.ForeignKey('users.id'))
    adm_privilege_id=db.Column(db.Integer, db.ForeignKey('admin_privileges.id'))
    
    
class AdminPrivilege(db.Model):
    
    __tablename__='admin_privileges'
    
    
    id=db.Column(db.Integer, primary_key=True)
    privilege=db.Column(db.String(255), nullable=False )
    description=db.Column(db.String(255), nullable=True )
    
    _privileges=db.relationship('PrivilegeConnector', backref='adm_privilege')
    users=association_proxy(
        '_privileges','user',
        creator=lambda us: PrivilegeConnector(user=us)
        )
    
    def to_dict(self):
        model_return={
            "id":self.id ,
            "privilege":self.privilege ,
            "description":self.description ,
            "users":[
                {
            "id":each.id ,
            "work_id":each.work_id ,
            "username":each.username ,
            "firstname":each.firstname ,
            "lastname":each.lastname ,
            "email":each.email ,
            "role":each.role,
        }
        for each in self.users] ,
            
        }
        return model_return
    
   