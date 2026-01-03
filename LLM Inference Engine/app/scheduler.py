import queue
import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Callable, List, Optional

from .errors import ContextLengthExceededError, QueueFullError


@dataclass
class GenerationJob:
    prompt: str
    max_tokens: int
    temperature: float
    top_p: float
    stop: List[str]
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    submitted_at: float = field(default_factory=time.perf_counter)
    out_queue: "queue.Queue" = field(default_factory=queue.Queue)
    cancel_event: threading.Event = field(default_factory=threading.Event)


class Slot:
    def __init__(self, index: int, engine):
        self.index = index
        self.engine = engine
        self.job: Optional[GenerationJob] = None
        self.generator = None
        self.generated_text = ""
        self.n_generated = 0

    @property
    def busy(self) -> bool:
        return self.job is not None


class BatchScheduler:
    def __init__(
        self,
        *,
        engine_factory: Callable,
        n_parallel: int = 2,
        max_queue: int = 64,
        request_timeout: float = 120.0,
    ):
        self.max_queue = max_queue
        self.request_timeout = request_timeout
        self._pending: "queue.Queue[GenerationJob]" = queue.Queue()
        self._slots = [
            Slot(index=i, engine=engine_factory()) for i in range(n_parallel)
        ]
        self._wake = threading.Event()
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def tokenize(self, text: str) -> List[int]:
        return self._slots[0].engine.tokenize(text)

    def submit(self, job: GenerationJob) -> None:
        if self._pending.qsize() >= self.max_queue:
            raise QueueFullError("Request queue is full; try again shortly.")
        self._pending.put(job)
        self._wake.set()

    def shutdown(self) -> None:
        self._stop.set()
        self._wake.set()
        self._thread.join(timeout=5)

    def _run(self) -> None:
        while not self._stop.is_set():
            self._admit_pending()
            active = [s for s in self._slots if s.busy]
            if not active:
                self._wake.wait(timeout=0.5)
                self._wake.clear()
                continue
            for slot in active:
                self._step(slot)

    def _admit_pending(self) -> None:
        for slot in self._slots:
            if slot.busy:
                continue
            try:
                job = self._pending.get_nowait()
            except queue.Empty:
                return
            if job.cancel_event.is_set():
                job.out_queue.put(("", "cancelled"))
                job.out_queue.put(None)
                continue
            if time.perf_counter() - job.submitted_at > self.request_timeout:
                job.out_queue.put(("", "timeout"))
                job.out_queue.put(None)
                continue
            self._start_job(slot, job)

    def _start_job(self, slot: Slot, job: GenerationJob) -> None:
        try:
            prompt_tokens = slot.engine.check_prompt_length(job.prompt)
        except ContextLengthExceededError:
            job.out_queue.put(("", "context_length_exceeded"))
            job.out_queue.put(None)
            return
        slot.job = job
        slot.generated_text = ""
        slot.n_generated = 0
        slot.generator = slot.engine.raw_generate(
            prompt_tokens, temp=job.temperature, top_p=job.top_p
        )

    def _step(self, slot: Slot) -> None:
        job = slot.job
        if job.cancel_event.is_set():
            self._finish(slot, "cancelled")
            return
        try:
            token_id = next(slot.generator)
        except StopIteration:
            self._finish(slot, "stop")
            return

        piece = slot.engine.detokenize([token_id])
        slot.generated_text += piece
        slot.n_generated += 1

        finish_reason = None
        if slot.engine.is_eos(token_id):
            finish_reason = "stop"
        elif job.stop and any(s and slot.generated_text.endswith(s) for s in job.stop):
            finish_reason = "stop"
        elif slot.n_generated >= job.max_tokens:
            finish_reason = "length"

        job.out_queue.put((piece, finish_reason))
        if finish_reason is not None:
            self._release(slot)

    def _finish(self, slot: Slot, finish_reason: str) -> None:
        slot.job.out_queue.put(("", finish_reason))
        self._release(slot)

    def _release(self, slot: Slot) -> None:
        slot.job.out_queue.put(None)
        slot.job = None
        slot.generator = None
        slot.generated_text = ""
        slot.n_generated = 0
