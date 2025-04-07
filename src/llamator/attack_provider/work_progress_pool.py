# llamator/src/llamator/attack_provider/work_progress_pool.py
import logging
import threading
import sys  # добавлен импорт для вывода в sys.stdout
from concurrent.futures import ThreadPoolExecutor

from tqdm.auto import tqdm

from llamator.format_output.color_consts import BRIGHT, GREEN, RED, RESET, YELLOW

logger = logging.getLogger(__name__)


class ProgressWorker:
    def __init__(self, worker_id, progress_bar=False):
        self.worker_id = worker_id
        self.progress_bar = None
        self.breach_count = 0
        self.resilient_count = 0
        self.error_count = 0

        if progress_bar:
            self.progress_bar = tqdm(
                total=1,
                desc=f"Worker #{worker_id:02}: {'(idle)':50}",
                position=worker_id,
                leave=True,
            )

    def shutdown(self):
        # When worker is destroyed, ensure the corresponding progress bars closes properly.
        if self.progress_bar:
            self.progress_bar.close()

    def update(
        self,
        task_name: str,
        progress: float,
        total: float,
        breach_count: int = 0,
        resilient_count: int = 0,
        error_count: int = 0,
        colour="BLACK",
    ):
        if not self.progress_bar:
            return

        # Update tracking counts
        self.breach_count = breach_count
        self.resilient_count = resilient_count
        self.error_count = error_count

        # Format status info
        status_info = f"[{BRIGHT}{RED}B:{breach_count}{RESET} | {BRIGHT}{GREEN}R:{resilient_count}{RESET} | {BRIGHT}{YELLOW}E:{error_count}{RESET}]"

        # Update the progress bar
        with self.progress_bar.get_lock():  # Ensure thread-safe updates
            progress_text = f"{task_name + ' ':.<40} [{progress}/{total}] {status_info}"
            self.progress_bar.set_description(
                f"Worker #{self.worker_id:02}: {progress_text}{RESET}",
                refresh=True,
            )
            self.progress_bar.colour = colour  # valid choices according to tqdm docs: [hex (#00ff00), BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE]
            self.progress_bar.n = int(progress)  # Directly set progress value
            self.progress_bar.total = int(total)  # And total value too
            self.progress_bar.refresh()  # Refresh to update the UI


class WorkProgressPool:
    def __init__(self, num_workers):
        enable_per_test_progress_bars = True  # Enable detailed progress bars
        self.num_workers = num_workers
        self.progress_workers = [
            ProgressWorker(worker_id, progress_bar=enable_per_test_progress_bars)
            for worker_id in range(self.num_workers)
        ]
        # Remove the queue_progress_bar as we don't want to display overall progress
        self.tasks_count = None
        self.semaphore = threading.Semaphore(
            self.num_workers
        )  # Used to ensure that at most this number of tasks are immediately pending waiting for free worker slot

    def worker_function(self, worker_id, tasks):
        progress_worker = self.progress_workers[worker_id]
        progress_bar = progress_worker.progress_bar
        for task in tasks:
            self.semaphore.acquire()  # Wait until a worker slot is available
            if task is None:
                break
            try:
                if progress_bar:
                    progress_bar.n = 0
                    progress_bar.total = 1
                    progress_bar.refresh()
                task(progress_worker)
            except Exception as e:
                # Task caused exception. We can't print it now, as it would interfere with the progress bar. We could log it to a file or similar.
                logger.error(f"Task caused exception: {e}", exc_info=True)
                raise
            finally:
                self.semaphore.release()  # Release the worker slot (this is crucial to do always, even if task thrown an exception, otherwise deadlocks or hangs could occur)
        """
        # Setting progress bar to a state indicating it is free and doesn't do any task right now...
        with progress_bar.get_lock():
            progress_bar.set_description(f"Worker #{worker_id:02}: {RESET}{'(idle)':50}{RESET}", refresh=True)
            progress_bar.n = 0
            progress_bar.total = 1
            progress_bar.refresh()
        """

    def run(self, tasks, tasks_count=None):
        self.tasks_count = tasks_count

        # We don't initialize or update queue_progress_bar anymore

        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            # Pass each worker its own progress bar reference
            futures = [executor.submit(self.worker_function, worker_id, tasks) for worker_id in range(self.num_workers)]
            # Wait for all workers to finish
            for future in futures:
                future.result()

        # Shut down the worker properly
        for pw in self.progress_workers:
            pw.shutdown()


class ThreadSafeTaskIterator:
    """This is a thread-safe iterator for tasks"""

    def __init__(self, generator):
        self.generator = generator
        self.lock = threading.Lock()

    def __iter__(self):
        return self

    def __next__(self):
        with self.lock:
            return next(self.generator)