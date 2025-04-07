# llamator/src/llamator/attack_provider/work_progress_pool.py

import logging
import threading
from concurrent.futures import ThreadPoolExecutor

from tqdm.auto import tqdm

from llamator.format_output.color_consts import BRIGHT, GREEN, RED, RESET, YELLOW
from llamator.format_output.box_drawing import strip_ansi

logger = logging.getLogger(__name__)


def _is_notebook_environment() -> bool:
    """
    Check if running in a Jupyter Notebook environment.
    Returns True if in Jupyter, otherwise False.
    """
    try:
        from IPython import get_ipython
        if get_ipython() is not None:
            return True
    except ImportError:
        pass
    return False


class ProgressWorker:
    """
    Manages progress display for a single worker.
    In notebook mode, each unique attack (identified by its ID) is updated in a dynamic tqdm progress bar.
    In non-notebook mode, only the final status is printed once per attack.
    """

    def __init__(self, worker_id, progress_bar=True):
        """
        Parameters
        ----------
        worker_id : int
            The worker's ID.
        progress_bar : bool
            Whether to enable progress display.
        """
        self.worker_id = worker_id
        self.enable_progress = progress_bar
        self.notebook_mode = _is_notebook_environment()
        self.lock = threading.Lock()
        if self.notebook_mode:
            self.task_bars = {}  # key: attack_id, value: tqdm bar
            self.position_counter = 0
        else:
            self.final_status = {}  # key: attack_id, value: final printed line

    def shutdown(self):
        """
        Close all progress bars (in notebook mode).
        """
        with self.lock:
            if self.notebook_mode:
                for bar in self.task_bars.values():
                    bar.close()
                self.task_bars.clear()

    def flush(self):
        """
        In notebook mode, update all progress bars to final state and close them.
        In non-notebook mode, nothing is required.
        """
        if self.notebook_mode:
            with self.lock:
                for bar in self.task_bars.values():
                    if bar.n < bar.total:
                        bar.update(bar.total - bar.n)
                    bar.refresh()
                    bar.close()
                self.task_bars.clear()

    def update(
        self,
        task_name: str,
        progress: float,
        total: float,
        breach_count: int = 0,
        resilient_count: int = 0,
        error_count: int = 0,
        colour: str = "BLACK",
    ):
        """
        Updates the progress display for a given attack.
        The task_name must be in the format "ACTION: ATTACK_ID", where ATTACK_ID is used as key.

        Parameters
        ----------
        task_name : str
            A string in the format "ACTION: ATTACK_ID" (e.g. "Attacking: RU_ucar").
        progress : float
            Current progress count.
        total : float
            Total steps.
        breach_count : int
            Number of breaches.
        resilient_count : int
            Number of resilient (blocked) attempts.
        error_count : int
            Number of errors.
        colour : str
            Colour for the progress display.
        """
        if not self.enable_progress:
            return

        try:
            action, attack_id = task_name.split(":", 1)
            action = action.strip()
            attack_id = attack_id.strip()
        except ValueError:
            action = ""
            attack_id = task_name.strip()

        # Build status info string
        status_info = (
            f"[{BRIGHT}{RED}B:{breach_count}{RESET} | "
            f"{BRIGHT}{GREEN}R:{resilient_count}{RESET} | "
            f"{BRIGHT}{YELLOW}E:{error_count}{RESET}]"
        )

        if self.notebook_mode:
            with self.lock:
                if _is_notebook_environment():
                    action = strip_ansi(action)
                    attack_id = strip_ansi(attack_id)
                    status_info = strip_ansi(status_info)
                if attack_id not in self.task_bars:
                    bar = tqdm(
                        total=int(total),
                        desc=f"Worker #{self.worker_id:02}: {action}: {attack_id}",
                        position=self.position_counter,
                        leave=True,
                    )
                    self.task_bars[attack_id] = bar
                    self.position_counter += 1
                else:
                    bar = self.task_bars[attack_id]
                desc_text = f"{action}: {attack_id} [{int(progress)}/{int(total)}] {status_info}"
                bar.set_description(f"Worker #{self.worker_id:02}: {desc_text}{RESET}", refresh=True)
                bar.colour = colour
                bar.total = int(total)
                bar.n = int(progress)
                bar.refresh()
                if progress >= total:
                    bar.close()
        else:
            # In non-notebook mode, print only the final status once.
            if progress < total:
                return
            with self.lock:
                if attack_id in self.final_status:
                    return
                final_status = f"Worker #{self.worker_id:02}: {action}: {attack_id} [{int(progress)}/{int(total)}] " \
                               f"[B:{breach_count} | R:{resilient_count} | E:{error_count}]"
                print(final_status)
                self.final_status[attack_id] = final_status


class WorkProgressPool:
    """
    A thread pool that executes tasks in parallel, each worker having its own ProgressWorker.
    """

    def __init__(self, num_workers: int):
        """
        Parameters
        ----------
        num_workers : int
            Number of parallel workers.
        """
        self.num_workers = num_workers
        self.progress_workers = [
            ProgressWorker(worker_id, progress_bar=True) for worker_id in range(self.num_workers)
        ]
        self.tasks_count = None
        self.semaphore = threading.Semaphore(self.num_workers)

    def worker_function(self, worker_id: int, tasks):
        """
        Worker loop: execute each task using the assigned ProgressWorker.
        """
        progress_worker = self.progress_workers[worker_id]
        for task in tasks:
            self.semaphore.acquire()
            if task is None:
                break
            try:
                task(progress_worker)
            except Exception as e:
                logger.error(f"Task caused exception: {e}", exc_info=True)
                raise
            finally:
                self.semaphore.release()

    def run(self, tasks, tasks_count=None):
        """
        Start the thread pool to execute a collection of tasks.

        Parameters
        ----------
        tasks : iterable
            An iterator or list of task callables. Each callable accepts a ProgressWorker.
        tasks_count : int, optional
            Total number of tasks.
        """
        self.tasks_count = tasks_count
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            futures = [
                executor.submit(self.worker_function, worker_id, tasks)
                for worker_id in range(self.num_workers)
            ]
            for f in futures:
                f.result()
        for pw in self.progress_workers:
            pw.flush()


class ThreadSafeTaskIterator:
    """
    A thread-safe iterator for tasks.
    """

    def __init__(self, generator):
        """
        Parameters
        ----------
        generator : iterable
            The source of tasks.
        """
        self.generator = generator
        self.lock = threading.Lock()

    def __iter__(self):
        return self

    def __next__(self):
        with self.lock:
            return next(self.generator)