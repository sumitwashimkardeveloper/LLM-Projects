import torch
import logging
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from peft import get_peft_model, LoraConfig, TaskType
from peft import prepare_model_for_kbit_training
from bitsandbytes.nn import Linear8bitLt
import os

logger = logging.getLogger(__name__)

class LoRAConfig:
    def __init__(self, r=8, lora_alpha=16, lora_dropout=0.05, target_modules=None, bias="none"):
        self.r = r
        self.lora_alpha = lora_alpha
        self.lora_dropout = lora_dropout
        self.target_modules = target_modules or ["q_proj", "v_proj"]
        self.bias = bias

    def to_peft_config(self):
        return LoraConfig(
            r=self.r,
            lora_alpha=self.lora_alpha,
            target_modules=self.target_modules,
            lora_dropout=self.lora_dropout,
            bias=self.bias,
            task_type=TaskType.CAUSAL_LM
        )

class TrainingConfig:
    def __init__(self, output_dir, num_train_epochs=3, per_device_train_batch_size=4,
                 per_device_eval_batch_size=4, learning_rate=2e-4, warmup_steps=100,
                 weight_decay=0.01, logging_steps=10, save_steps=500, eval_steps=500,
                 save_total_limit=3, gradient_accumulation_steps=1):
        self.output_dir = output_dir
        self.num_train_epochs = num_train_epochs
        self.per_device_train_batch_size = per_device_train_batch_size
        self.per_device_eval_batch_size = per_device_eval_batch_size
        self.learning_rate = learning_rate
        self.warmup_steps = warmup_steps
        self.weight_decay = weight_decay
        self.logging_steps = logging_steps
        self.save_steps = save_steps
        self.eval_steps = eval_steps
        self.save_total_limit = save_total_limit
        self.gradient_accumulation_steps = gradient_accumulation_steps

    def to_transformers_config(self):
        return TrainingArguments(
            output_dir=self.output_dir,
            overwrite_output_dir=True,
            num_train_epochs=self.num_train_epochs,
            per_device_train_batch_size=self.per_device_train_batch_size,
            per_device_eval_batch_size=self.per_device_eval_batch_size,
            learning_rate=self.learning_rate,
            warmup_steps=self.warmup_steps,
            weight_decay=self.weight_decay,
            logging_steps=self.logging_steps,
            logging_dir='./logs',
            save_strategy="steps",
            save_steps=self.save_steps,
            eval_strategy="steps",
            eval_steps=self.eval_steps,
            save_total_limit=self.save_total_limit,
            gradient_accumulation_steps=self.gradient_accumulation_steps,
            fp16=torch.cuda.is_available(),
            push_to_hub=False,
            load_best_model_at_end=True,
        )

class ModelTrainer:
    def __init__(self, model_id, training_type='lora', use_4bit=False, use_8bit=False):
        self.model_id = model_id
        self.training_type = training_type
        self.use_4bit = use_4bit
        self.use_8bit = use_8bit
        self.model = None
        self.tokenizer = None

    def load_model(self):
        logger.info(f"Loading model: {self.model_id}")

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id, trust_remote_code=True)
        self.tokenizer.pad_token = self.tokenizer.eos_token

        model_kwargs = {
            'trust_remote_code': True,
            'torch_dtype': torch.float16 if torch.cuda.is_available() else torch.float32,
            'device_map': 'auto'
        }

        if self.use_4bit:
            model_kwargs.update({
                'load_in_4bit': True,
                'bnb_4bit_compute_dtype': torch.float16,
                'bnb_4bit_use_double_quant': True,
                'bnb_4bit_quant_type': 'nf4'
            })
        elif self.use_8bit:
            model_kwargs['load_in_8bit'] = True

        self.model = AutoModelForCausalLM.from_pretrained(self.model_id, **model_kwargs)

        if self.use_4bit or self.use_8bit:
            self.model = prepare_model_for_kbit_training(self.model)

        return self.model, self.tokenizer

    def apply_lora(self, lora_config):
        if self.model is None:
            self.load_model()

        logger.info("Applying LoRA configuration")
        peft_config = lora_config.to_peft_config()
        self.model = get_peft_model(self.model, peft_config)
        self.model.print_trainable_parameters()

        return self.model

    def train(self, train_dataset, eval_dataset, training_config, callbacks=None):
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model() first.")

        logger.info("Starting training")

        def preprocess_function(examples):
            return self.tokenizer(
                examples['text'],
                truncation=True,
                max_length=512,
                padding='max_length'
            )

        train_dataset_processed = train_dataset.map(preprocess_function, batched=True)
        eval_dataset_processed = eval_dataset.map(preprocess_function, batched=True)

        training_args = training_config.to_transformers_config()

        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset_processed,
            eval_dataset=eval_dataset_processed,
            callbacks=callbacks or [],
        )

        trainer.train()

        return trainer

    def save_model(self, output_dir):
        logger.info(f"Saving model to {output_dir}")
        os.makedirs(output_dir, exist_ok=True)

        if hasattr(self.model, 'save_pretrained'):
            self.model.save_pretrained(output_dir)

        if self.tokenizer:
            self.tokenizer.save_pretrained(output_dir)

        return output_dir

    def save_adapter(self, output_dir):
        logger.info(f"Saving adapter to {output_dir}")
        os.makedirs(output_dir, exist_ok=True)

        if hasattr(self.model, 'save_pretrained'):
            self.model.save_pretrained(output_dir)

        return output_dir

    def merge_and_save(self, output_dir):
        logger.info(f"Merging and saving model to {output_dir}")

        if hasattr(self.model, 'merge_and_unload'):
            merged_model = self.model.merge_and_unload()
        else:
            merged_model = self.model

        os.makedirs(output_dir, exist_ok=True)
        merged_model.save_pretrained(output_dir)

        if self.tokenizer:
            self.tokenizer.save_pretrained(output_dir)

        return output_dir
