from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Multi-model manifest (see models.json.example). If the file doesn't
    # exist, the single MODEL_PATH/MODEL_NAME/MODEL_FAMILY fields below are
    # used to build a one-model registry instead.
    models_manifest: str = "models.json"
    max_loaded_models: int = 1

    # Legacy / single-model fallback
    model_path: Optional[str] = None
    model_name: str = "local-model"
    model_family: str = "auto"

    # Defaults applied to any manifest entry that doesn't override them
    n_ctx: int = 4096
    n_gpu_layers: int = 0
    n_threads: Optional[int] = None
    verbose: bool = False

    # Server
    host: str = "0.0.0.0"
    port: int = 8000


settings = Settings()
