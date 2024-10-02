from app import db
import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    profile = db.Column(db.JSON, default={}, nullable=False)
    status = db.Column(db.Integer, default=0, nullable=False)
    settings = db.Column(db.JSON, default={}, nullable=True)
    created_at = db.Column(db.BigInteger, default=lambda: int(datetime.datetime.utcnow().timestamp()), nullable=False)
    updated_at = db.Column(db.BigInteger, default=lambda: int(datetime.datetime.utcnow().timestamp()), 
                            onupdate=lambda: int(datetime.datetime.utcnow().timestamp()), nullable=False)
    invites = db.relationship('Invite', backref='user', lazy=True, cascade="all, delete-orphan")
    members = db.relationship('Member', backref='user', lazy=True, cascade="all, delete-orphan")

class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    status = db.Column(db.Integer, default=0, nullable=False)
    personal = db.Column(db.Boolean, default=False, nullable=True)
    settings = db.Column(db.JSON, default={}, nullable=True)
    expire_minutes = db.Column(db.Integer, nullable=True)  # Nullable expiration field
    created_at = db.Column(db.BigInteger, default=lambda: int(datetime.datetime.utcnow().timestamp()), nullable=False)
    updated_at = db.Column(db.BigInteger, default=lambda: int(datetime.datetime.utcnow().timestamp()), 
                            onupdate=lambda: int(datetime.datetime.utcnow().timestamp()), nullable=False)
    roles = db.relationship('Role', backref='organization', lazy=True, cascade="all, delete-orphan")
    members = db.relationship('Member', backref='organization', lazy=True, cascade="all, delete-orphan")
    invites = db.relationship('Invite', backref='organization', lazy=True, cascade="all, delete-orphan")

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    org_id = db.Column(db.Integer, db.ForeignKey('organization.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.BigInteger, default=lambda: int(datetime.datetime.utcnow().timestamp()), nullable=False)
    updated_at = db.Column(db.BigInteger, default=lambda: int(datetime.datetime.utcnow().timestamp()), 
                            onupdate=lambda: int(datetime.datetime.utcnow().timestamp()), nullable=False)
    members = db.relationship('Member', backref='role', lazy=True, cascade="all, delete-orphan")

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    org_id = db.Column(db.Integer, db.ForeignKey('organization.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.Integer, default=0, nullable=False)
    settings = db.Column(db.JSON, default={}, nullable=True)
    created_at = db.Column(db.BigInteger, default=lambda: int(datetime.datetime.utcnow().timestamp()), nullable=False)
    updated_at = db.Column(db.BigInteger, default=lambda: int(datetime.datetime.utcnow().timestamp()), 
                            onupdate=lambda: int(datetime.datetime.utcnow().timestamp()), nullable=False)

class Invite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(120), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    org_id = db.Column(db.Integer, db.ForeignKey('organization.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.BigInteger, default=lambda: int(datetime.datetime.utcnow().timestamp()), nullable=False)