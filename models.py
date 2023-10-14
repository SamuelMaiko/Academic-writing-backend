from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin
import re

db=SQLAlchemy()

class User(db.Model):
    
    __tablename__='users'
    
    id=db.Column(db.Integer, primary_key=True)
    # , autoincrement=True
    work_id=db.Column(db.Integer, unique=True)
    username=db.Column(db.String(255), nullable=False, unique=True )
    email=db.Column(db.String(255), nullable=False, unique=True )
    password=db.Column(db.String(255), nullable=False )
    role=db.Column(db.String(255), nullable=False )
    created_at=db.Column(db.DateTime, server_default=db.func.now() )
    updated_at=db.Column(db.DateTime, onupdate=db.func.now() )
    
    @validates('password')
    def validate_password(self, key, value):
        if not (8 <= len(value) <= 12) or not re.match(r'^[A-Za-z0-9]*$', value):
            raise ValueError("Password must be between 8 and 12 characters long and contain only alphanumeric characters.")
        return value
    
    
    @validates('work_id')
    def validate_work_id(self, key, value):
        if not re.match(r'^W\d{4}$', value):
            raise ValueError("Work ID must be in the format 'WXXXX' where XXXX is a 4-digit number.")
        elif not re.match(r'^A\d{4}$', value):
            raise ValueError("Work ID must be in the format 'AXXXX' where XXXX is a 4-digit number.")
        return value
    
    
class Admin(db.Model):
    
    __tablename__='admins'
    
    
    id=db.Column(db.Integer, primary_key=True)
    work_id=db.Column(db.String(255), unique=True )
    username=db.Column(db.String(255), nullable=False, unique=True )
    firstname=db.Column(db.String(255), nullable=False )
    lastname=db.Column(db.String(255), nullable=False )
    email=db.Column(db.String(255), nullable=False, unique=True)
    password=db.Column(db.String(255), nullable=False )
    control_status=db.Column(db.Enum('Main Admin', 'Admin'), nullable=False)
    created_at=db.Column(db.DateTime, server_default=db.func.now() )
    updated_at=db.Column(db.DateTime, onupdate=db.func.now() )
    
    created_writer_accounts=db.relationship('Writer',backref='account_creator')
    created_assignments=db.relationship('Assignment', backref='assignment_author')
    
    _privileges=db.relationship('PrivilegeConnector', backref='admin')
    admin_privileges=association_proxy(
        '_privileges','adm_privilege',
        creator=lambda pr:PrivilegeConnector(adm_privilege=pr)
        )
    
    
    @validates('password')
    def validate_password(self, key, value):
        if not (8 <= len(value) <= 12) or not re.match(r'^[A-Za-z0-9]*$', value):
            raise ValueError("Password must be between 8 and 12 characters long and contain only alphanumeric characters.")
        return value
    
    @validates('control_status')
    def validate_control_status(self,key,value):
        control_status_options=['Main Admin', 'Admin']
        if value not in control_status_options:
            raise ValueError("Only values accepted: 'Main Admin', 'Admin'")
        
        return value
    
    @validates('work_id')
    def validate_work_id(self, key, value):
        if not re.match(r'^A\d{4}$', value):
            raise ValueError("Work ID must be in the format 'AXXXX' where XXXX is a 4-digit number.")
        return value
    
    
    def to_dict(self):
        model_return={
            "id":self.id ,
            "work_id":self.work_id ,
            "username":self.username ,
            "firstname":self.firstname ,
            "lastname":self.lastname ,
            "email":self.email ,
            "control_status":self.control_status ,
            "created_writer_accounts":[each.to_dict() for each in self.created_writer_accounts] ,
            "created_assignments": [each.to_dict() for each in self.created_assignments] ,
            "admin_privileges":[each.to_dict() for each in self.admin_privileges] ,
        }
        return model_return
    

class PrivilegeConnector(db.Model):
    
    __tablename__='privilegeconnector'
    
    
    id=db.Column(db.Integer, primary_key=True)
     
    admin_id=db.Column(db.Integer, db.ForeignKey('admins.id'))
    adm_privilege_id=db.Column(db.Integer, db.ForeignKey('admin_privileges.id'))
    
    
class AdminPrivilege(db.Model):
    
    __tablename__='admin_privileges'
    
    
    id=db.Column(db.Integer, primary_key=True)
    privilege=db.Column(db.String(255), nullable=False )
    description=db.Column(db.String(255), nullable=True )
    
    _privileges=db.relationship('PrivilegeConnector', backref='adm_privilege')
    admins=association_proxy(
        '_privileges','admin',
        creator=lambda adm: PrivilegeConnector(admin=adm)
        )
    
    def to_dict(self):
        model_return={
            "id":self.id ,
            "privilege":self.privilege ,
            "description":self.description ,
            "admins":[
                {
            "id":each.id ,
            "work_id":each.work_id ,
            "username":each.username ,
            "firstname":each.firstname ,
            "lastname":each.lastname ,
            "email":each.email ,
            "control_status":each.control_status,
        }
        for each in self.admins] ,
            
        }
        return model_return
    
    
class Writer(db.Model):
    
    __tablename__='writers'
    
    
    id=db.Column(db.Integer, primary_key=True)
    work_id=db.Column(db.String(255), unique=True )
    username=db.Column(db.String(255), nullable=False, unique=True )
    firstname=db.Column(db.String(255), nullable=False )
    lastname=db.Column(db.String(255), nullable=False )
    email=db.Column(db.String(255), nullable=False, unique=True )
    password=db.Column(db.String(255), nullable=False )
    account_status=db.Column(db.Enum('Active', 'Deactivated'), nullable=False)
    
    admin_id=db.Column(db.Integer, db.ForeignKey('admins.id'))
    
    assigned_assignments=db.relationship('Assignment', backref='assigned_writer')
    
    created_at=db.Column(db.DateTime, server_default=db.func.now() )
    updated_at=db.Column(db.DateTime, onupdate=db.func.now() )
    
    @validates('password')
    def validate_password(self, key, value):
        if not (8 <= len(value) <= 12) or not re.match(r'^[A-Za-z0-9]*$', value):
            raise ValueError("Password must be between 8 and 12 characters long and contain only alphanumeric characters.")
        return value
    
    @validates('account_status')
    def validate_account_status(self,key,value):
        account_status_options=['Active', 'Deactivated']
        if value not in account_status_options:
            raise ValueError("Only values accepted: 'Active', 'Deactivated'")
        
        return value
    
    @validates('work_id')
    def validate_work_id(self, key, value):
        if not re.match(r'^W\d{4}$', value):
            raise ValueError("Work ID must be in the format 'WXXXX' where XXXX is a 4-digit number.")
        return value
    
    
    def to_dict(self):
        model_return={
            "id":self.id ,
            "work_id":self.work_id ,
            "username":self.username ,
            "firstname":self.firstname ,
            "lastname":self.lastname ,
            "email":self.email ,
            "account_status":self.account_status ,
            "assigned_assignments":[each.to_dict() for each in self.assigned_assignments] ,
            # "lastname":self.lastname ,
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
    
    writer_id=db.Column(db.Integer,db.ForeignKey('writers.id'))
    author_id=db.Column(db.Integer,db.ForeignKey('admins.id'))
    
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
        return model_return