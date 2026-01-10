from .auth import auth_bp
from .models import models_bp
from .health import health_bp
from .datasets import datasets_bp
from .training import training_bp
from .dashboard import dashboard_bp
from .inference import inference_bp
from .alerts import alerts_bp
from .export import export_bp
from .collaboration import collab_bp

__all__ = ['auth_bp', 'models_bp', 'health_bp', 'datasets_bp', 'training_bp', 'dashboard_bp', 'inference_bp', 'alerts_bp', 'export_bp', 'collab_bp']
