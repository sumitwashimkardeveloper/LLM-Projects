import torch
from torch.nn.utils import clip_grad_norm_
import logging

logger = logging.getLogger(__name__)

class DistributedTrainingConfig:
    def __init__(self, backend='nccl', init_method='env://'):
        self.backend = backend
        self.init_method = init_method
        self.rank = 0
        self.world_size = 1
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    def setup_distributed(self):
        if torch.cuda.is_available() and torch.cuda.device_count() > 1:
            torch.distributed.init_process_group(
                backend=self.backend,
                init_method=self.init_method
            )
            self.rank = torch.distributed.get_rank()
            self.world_size = torch.distributed.get_world_size()
            logger.info(f"Distributed training setup: rank={self.rank}, world_size={self.world_size}")

    def cleanup(self):
        if torch.distributed.is_available() and torch.distributed.is_initialized():
            torch.distributed.destroy_process_group()


class MixedPrecisionTrainer:
    def __init__(self, model, use_amp=True):
        self.model = model
        self.use_amp = use_amp and torch.cuda.is_available()
        self.scaler = torch.cuda.amp.GradScaler() if self.use_amp else None

    def train_step(self, batch, optimizer, loss_fn):
        if self.use_amp:
            with torch.cuda.amp.autocast():
                outputs = self.model(**batch)
                loss = loss_fn(outputs)

            self.scaler.scale(loss).backward()
            self.scaler.unscale_(optimizer)
            clip_grad_norm_(self.model.parameters(), 1.0)
            self.scaler.step(optimizer)
            self.scaler.update()
        else:
            outputs = self.model(**batch)
            loss = loss_fn(outputs)
            loss.backward()
            clip_grad_norm_(self.model.parameters(), 1.0)
            optimizer.step()

        return loss.item()


class GradientAccumulator:
    def __init__(self, accumulation_steps=4):
        self.accumulation_steps = accumulation_steps
        self.step_count = 0

    def should_step(self):
        return (self.step_count + 1) % self.accumulation_steps == 0

    def increment(self):
        self.step_count += 1

    def reset(self):
        self.step_count = 0


class CallbackManager:
    def __init__(self):
        self.callbacks = []

    def add_callback(self, callback):
        self.callbacks.append(callback)

    def on_train_begin(self, args, state, control):
        for callback in self.callbacks:
            if hasattr(callback, 'on_train_begin'):
                callback.on_train_begin(args, state, control)

    def on_step_end(self, args, state, control):
        for callback in self.callbacks:
            if hasattr(callback, 'on_step_end'):
                callback.on_step_end(args, state, control)

    def on_epoch_end(self, args, state, control):
        for callback in self.callbacks:
            if hasattr(callback, 'on_epoch_end'):
                callback.on_epoch_end(args, state, control)

    def on_train_end(self, args, state, control):
        for callback in self.callbacks:
            if hasattr(callback, 'on_train_end'):
                callback.on_train_end(args, state, control)


class CustomLossFunction:
    @staticmethod
    def focal_loss(predictions, targets, alpha=0.25, gamma=2.0):
        ce_loss = torch.nn.functional.cross_entropy(predictions, targets, reduction='none')
        p_t = torch.exp(-ce_loss)
        focal_loss = alpha * (1 - p_t) ** gamma * ce_loss
        return focal_loss.mean()

    @staticmethod
    def label_smoothing_loss(predictions, targets, smoothing=0.1):
        n_classes = predictions.size(-1)
        log_probs = torch.nn.functional.log_softmax(predictions, dim=-1)
        loss = -log_probs.gather(dim=-1, index=targets.unsqueeze(-1))
        loss += -((1.0 - smoothing) / (n_classes - 1)) * log_probs.sum(dim=-1, keepdim=True)
        return loss.mean()

    @staticmethod
    def contrastive_loss(embeddings1, embeddings2, temperature=0.07):
        logits = torch.matmul(embeddings1, embeddings2.t()) / temperature
        batch_size = embeddings1.size(0)
        labels = torch.arange(batch_size).to(embeddings1.device)
        loss = torch.nn.functional.cross_entropy(logits, labels)
        return loss


class ModelOptimizer:
    @staticmethod
    def prune_model(model, pruning_amount=0.3):
        import torch.nn.utils.prune as prune

        for name, module in model.named_modules():
            if isinstance(module, torch.nn.Linear):
                prune.l1_unstructured(module, name='weight', amount=pruning_amount)
                prune.remove(module, 'weight')

        return model

    @staticmethod
    def quantize_model(model, quantization_type='int8'):
        if quantization_type == 'int8':
            model = torch.quantization.quantize_dynamic(
                model,
                {torch.nn.Linear},
                dtype=torch.qint8
            )
        elif quantization_type == 'float16':
            model = model.half()

        return model

    @staticmethod
    def knowledge_distillation(teacher_model, student_model, train_dataloader,
                               temperature=4.0, alpha=0.7, num_epochs=3):
        optimizer = torch.optim.Adam(student_model.parameters(), lr=1e-4)
        criterion = torch.nn.KLDivLoss(reduction='batchmean')

        for epoch in range(num_epochs):
            for batch in train_dataloader:
                teacher_outputs = teacher_model(**batch)
                student_outputs = student_model(**batch)

                teacher_probs = torch.softmax(teacher_outputs.logits / temperature, dim=-1)
                student_log_probs = torch.log_softmax(student_outputs.logits / temperature, dim=-1)

                distillation_loss = criterion(student_log_probs, teacher_probs)
                task_loss = torch.nn.functional.cross_entropy(
                    student_outputs.logits,
                    batch['labels']
                )

                loss = alpha * distillation_loss + (1 - alpha) * task_loss

                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

        return student_model
