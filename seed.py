from models import db, Admin, Writer, AdminPrivilege, Assignment,PrivilegeConnector
from app import app
from faker import Faker 
import random
from random import randint, choice 
from datetime import datetime, timedelta
import string

fake=Faker()

with app.app_context():
    
    Admin.query.delete()
    Writer.query.delete()
    print("Deleting...")
    AdminPrivilege.query.delete()
    Assignment.query.delete()
    # PrivilegeConnector.query.delete()
    
    
    def generate_random_password():
        length = random.randint(8, 12)  # Choose a random length between 8 and 12 characters
        characters = string.ascii_letters + string.digits  # Alphanumeric characters
        password = ''.join(random.choice(characters) for _ in range(length))
        return password
    
    # Adding admins...
    control_status_options=['Main Admin', 'Admin']
    username_options=["Mary","Kate","Michaelson","Edgar","Susan"]
    print("Adding admins...")
    all_admins=list()
    for username in username_options:
        random_numbers=random.randint(1000, 9999)
        each_admin=Admin(
            work_id=f"A{random_numbers}",
            username=username, firstname=fake.first_name(),lastname=fake.last_name(),
            email=fake.email(),password=generate_random_password(),control_status=random.choice(control_status_options)
            )
        all_admins.append(each_admin)
    
    db.session.bulk_save_objects(all_admins)
    
    
    # Adding the writers
    account_status_options=['Active', 'Deactivated']
    print("Adding writers...")
    all_writers=list()
    for n in range(0,15):
        random_number = random.randint(1000, 9999)
        each_writer=Writer(
            work_id=f"W{random_number}",
            username=fake.user_name(), firstname=fake.first_name(),lastname=fake.last_name(),
            email=fake.email(),password=generate_random_password(),account_status=random.choice(account_status_options),
            admin_id=random.randint(1,5)
            )
        all_writers.append(each_writer)
    
    db.session.bulk_save_objects(all_writers)
    
    # Adding assignments
    personnel_status_options=['Assigned', 'Unassigned']
    assignment_status_options=['In progress', 'Completed']
    word_count_options=[1500,200,3000]
    today = datetime.now()
    future_date = today + timedelta(days=fake.random_int(min=1, max=30))
    print("Adding assignments...")
    all_assignments=list()
    for n in range(0,40):
        each_assignment=Assignment(
            assignment_id=random.randint(1000, 3000), title=fake.catch_phrase(),additional_info=fake.paragraph(),
            word_count=random.choice(word_count_options),deadline=fake.date_time_between(start_date=today, end_date=future_date),
            personnel_status=random.choice(personnel_status_options),assignment_status=random.choice(assignment_status_options),
            writer_id=random.randint(1,15), author_id=random.randint(1,5)
            )
        all_assignments.append(each_assignment)
    
    db.session.bulk_save_objects(all_assignments)
    
    
    # Adding admin privileges...
    privilege_options=['Modify Admin Permissions', 'Delete Admin Accounts', 'Deactivate And Delete Writer Accounts', 'Create Writer Accounts','Create And Edit Assignments']
    print("Adding admin privileges...")
    all_admin_privileges=list()
    
    for privilege in privilege_options:
        each_admin_privilege=AdminPrivilege(
            privilege=privilege, description=fake.paragraph()
            )
        all_admin_privileges.append(each_admin_privilege)
    
    db.session.bulk_save_objects(all_admin_privileges)
    
    
    
    # Adding admin privilege connectors...
    print("Adding admin privilege connectors...")
    all_admin_privileges_connectors=list()
    for n in range(3,4):
        each_admin_privilege=PrivilegeConnector(
            admin_id=5, adm_privilege_id=1+n
            )
        all_admin_privileges.append(each_admin_privilege)
    
    db.session.bulk_save_objects(all_admin_privileges)
    
    
    db.session.commit()