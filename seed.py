from models import db, User, AdminPrivilege, Assignment,UserProfile,PrivilegeConnector
from app import app
from faker import Faker 
import random
from random import randint, choice 
from datetime import datetime, timedelta
import string

fake=Faker()

with app.app_context():
    # Assignment.query.delete()
    
    
    # Writer.query.delete()
    # User.query.filter(User.id>21).delete()
    print("Deleting ...")
    # AdminPrivilege.query.delete()
    # Assignment.query.delete()
    # PrivilegeConnector.query.delete()
    
    
    def generate_random_password():
        length = random.randint(8, 12)  # Choose a random length between 8 and 12 characters
        characters = string.ascii_letters + string.digits  # Alphanumeric characters
        password = ''.join(random.choice(characters) for _ in range(length))
        return password
    
    # Adding admins...
    control_status_options=['Main Admin', 'Admin']
    username_options=["Michaelson"]
    print("Adding admins...")
    all_admins=list()
    for username in username_options:
        random_numbers=random.randint(1000, 9999)
        each_admin=User(
            id=25,
            work_id=f"A{random_numbers}",
            username=fake.user_name(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone_number="+254763000000",
            email=fake.email(),password=generate_random_password(),role=random.choice(control_status_options),
            account_status="Active",
            # admin_id=random.randint(1,5)
            )
        all_admins.append(each_admin)
    
    db.session.bulk_save_objects(all_admins)
    
    
    # # Adding the writers______________________________________________________________
    # account_status_options=['Active', 'Deactivated']
    # print("Adding users...")
    # all_users=list()
    # for n in range(0,20):
    #     random_number = random.randint(1000, 9999)
    #     each_user=User(
    #         work_id=f"W{random_number}",
    #         username=fake.user_name(), firstname=fake.first_name(),lastname=fake.last_name(),
    #         phone_number="+254722000000",
    #         email=fake.email(),password=generate_random_password(),role="Writer",
    #         account_status=random.choice(account_status_options),
    #         # admin_id=random.randint(1,5)
    #         )
    #     all_users.append(each_user)
    
    # db.session.bulk_save_objects(all_users)
    
    # adding the user profiles___________________________________________________________________
    # all_profiles=list()
    # for n in range(22,26):
        
    #     single_profile=UserProfile(username=fake.user_name(), bio=fake.text(max_nb_chars=200), 
    #                                profile_url=None, user_id=n+1)
    #     all_profiles.append(single_profile)
    
    # db.session.bulk_save_objects(all_profiles)
    
    
    
    # # Adding assignments_____________________________________________________________
    # personnel_status_options=['Assigned', 'Unassigned']
    # assignment_status_options=['In progress', 'Completed']
    # word_count_options=[1500,2000,3000]
    # today = datetime.now()
    # future_date = today + timedelta(days=fake.random_int(min=1, max=30))
    # print("Adding assignments...")
    # all_assignments=list()
    # for n in range(0,40):
    #     each_assignment=Assignment(
    #         assignment_id=random.randint(1000, 3000), title=fake.catch_phrase(),additional_info=fake.paragraph(),
    #         word_count=random.choice(word_count_options),deadline=fake.date_time_between(start_date=today, end_date=future_date),
    #         personnel_status=random.choice(personnel_status_options),assignment_status=random.choice(assignment_status_options),
    #         writer_id=random.randint(0,20), author_id=random.randint(21,26)
    #         )
    #     all_assignments.append(each_assignment)
    
    # db.session.bulk_save_objects(all_assignments)
    
    
    
    
    # # Adding admin privileges...-_________________________________________________
    # privilege_options=['Modify Admin Permissions', 'Delete Admin Accounts', 'Deactivate And Delete Writer Accounts', 'Create Writer Accounts','Create And Edit Assignments']
    # print("Adding admin privileges...")
    # all_admin_privileges=list()
    
    # for privilege in privilege_options:
    #     each_admin_privilege=AdminPrivilege(
    #         privilege=privilege, description=fake.paragraph()
    #         )
    #     all_admin_privileges.append(each_admin_privilege)
    
    # db.session.bulk_save_objects(all_admin_privileges)
    
    
    
    # # Adding admin privilege connectors..._________________________________________________
    # print("Adding admin privilege connectors...")
    # all_admin_privileges_connectors=list()
    # for n in range(1,2):
    #     each_admin_privilege=PrivilegeConnector(
    #         user_id=26, adm_privilege_id=1+n
    #         )
    #     all_admin_privileges_connectors.append(each_admin_privilege)
    
    # db.session.bulk_save_objects(all_admin_privileges_connectors)
    
    
    db.session.commit()