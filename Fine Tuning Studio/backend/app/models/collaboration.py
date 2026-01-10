from . import db, BaseModel

class Team(BaseModel):
    __tablename__ = 'teams'

    name = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_public = db.Column(db.Boolean, default=False)

    members = db.relationship('TeamMember', backref='team', lazy=True, cascade='all, delete-orphan')
    models = db.relationship('SharedModel', backref='team', lazy=True)
    experiments = db.relationship('SharedExperiment', backref='team', lazy=True)

    def to_dict(self):
        data = super().to_dict()
        data.update({
            'name': self.name,
            'description': self.description,
            'owner_id': self.owner_id,
            'is_public': self.is_public
        })
        return data


class TeamMember(BaseModel):
    __tablename__ = 'team_members'

    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    role = db.Column(db.String(50), default='member')
    is_active = db.Column(db.Boolean, default=True)

    user = db.relationship('User')

    def to_dict(self):
        data = super().to_dict()
        data.update({
            'team_id': self.team_id,
            'user_id': self.user_id,
            'role': self.role,
            'is_active': self.is_active
        })
        return data


class SharedModel(BaseModel):
    __tablename__ = 'shared_models'

    model_id = db.Column(db.Integer, db.ForeignKey('model_metadata.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    shared_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    access_level = db.Column(db.String(50), default='read')

    def to_dict(self):
        data = super().to_dict()
        data.update({
            'model_id': self.model_id,
            'team_id': self.team_id,
            'shared_by': self.shared_by,
            'access_level': self.access_level
        })
        return data


class SharedExperiment(BaseModel):
    __tablename__ = 'shared_experiments'

    training_job_id = db.Column(db.Integer, db.ForeignKey('training_jobs.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    shared_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    access_level = db.Column(db.String(50), default='read')

    def to_dict(self):
        data = super().to_dict()
        data.update({
            'training_job_id': self.training_job_id,
            'team_id': self.team_id,
            'shared_by': self.shared_by,
            'access_level': self.access_level
        })
        return data


class Comment(BaseModel):
    __tablename__ = 'comments'

    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    training_job_id = db.Column(db.Integer, db.ForeignKey('training_jobs.id'))
    dataset_id = db.Column(db.Integer, db.ForeignKey('datasets.id'))

    user = db.relationship('User')

    def to_dict(self):
        data = super().to_dict()
        data.update({
            'content': self.content,
            'user_id': self.user_id,
            'training_job_id': self.training_job_id,
            'dataset_id': self.dataset_id
        })
        return data


class ConfigVersion(BaseModel):
    __tablename__ = 'config_versions'

    name = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    config_data = db.Column(db.JSON, nullable=False)
    description = db.Column(db.Text)
    version = db.Column(db.Integer, default=1)

    user = db.relationship('User')

    def to_dict(self):
        data = super().to_dict()
        data.update({
            'name': self.name,
            'user_id': self.user_id,
            'config_data': self.config_data,
            'description': self.description,
            'version': self.version
        })
        return data
