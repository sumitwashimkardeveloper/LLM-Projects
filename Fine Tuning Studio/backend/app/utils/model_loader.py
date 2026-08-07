import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ModelRegistry:
    """Registry for supported models"""

    MODELS = {
        'llama': {
            'default': 'meta-llama/Llama-2-7b-hf',
            'variants': {
                '7b': 'meta-llama/Llama-2-7b-hf',
                '13b': 'meta-llama/Llama-2-13b-hf',
                '70b': 'meta-llama/Llama-2-70b-hf'
            }
        },
        'mistral': {
            'default': 'mistralai/Mistral-7B-v0.1',
            'variants': {
                '7b': 'mistralai/Mistral-7B-v0.1',
            }
        },
        'qwen': {
            'default': 'Qwen/Qwen-7B',
            'variants': {
                '7b': 'Qwen/Qwen-7B',
                '14b': 'Qwen/Qwen-14B',
            }
        }
    }

    @classmethod
    def get_model_id(cls, model_type: str, variant: Optional[str] = None) -> str:
        """Get HuggingFace model ID"""
        if model_type not in cls.MODELS:
            raise ValueError(f"Unsupported model type: {model_type}")

        if variant:
            if variant not in cls.MODELS[model_type]['variants']:
                raise ValueError(f"Unsupported variant: {variant}")
            return cls.MODELS[model_type]['variants'][variant]

        return cls.MODELS[model_type]['default']

    @classmethod
    def is_supported(cls, model_type: str) -> bool:
        """Check if model type is supported"""
        return model_type in cls.MODELS

    @classmethod
    def get_supported_types(cls) -> list:
        """Get list of supported model types"""
        return list(cls.MODELS.keys())


class ModelLoader:
    """Load and manage LLM models"""

    def __init__(self, model_cache_dir: str, device: str = 'cuda'):
        self.model_cache_dir = model_cache_dir
        self.device = device if torch.cuda.is_available() else 'cpu'
        self.loaded_models = {}
        logger.info(f"ModelLoader initialized with device: {self.device}")

    def load_model(
        self,
        model_type: str,
        model_id: Optional[str] = None,
        use_8bit: bool = False,
        use_4bit: bool = False,
        **kwargs
    ) -> tuple:
        """Load model and tokenizer"""

        try:
            # Get model ID
            if not model_id:
                model_id = ModelRegistry.get_model_id(model_type)

            # Check if model already loaded
            cache_key = f"{model_id}_{use_8bit}_{use_4bit}"
            if cache_key in self.loaded_models:
                logger.info(f"Using cached model: {model_id}")
                return self.loaded_models[cache_key]

            logger.info(f"Loading model: {model_id}")

            # Quantization configuration
            bnb_config = None
            if use_4bit or use_8bit:
                from bitsandbytes.nn import Linear4bit, Linear8bitLt
                bnb_config = {
                    'load_in_8bit': use_8bit,
                    'load_in_4bit': use_4bit,
                }
                if use_4bit:
                    bnb_config.update({
                        'bnb_4bit_compute_dtype': torch.float16,
                        'bnb_4bit_use_double_quant': True,
                        'bnb_4bit_quant_type': 'nf4'
                    })

            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(
                model_id,
                cache_dir=self.model_cache_dir,
                trust_remote_code=True
            )

            # Load model
            model_kwargs = {
                'cache_dir': self.model_cache_dir,
                'trust_remote_code': True,
                'torch_dtype': torch.float16 if self.device == 'cuda' else torch.float32,
                'device_map': 'auto'
            }

            if bnb_config:
                model_kwargs.update(bnb_config)

            model = AutoModelForCausalLM.from_pretrained(
                model_id,
                **model_kwargs
            )

            self.loaded_models[cache_key] = (model, tokenizer)
            logger.info(f"Model loaded successfully: {model_id}")

            return model, tokenizer

        except Exception as e:
            logger.error(f"Error loading model {model_id}: {str(e)}")
            raise

    def unload_model(self, model_id: str, use_8bit: bool = False, use_4bit: bool = False):
        """Unload model from memory"""
        cache_key = f"{model_id}_{use_8bit}_{use_4bit}"
        if cache_key in self.loaded_models:
            del self.loaded_models[cache_key]
            logger.info(f"Model unloaded: {model_id}")

    def get_model_info(self, model_type: str, model_id: Optional[str] = None) -> Dict[str, Any]:
        """Get model information"""
        if not model_id:
            model_id = ModelRegistry.get_model_id(model_type)

        return {
            'model_id': model_id,
            'model_type': model_type,
            'device': self.device,
            'cached': f"{model_id}_*" in str(self.loaded_models.keys())
        }

    def clear_cache(self):
        """Clear all loaded models"""
        self.loaded_models.clear()
        logger.info("Model cache cleared")
