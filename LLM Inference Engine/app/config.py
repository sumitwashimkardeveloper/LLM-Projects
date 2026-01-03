from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    models_manifest: str = "models.json"
    max_loaded_models: int = 1
    n_parallel: int = 2
    max_queue_depth: int = 64
    request_timeout_s: float = 120.0

    model_path: Optional[str] = None
    model_name: str = "local-model"
    model_family: str = "auto"

    n_ctx: int = 4096
    n_gpu_layers: int = 0
    n_threads: Optional[int] = None
    verbose: bool = False

    awq_device: str = "cuda:0"
    awq_dtype: str = "float16"

    api_keys: str = ""
    rate_limit_rpm: int = 0

    host: str = "0.0.0.0"
    port: int = 8000


settings = Settings()
