import os
import time
from typing import Dict, Tuple
from abc import ABC, abstractmethod
from dataclasses import dataclass
from config import ModelProvider, ModelConfig, OPENAI_PRICING, CLAUDE_PRICING, GEMINI_PRICING, LLAMA_PRICING

@dataclass
class ModelResponse:
    text: str
    latency: float
    input_tokens: int
    output_tokens: int
    cost: float

class BaseModel(ABC):
    def __init__(self, config: ModelConfig):
        self.config = config
        self.latency = 0.0
        self.cost = 0.0

    @abstractmethod
    def generate(self, prompt: str) -> ModelResponse:
        pass

    @abstractmethod
    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        pass

class OpenAIModel(BaseModel):
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=config.api_key or os.getenv("OPENAI_API_KEY"))
        except ImportError:
            raise ImportError("OpenAI library not installed")

    def generate(self, prompt: str) -> ModelResponse:
        start_time = time.time()

        try:
            response = self.client.chat.completions.create(
                model=self.config.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )

            latency = time.time() - start_time
            text = response.choices[0].message.content
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens

            cost = self.calculate_cost(input_tokens, output_tokens)

            return ModelResponse(
                text=text,
                latency=latency,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=cost
            )
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        pricing = OPENAI_PRICING.get(self.config.model_name, {"input": 0.0, "output": 0.0})
        cost = (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1000000
        return cost

class ClaudeModel(BaseModel):
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=config.api_key or os.getenv("ANTHROPIC_API_KEY"))
        except ImportError:
            raise ImportError("Anthropic library not installed")

    def generate(self, prompt: str) -> ModelResponse:
        start_time = time.time()

        try:
            response = self.client.messages.create(
                model=self.config.model_name,
                max_tokens=self.config.max_tokens,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.config.temperature
            )

            latency = time.time() - start_time
            text = response.content[0].text
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens

            cost = self.calculate_cost(input_tokens, output_tokens)

            return ModelResponse(
                text=text,
                latency=latency,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=cost
            )
        except Exception as e:
            raise Exception(f"Claude API error: {str(e)}")

    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        pricing = CLAUDE_PRICING.get(self.config.model_name, {"input": 0.0, "output": 0.0})
        cost = (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1000000
        return cost

class GeminiModel(BaseModel):
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        try:
            import google.generativeai as genai
            genai.configure(api_key=config.api_key or os.getenv("GEMINI_API_KEY"))
            self.model = genai.GenerativeModel(config.model_name)
        except ImportError:
            raise ImportError("Google Generative AI library not installed")

    def generate(self, prompt: str) -> ModelResponse:
        start_time = time.time()

        try:
            response = self.model.generate_content(
                prompt,
                generation_config={"temperature": self.config.temperature}
            )

            latency = time.time() - start_time
            text = response.text

            input_tokens = len(prompt.split())
            output_tokens = len(text.split())

            cost = self.calculate_cost(input_tokens, output_tokens)

            return ModelResponse(
                text=text,
                latency=latency,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=cost
            )
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")

    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        pricing = GEMINI_PRICING.get(self.config.model_name, {"input": 0.0, "output": 0.0})
        cost = (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1000000
        return cost

class LlamaModel(BaseModel):
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        try:
            from llama_cpp import Llama
            self.client = Llama(model_path=config.model_name)
        except ImportError:
            raise ImportError("Llama CPP Python library not installed")

    def generate(self, prompt: str) -> ModelResponse:
        start_time = time.time()

        try:
            response = self.client(
                prompt,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                echo=False
            )

            latency = time.time() - start_time
            text = response["choices"][0]["text"]

            input_tokens = len(prompt.split())
            output_tokens = len(text.split())

            cost = self.calculate_cost(input_tokens, output_tokens)

            return ModelResponse(
                text=text,
                latency=latency,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=cost
            )
        except Exception as e:
            raise Exception(f"Llama error: {str(e)}")

    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        pricing = LLAMA_PRICING.get(self.config.model_name, {"input": 0.0, "output": 0.0})
        cost = (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1000000
        return cost

class ModelFactory:
    @staticmethod
    def create_model(config: ModelConfig) -> BaseModel:
        if config.provider == ModelProvider.OPENAI:
            return OpenAIModel(config)
        elif config.provider == ModelProvider.CLAUDE:
            return ClaudeModel(config)
        elif config.provider == ModelProvider.GEMINI:
            return GeminiModel(config)
        elif config.provider == ModelProvider.LLAMA:
            return LlamaModel(config)
        else:
            raise ValueError(f"Unknown provider: {config.provider}")
