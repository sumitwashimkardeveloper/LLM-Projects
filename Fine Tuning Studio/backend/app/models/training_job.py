from . import db, BaseModel

class TrainingJob(BaseModel):
    """Training job model"""
    __tablename__ = 'training_jobs'

    name = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    model_id = db.Column(db.Integer, db.ForeignKey('model_metadata.id'), nullable=False, index=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey('datasets.id'), nullable=False, index=True)

    # Training Configuration
    training_type = db.Column(db.String(50), nullable=False)  # lora, qlora, peft
    learning_rate = db.Column(db.Float, default=2e-4)
    batch_size = db.Column(db.Integer, default=4)
    num_epochs = db.Column(db.Integer, default=3)
    max_steps = db.Column(db.Integer, default=-1)

    # LoRA Configuration
    lora_r = db.Column(db.Integer, default=8)
    lora_alpha = db.Column(db.Integer, default=16)
    lora_dropout = db.Column(db.Float, default=0.05)
    lora_target_modules = db.Column(db.JSON)

    # Quantization Configuration
    use_4bit = db.Column(db.Boolean, default=False)
    use_8bit = db.Column(db.Boolean, default=False)

    # Training Status
    status = db.Column(db.String(50), default='queued')  # queued, running, completed, failed, paused
    progress = db.Column(db.Float, default=0.0)  # 0-100
    current_step = db.Column(db.Integer, default=0)
    total_steps = db.Column(db.Integer)

    # Training Metrics
    current_loss = db.Column(db.Float)
    best_loss = db.Column(db.Float)
    training_time = db.Column(db.Integer)  # in seconds

    # Output Configuration
    output_dir = db.Column(db.String(1024))
    save_strategy = db.Column(db.String(50), default='steps')  # steps, epoch, no
    save_steps = db.Column(db.Integer, default=500)

    # Error Tracking
    error_message = db.Column(db.Text)

    # Relationships
    user = db.relationship('User', backref='training_jobs')
    base_model = db.relationship('ModelMetadata', backref='training_jobs')
    dataset = db.relationship('Dataset', backref='training_jobs')

    def to_dict(self):
        """Convert to dictionary"""
        data = super().to_dict()
        data.update({
            'name': self.name,
            'user_id': self.user_id,
            'model_id': self.model_id,
            'dataset_id': self.dataset_id,
            'training_type': self.training_type,
            'learning_rate': self.learning_rate,
            'batch_size': self.batch_size,
            'num_epochs': self.num_epochs,
            'max_steps': self.max_steps,
            'lora_r': self.lora_r,
            'lora_alpha': self.lora_alpha,
            'lora_dropout': self.lora_dropout,
            'lora_target_modules': self.lora_target_modules,
            'use_4bit': self.use_4bit,
            'use_8bit': self.use_8bit,
            'status': self.status,
            'progress': self.progress,
            'current_step': self.current_step,
            'total_steps': self.total_steps,
            'current_loss': self.current_loss,
            'best_loss': self.best_loss,
            'training_time': self.training_time,
            'output_dir': self.output_dir,
            'save_strategy': self.save_strategy,
            'save_steps': self.save_steps,
            'error_message': self.error_message
        })
        return data
