import os
import torch
import json
from transformers import AutoModelForCausalLM, AutoTokenizer

class ModelExporter:
    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer

    def export_huggingface(self, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        self.model.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)
        return output_dir

    def export_onnx(self, output_dir, opset_version=14):
        try:
            from transformers.onnx import export
            os.makedirs(output_dir, exist_ok=True)

            onnx_config_class = export.TasksMapping.get_onnx_config_class(self.model.config.model_type)
            onnx_config = onnx_config_class(self.model.config)

            export(
                onnx_config=onnx_config,
                model=self.model,
                tokenizer=self.tokenizer,
                output_dir=output_dir,
                opset=opset_version
            )

            return output_dir
        except Exception as e:
            raise ValueError(f"ONNX export failed: {str(e)}")

    def export_torchscript(self, output_dir):
        os.makedirs(output_dir, exist_ok=True)

        traced_model = torch.jit.trace(
            self.model,
            example_kwarg_inputs=self._get_example_inputs()
        )

        model_path = os.path.join(output_dir, 'model.pt')
        traced_model.save(model_path)

        self.tokenizer.save_pretrained(output_dir)

        return output_dir

    def export_ggml(self, output_dir):
        os.makedirs(output_dir, exist_ok=True)

        model_path = os.path.join(output_dir, 'model.bin')
        torch.save(self.model.state_dict(), model_path)

        config_path = os.path.join(output_dir, 'config.json')
        with open(config_path, 'w') as f:
            json.dump(self.model.config.to_dict(), f)

        self.tokenizer.save_pretrained(output_dir)

        return output_dir

    def _get_example_inputs(self):
        dummy_input = {
            'input_ids': torch.tensor([[1, 2, 3, 4, 5]]),
            'attention_mask': torch.tensor([[1, 1, 1, 1, 1]])
        }
        return dummy_input


class AdapterMerger:
    @staticmethod
    def merge_lora(model, adapter_path=None):
        if hasattr(model, 'merge_and_unload'):
            return model.merge_and_unload()
        return model

    @staticmethod
    def merge_multiple_adapters(base_model, adapter_paths):
        current_model = base_model

        for adapter_path in adapter_paths:
            try:
                from peft import PeftModel
                current_model = PeftModel.from_pretrained(current_model, adapter_path)
                if hasattr(current_model, 'merge_and_unload'):
                    current_model = current_model.merge_and_unload()
            except Exception as e:
                raise ValueError(f"Failed to merge adapter {adapter_path}: {str(e)}")

        return current_model

    @staticmethod
    def save_merged_model(merged_model, tokenizer, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        merged_model.save_pretrained(output_dir)
        tokenizer.save_pretrained(output_dir)
        return output_dir


class QuantizationExporter:
    @staticmethod
    def export_4bit(model, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        model.save_pretrained(output_dir)
        return output_dir

    @staticmethod
    def export_8bit(model, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        model.save_pretrained(output_dir)
        return output_dir
