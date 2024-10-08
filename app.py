import uuid
import datetime
import jwt
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from email_validator import validate_email, EmailNotValidError
from utils import send_email
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from tasks import send_queued_emails, queue_email
# Initialize Flask application
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://avnadmin:AVNS_7JH-2ruzIie96bkdhcs@mysql-279450c7-rajkisanssvrs-16fb.k.aivencloud.com:22461/defaultdb'
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Replace with your secret key

# Initialize SQLAlchemy and Migrate
db = SQLAlchemy(app)
migrate = Migrate(app, db)
scheduler = BackgroundScheduler()
# Import models after initializing SQLAlchemy
from models import User, Organization, Role, Member, Invite



import socket; ip_address = str(next((ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith('127.')), None))


def delete_expired_invites():
    with app.app_context():  # Create an application context
        try:
            # Retrieve all organizations that have set an expiration time
            organizations = Organization.query.filter(Organization.expire_minutes.isnot(None)).all()
            
            for org in organizations:
                # Get the expiration time for the organization
                expiration_time = datetime.utcnow() - timedelta(minutes=org.expire_minutes)
                
                # Fetch and delete expired invites for this organization
                expired_invites = Invite.query.filter(
                    Invite.org_id == org.id,
                    Invite.created_at < expiration_time.timestamp() * 1000  # Convert to milliseconds
                ).all()

                for invite in expired_invites:
                    db.session.delete(invite)
            
            # Commit after processing all organizations
            db.session.commit()
            print("Expired invites deleted successfully.")
        except Exception as e:
            print(f"Error in deleting expired invites: {e}")

scheduler.add_job(delete_expired_invites, 'interval', minutes=10)
scheduler.start()

@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.json
        required_fields = ('email', 'password', 'organization_name', 'role')
        if not all(key in data for key in required_fields):
            return jsonify({'message': 'Missing required fields'}), 400

        # Check if the organization already exists
        org = Organization.query.filter_by(name=data['organization_name']).first()

        # If organization does not exist, create a new one
        if not org:
            org = Organization(
                name=data['organization_name'],
                status=0
            )
            db.session.add(org)
            db.session.commit()

        # Check if the user already exists within the organization
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            # If user exists, check if they are already a member of the organization
            member = Member.query.filter_by(org_id=org.id, user_id=existing_user.id).first()
            if member:
                return jsonify({'message': 'User already exists in the organization.'}), 400

            # If user exists but is not a member, add them as a member
            role_name = data['role']
            role = Role.query.filter_by(name=role_name, org_id=org.id).first()
            if not role:
                role = Role(
                    name=role_name,
                    org_id=org.id
                )
                db.session.add(role)
                db.session.commit()

            member = Member(
                org_id=org.id,
                user_id=existing_user.id,
                role_id=role.id
            )
            db.session.add(member)
            db.session.commit()

            # Return response indicating user already exists
            return jsonify({
                'message': 'User already exists. Added to existing organization.',
                'user': {
                    'id': existing_user.id,
                    'email': existing_user.email
                },
                'organization': {
                    'id': org.id,
                    'name': org.name
                },
                'role': {
                    'id': role.id,
                    'name': role.name
                }
            })

        # If user does not exist, create a new user
        user = User(
            email=data['email'],
            password=generate_password_hash(data['password']),
            profile={},
            status=0
        )
        db.session.add(user)
        db.session.commit()

        # Create a new role if it doesn't already exist
        role_name = data['role']
        role = Role.query.filter_by(name=role_name, org_id=org.id).first()
        if not role:
            role = Role(
                name=role_name,
                org_id=org.id
            )
            db.session.add(role)
            db.session.commit()

        # Create a new member entry
        member = Member(
            org_id=org.id,
            user_id=user.id,
            role_id=role.id
        )
        db.session.add(member)
        db.session.commit()

        # Create and send invite
        invite_token = str(uuid.uuid4())
        invite_link = f'http://{ip_address}:5001/accept_invite?token={invite_token}'

        # Create and save invite
        invite = Invite(
            token=invite_token,
            user_id=user.id,
            org_id=org.id
        )
        db.session.add(invite)
        db.session.commit()

        # Send invite email
        queue_new_email(user.email, 'Welcome to our service!', 
                    f'You have been successfully signed up! Here is your invite link: {invite_link} (Invite expires in 10 minutes)')

        # Return response with user and organization information
        return jsonify({
            'message': 'User created successfully, invite mail sent successfully',
            'user': {
                'id': user.id,
                'email': user.email
            },
            'organization': {
                'id': org.id,
                'name': org.name
            },
            'role': {
                'id': role.id,
                'name': role.name
            }
        })

    except Exception as e:
        return jsonify({'message': str(e)}), 500


@app.route('/accept_invite', methods=['GET'])
def accept_invite():
    try:
        token = request.args.get('token')
        if not token:
            return jsonify({'message': 'Token is required'}), 400

        invite = Invite.query.filter_by(token=token).first()
        if invite:
            # Optionally, update the invite status or perform other actions here
            return jsonify({'message': 'Thanks for accepting the invite'})
        else:
            return jsonify({'message': 'Invalid or expired invite token'}), 400

    except Exception as e:
        return jsonify({'message': str(e)}), 500


@app.route('/get_user_org', methods=['GET'])
def get_user_orgs():
    try:
        # Get the username (email) from the query parameters
        username = request.args.get('username')

        if not username:
            return jsonify({'message': 'Username (email) is required.'}), 400

        # Query to find the user by email
        user = User.query.filter_by(email=username).first()

        if not user:
            return jsonify({'message': 'User not found.'}), 404

        # Find all members associated with the user
        members = Member.query.filter_by(user_id=user.id).all()

        if not members:
            return jsonify({'message': 'User is not a member of any organization.'}), 404

        # Retrieve all organizations linked to the user
        organizations = []
        for member in members:
            organization = Organization.query.get(member.org_id)
            if organization:
                organizations.append({
                    'organization_id': organization.id,
                    'organization_name': organization.name
                })

        return jsonify({
            'user_id': user.id,
            'organizations': organizations
        }), 200

    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/signin', methods=['POST'])
def signin():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()

    if user and check_password_hash(user.password, data['password']):
        # Fetch the user's role
        member = Member.query.filter_by(user_id=user.id).first()
        if member:
            role = Role.query.get(member.role_id)
            role_name = role.name if role else 'No Role Assigned'
        else:
            role_name = 'No Role Assigned'

        # Generate JWT token
        send_email(data['email'], 'Login Detected', 'You have logged in recently.')
        access_token = jwt.encode({'user_id': user.id, 'exp': datetime.utcnow() + timedelta(hours=1)},
                                  app.config['SECRET_KEY'], algorithm='HS256')
        refresh_token = jwt.encode({'user_id': user.id, 'exp': datetime.utcnow() + timedelta(days=30)},
                                   app.config['SECRET_KEY'], algorithm='HS256')

        return jsonify({
            'message': 'Login Mail Sent Successfully',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'role': role_name
        })
    else:
        return jsonify({'message': 'Invalid credentials'}), 401


@app.route('/reset_password', methods=['POST'])
def reset_password():
    data = request.json
    
    # Ensure all required fields are present
    if not all(key in data for key in ('email', 'new_password')):
        return jsonify({'message': 'Missing required fields'}), 400

    # Retrieve user by email
    user = User.query.filter_by(email=data['email']).first()

    if user:
        # Update password
        user.password = generate_password_hash(data['new_password'])
        db.session.commit()

        # Send confirmation email
        send_email(user.email, 'Password Reset', 'Your password has been reset successfully.')
        return jsonify({'message': 'Password reset successfully and mail sent successfully'})
    else:
        return jsonify({'message': 'User not found'}), 404


@app.route('/invite_member', methods=['POST'])
def invite_member():
    data = request.json
    invite_token = str(uuid.uuid4())

    invite_link = f'http://{ip_address}:5001/accept_invite?token={invite_token}'

    invite = Invite(
        token=invite_token,
        user_id=data['user_id'],
        org_id=data['org_id']
    )
    db.session.add(invite)
    db.session.commit()

    # Send invite email
    user = User.query.get(data['user_id'])
    queue_new_email(user.email, 'You are invited to join an organization!', 'You have been invited to join an organization. Please use the following link to accept the invite:' + invite_link +" Invite expires in 10 Minutes")

    return jsonify({'message': 'Invite mail sent successfully'})

@app.route('/delete', methods=['DELETE'])
def delete_entry():
    data = request.json
    user_id = data.get('user_id')
    org_id = data.get('org_id')

    # Check if both user_id and org_id are provided
    if not user_id:
        return jsonify({'message': 'User ID not provided'}), 400
    if not org_id:
        return jsonify({'message': 'Organization ID not provided'}), 400

    # Convert user_id to integer
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({'message': 'Invalid User ID'}), 400

    try:
        # Start a transaction
        # Find and delete member if it exists
        member = Member.query.filter_by(org_id=org_id, user_id=user_id).first()
        if member:
            print(f"Deleting member: {member}")  # Debugging line
            db.session.delete(member)

        # Delete associated invites if any
        invites = Invite.query.filter_by(user_id=user_id).all()
        for invite in invites:
            print(f"Deleting invite: {invite}")  # Debugging line
            db.session.delete(invite)

        # Find and delete the user if it exists
        user = User.query.get(user_id)
        if user:
            print(f"Deleting user: {user}")  # Debugging line
            db.session.delete(user)
        else:
            return jsonify({'message': 'User not found'}), 404

        # Commit all changes in one transaction
        db.session.commit()

        return jsonify({'message': 'User, Member, and associated Invites deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()  # Roll back in case of an error
        return jsonify({'message': 'An error occurred while deleting: ' + str(e)}), 500

@app.route('/organization/<int:org_id>/expire-minutes', methods=['GET'])
def set_expire_minutes(org_id):
    # Get the expire_minutes from request args
    expire_minutes = request.args.get('expire_minutes', None)

    # Validate if expire_minutes is provided and is a valid integer
    if expire_minutes is not None:
        try:
            expire_minutes = int(expire_minutes)
        except ValueError:
            return jsonify({"error": "expire_minutes must be a valid integer"}), 400
        
        # Check if expire_minutes is a multiple of 5
        if expire_minutes % 5 != 0:
            return jsonify({"error": "expire_minutes must be a multiple of 5"}), 400

    # Fetch the organization by ID
    organization = Organization.query.get(org_id)
    
    if not organization:
        return jsonify({"error": "Organization not found"}), 404

    # Update the expire_minutes field (can be set to None for null)
    organization.expire_minutes = expire_minutes
    
    # Commit the change to the database
    db.session.commit()
    
    return jsonify({"message": "expire_minutes updated successfully", 
                    "organization": {
                        "id": organization.id,
                        "name": organization.name,
                        "expire_minutes": organization.expire_minutes
                    }
                  }), 200

@app.route('/update_member_role', methods=['POST'])
def update_member_role():
    try:
        data = request.json

        user_id = data.get('user_id')
        org_id = data.get('org_id')
        new_role_name = data.get('new_role_name')

        if not all([user_id, org_id, new_role_name]):
            return jsonify({'message': 'Missing required fields'}), 400

        # Fetch the user and organization
        user = User.query.get(user_id)
        organization = Organization.query.get(org_id)

        if not user or not organization:
            return jsonify({'message': 'User or Organization not found'}), 404

        # Fetch the new role by name
        new_role = Role.query.filter_by(name=new_role_name, org_id=org_id).first()

        if not new_role:
            # Create a new role if it does not exist
            new_role = Role(name=new_role_name, org_id=org_id)
            db.session.add(new_role)
            db.session.commit()

        # Find the member and update the role
        member = Member.query.filter_by(user_id=user_id, org_id=org_id).first()

        if member:
            member.role_id = new_role.id
            db.session.commit()
            return jsonify({'message': 'Member role updated successfully'})
        else:
            return jsonify({'message': 'Member not found'}), 404

    except Exception as e:
        return jsonify({'message': str(e)}), 500



@app.route('/role_wise_users', methods=['GET'])
def role_wise_users():
    try:
        # Start by specifying the base table
        query = db.session.query(
            Role.name.label('role_name'),
            db.func.count(User.id).label('user_count')
        ).select_from(Role).join(Member).join(User)

        # Group by the role name
        query = query.group_by(Role.name)

        # Execute the query
        roles = query.all()

        # Convert the result to a list of dictionaries
        result = [{'role_name': role_name, 'user_count': user_count} for role_name, user_count in roles]

        return jsonify({'role_wise_users': result})
    except Exception as e:
        # Log the error and return an appropriate message
        print(f"Error: {e}")
        return jsonify({'message': 'An error occurred while processing the request'}), 500




@app.route('/stats/organization-role-users', methods=['GET'])
def get_organization_role_user_stats():
    from_time = request.args.get('from_time', type=int)
    to_time = request.args.get('to_time', type=int)
    status = request.args.get('status', type=int)
    
    try:
        # Base query
        query = db.session.query(
            Organization.name.label('organization_name'),
            Role.name.label('role_name'),
            User.created_at.label('created_at'),
            db.func.count(User.id).label('user_count')
        ).join(
            Member, Member.org_id == Organization.id
        ).join(
            User, User.id == Member.user_id
        ).join(
            Role, Role.id == Member.role_id
        )
        
        # Apply timestamp filters if provided
        if from_time is not None and to_time is not None:
            query = query.filter(User.created_at.between(from_time, to_time))
        
        # Apply status filter if provided
        if status is not None:
            query = query.filter(User.status == status)
        
        # Group by and fetch results
        results = query.group_by(
            Organization.name, Role.name, User.created_at
        ).all()

        # Create a response structure to organize the results
        stats = {}
        for org_name, role_name, created_at, user_count in results:
            created_at_str = datetime.fromtimestamp(created_at).strftime('%Y-%m-%d %H:%M:%S')
            if org_name not in stats:
                stats[org_name] = {}
            if role_name not in stats[org_name]:
                stats[org_name][role_name] = {
                    'user_count': user_count,
                    'created_at': created_at_str
                }
            else:
                stats[org_name][role_name]['user_count'] += user_count

        response = {
            'from_time': from_time,
            'to_time': to_time,
            'status': status,
            'data': stats
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({'message': str(e)}), 500
@app.route('/stats/organization-users', methods=['GET'])
def get_organization_user_stats():
    from_time = request.args.get('from_time', type=int)
    to_time = request.args.get('to_time', type=int)
    status = request.args.get('status', type=int)
    
    try:
        # Base query
        query = db.session.query(
            Organization.name.label('organization_name'),
            User.created_at.label('created_at'),
            db.func.count(User.id).label('user_count')
        ).join(
            Member, Member.org_id == Organization.id
        ).join(
            User, User.id == Member.user_id
        )
        
        # Apply timestamp filters if provided
        if from_time is not None and to_time is not None:
            query = query.filter(User.created_at.between(from_time, to_time))
        
        # Apply status filter if provided
        if status is not None:
            query = query.filter(User.status == status)
        
        # Group by and fetch results
        results = query.group_by(
            Organization.name, User.created_at
        ).all()

        # Create a response structure to organize the results
        stats = {}
        from_time_str = datetime.fromtimestamp(from_time).strftime('%Y-%m-%d %H:%M:%S')
        to_time_str = datetime.fromtimestamp(to_time).strftime('%Y-%m-%d %H:%M:%S')

        for org_name, created_at, user_count in results:
            created_at_str = datetime.fromtimestamp(created_at).strftime('%Y-%m-%d %H:%M:%S')

            print(created_at)
            stats[org_name] = {
                'user_count': user_count,
                'created_at': created_at_str
            }

        response = {
            'from_time': from_time_str,
            'to_time': to_time_str,
            'status': status,
            'data': stats
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({'message': str(e)}), 500


def queue_new_email(to_email, subject, content):
    # Add email to queue (you can change this to get data from request payload)
    queue_email.delay(to_email, subject, content)
    return jsonify({"message": "Email queued and will be sent in 1 minute."}), 200

# Route to immediately send all queued emails
@app.route('/send_queued_emails', methods=['GET'])
def send_all_queued_emails():
    # Call the task to immediately send all queued emails
    result = send_queued_emails.apply_async()
    return jsonify({"message": "All queued emails sent immediately.", "task_id": result.id}), 200

if __name__ == '__main__':

    app.run(host='0.0.0.0',port=5001,debug=True)

