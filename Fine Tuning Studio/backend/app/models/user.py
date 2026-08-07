from . import db, BaseModel
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(BaseModel):
    """User model for authentication"""
    __tablename__ = 'users'

    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120))
    role = db.Column(db.String(20), default='user', nullable=False)  # user, admin
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    api_keys = db.relationship('APIKey', backref='user', lazy=True, cascade='all, delete-orphan')
    training_jobs = db.relationship('TrainingJob', backref='user', lazy=True, cascade='all, delete-orphan')
    datasets = db.relationship('Dataset', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = pwd_context.hash(password)

    def verify_password(self, password):
        """Verify password against hash"""
        return pwd_context.verify(password, self.password_hash)

    def to_dict(self):
        """Convert user to dictionary"""
        data = super().to_dict()
        data.update({
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'is_active': self.is_active
        })
        return data


class APIKey(BaseModel):
    """API key model for authentication"""
    __tablename__ = 'api_keys'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    key = db.Column(db.String(255), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120))
    is_active = db.Column(db.Boolean, default=True)
    last_used_at = db.Column(db.DateTime)

    def to_dict(self):
        """Convert API key to dictionary"""
        data = super().to_dict()
        data.update({
            'user_id': self.user_id,
            'key': f"{self.key[:10]}...***",
            'name': self.name,
            'is_active': self.is_active,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None
        })
        return data
