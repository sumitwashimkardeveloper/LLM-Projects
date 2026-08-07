from . import db, BaseModel

class ModelMetadata(BaseModel):
    """Model metadata storage"""
    __tablename__ = 'model_metadata'

    name = db.Column(db.String(120), unique=True, nullable=False, index=True)
    model_type = db.Column(db.String(50), nullable=False)  # llama, mistral, qwen
    model_size = db.Column(db.String(50))  # 7b, 13b, 70b, etc.
    huggingface_id = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    parameters_count = db.Column(db.BigInteger)
    context_window = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    training_jobs = db.relationship('TrainingJob', backref='base_model', lazy=True)

    def to_dict(self):
        """Convert to dictionary"""
        data = super().to_dict()
        data.update({
            'name': self.name,
            'model_type': self.model_type,
            'model_size': self.model_size,
            'huggingface_id': self.huggingface_id,
            'description': self.description,
            'parameters_count': self.parameters_count,
            'context_window': self.context_window,
            'is_active': self.is_active
        })
        return data


class Checkpoint(BaseModel):
    """Model checkpoint storage"""
    __tablename__ = 'checkpoints'

    training_job_id = db.Column(db.Integer, db.ForeignKey('training_jobs.id'), nullable=False, index=True)
    checkpoint_name = db.Column(db.String(255), nullable=False)
    step = db.Column(db.Integer, nullable=False)
    loss = db.Column(db.Float)
    eval_loss = db.Column(db.Float)
    accuracy = db.Column(db.Float)
    checkpoint_path = db.Column(db.String(1024), nullable=False)
    metadata = db.Column(db.JSON)  # Additional checkpoint metadata
    is_best = db.Column(db.Boolean, default=False)

    # Relationships
    training_job = db.relationship('TrainingJob', backref='checkpoints')

    def to_dict(self):
        """Convert to dictionary"""
        data = super().to_dict()
        data.update({
            'training_job_id': self.training_job_id,
            'checkpoint_name': self.checkpoint_name,
            'step': self.step,
            'loss': self.loss,
            'eval_loss': self.eval_loss,
            'accuracy': self.accuracy,
            'checkpoint_path': self.checkpoint_path,
            'metadata': self.metadata,
            'is_best': self.is_best
        })
        return data
