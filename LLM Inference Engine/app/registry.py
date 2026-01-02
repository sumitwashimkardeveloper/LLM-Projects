"""Multi-model registry: declares which GGUF models are available, loads
them lazily on first use, and evicts the least-recently-used model once
more than `max_loaded_models` are resident so memory stays bounded.
"""

import json
import threading
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from .config import Settings
from .engine import LlamaCppEngine
from .errors import ModelNotFoundError
from .templates import ALLOWED_FAMILIES, detect_family

ALLOWED_SPEC_FAMILIES = ALLOWED_FAMILIES | {"auto"}


@dataclass
class ModelSpec:
    name: str
    path: str
    family: str = "auto"
    n_ctx: Optional[int] = None
    n_gpu_layers: Optional[int] = None
    n_threads: Optional[int] = None


def _load_model_specs(settings: Settings) -> List[ModelSpec]:
    manifest_path = Path(settings.models_manifest)
    if manifest_path.exists():
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        specs = [ModelSpec(**entry) for entry in data["models"]]
    elif settings.model_path:
        specs = [
            ModelSpec(name=settings.model_name, path=settings.model_path, family=settings.model_family)
        ]
    else:
        raise RuntimeError(
            f"No models configured: '{settings.models_manifest}' not found and MODEL_PATH is unset."
        )

    for spec in specs:
        if spec.family not in ALLOWED_SPEC_FAMILIES:
            raise RuntimeError(
                f"Model '{spec.name}' has unknown family '{spec.family}'; "
                f"expected one of {sorted(ALLOWED_SPEC_FAMILIES)}."
            )
    return specs


class ModelRegistry:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.specs: Dict[str, ModelSpec] = {s.name: s for s in _load_model_specs(settings)}
        self._engines: "OrderedDict[str, LlamaCppEngine]" = OrderedDict()
        self._lock = threading.Lock()

    def list_specs(self) -> List[ModelSpec]:
        return list(self.specs.values())

    def is_loaded(self, name: str) -> bool:
        return name in self._engines

    def get_family(self, name: str) -> str:
        spec = self.specs[name]
        return detect_family(name) if spec.family == "auto" else spec.family

    def get_engine(self, name: str) -> LlamaCppEngine:
        spec = self.specs.get(name)
        if spec is None:
            raise ModelNotFoundError(f"Model '{name}' is not configured.", param="model")

        with self._lock:
            engine = self._engines.get(name)
            if engine is not None:
                self._engines.move_to_end(name)
                return engine

            engine = LlamaCppEngine(
                model_path=spec.path,
                n_ctx=spec.n_ctx or self.settings.n_ctx,
                n_gpu_layers=(
                    spec.n_gpu_layers if spec.n_gpu_layers is not None else self.settings.n_gpu_layers
                ),
                n_threads=spec.n_threads if spec.n_threads is not None else self.settings.n_threads,
                verbose=self.settings.verbose,
            )
            self._engines[name] = engine

            while len(self._engines) > self.settings.max_loaded_models:
                self._engines.popitem(last=False)

            return engine
