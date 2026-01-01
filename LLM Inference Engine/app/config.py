from typing import Literal, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Model
    model_path: str
    model_name: str = "local-model"
    model_family: Literal["llama3", "mistral", "qwen", "gemma", "auto"] = "auto"

    # llama.cpp context
    n_ctx: int = 4096
    n_gpu_layers: int = 0
    n_threads: Optional[int] = None
    verbose: bool = False

    # Server
    host: str = "0.0.0.0"
    port: int = 8000


settings = Settings()
