from . import db, BaseModel

class Dataset(BaseModel):
    """Dataset model"""
    __tablename__ = 'datasets'

    name = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    description = db.Column(db.Text)
    file_path = db.Column(db.String(1024), nullable=False)
    file_format = db.Column(db.String(50))  # csv, json, jsonl, parquet
    file_size = db.Column(db.BigInteger)
    total_samples = db.Column(db.Integer)
    train_samples = db.Column(db.Integer)
    val_samples = db.Column(db.Integer)
    test_samples = db.Column(db.Integer)
    status = db.Column(db.String(50), default='uploaded')  # uploaded, processed, validating
    metadata = db.Column(db.JSON)

    # Relationships
    user = db.relationship('User', backref='datasets')
    training_jobs = db.relationship('TrainingJob', backref='dataset', lazy=True)

    def to_dict(self):
        """Convert to dictionary"""
        data = super().to_dict()
        data.update({
            'name': self.name,
            'user_id': self.user_id,
            'description': self.description,
            'file_path': self.file_path,
            'file_format': self.file_format,
            'file_size': self.file_size,
            'total_samples': self.total_samples,
            'train_samples': self.train_samples,
            'val_samples': self.val_samples,
            'test_samples': self.test_samples,
            'status': self.status,
            'metadata': self.metadata
        })
        return data
