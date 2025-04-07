# llamator/src/llamator/attack_provider/work_progress_pool.py

import logging
import threading
from concurrent.futures import ThreadPoolExecutor

from tqdm import tqdm as console_tqdm
from tqdm.auto import tqdm as notebook_tqdm

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
    В ноутбуке: каждая уникальная атака (ID) отображается динамическим баром tqdm.
    В консоли: используется один общий tqdm-бар на воркер, который обновляется при каждой задаче.
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
        self.progress_bar_enabled = progress_bar
        self.notebook_mode = _is_notebook_environment()
        self.lock = threading.Lock()

        # --- Ноутбучная логика (как было изначально) ---
        if self.notebook_mode:
            self.task_bars = {}  # key: attack_id, value: tqdm bar
            self.position_counter = 0
            self.final_status = {}
        else:
            # --- Консольная логика (ваш ранее работающий код) ---
            self.progress_bar = None
            self.breach_count = 0
            self.resilient_count = 0
            self.error_count = 0
            if progress_bar:
                # Создаём один общий bar на весь воркер
                self.progress_bar = console_tqdm(
                    total=1,
                    desc=f"Worker #{worker_id:02}: {'(idle)':50}",
                    position=worker_id,
                    leave=True,
                )

    def shutdown(self):
        """
        Закрывает прогресс-бары для ноутбука или консоли.
        """
        with self.lock:
            if self.notebook_mode:
                for bar in self.task_bars.values():
                    bar.close()
                self.task_bars.clear()
            else:
                # Консольный режим: закрываем общий бар, если он есть.
                if self.progress_bar:
                    self.progress_bar.close()

    def flush(self):
        """
        В ноутбуке обновляет все бары до конца и закрывает их.
        В консоли закрывать нечего — бар один и управляется напрямую.
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
        colour="BLACK",
    ):
        """
        Обновляет прогресс для заданной атаки (или задачи).

        Для ноутбука:
        -------------
        The task_name must be in the format "ACTION: ATTACK_ID", where ATTACK_ID is used as key.
        Внутри себя хранит словарь bar'ов.

        Для консоли:
        ------------
        Используется один общий tqdm-бар на воркер, обновляем при каждой задаче.

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
            Colour for the progress display (tqdm color choices).
        """
        if not self.progress_bar_enabled:
            return

        if self.notebook_mode:
            # ------------------ Ноутбуковый вариант -----------------------
            try:
                action, attack_id = task_name.split(":", 1)
                action = action.strip()
                attack_id = attack_id.strip()
            except ValueError:
                action = ""
                attack_id = task_name.strip()

            status_info = (
                f"[{BRIGHT}{RED}B:{breach_count}{RESET} | "
                f"{BRIGHT}{GREEN}R:{resilient_count}{RESET} | "
                f"{BRIGHT}{YELLOW}E:{error_count}{RESET}]"
            )

            with self.lock:
                # Убираем ANSI, если работаем в ноутбуке
                action = strip_ansi(action)
                attack_id = strip_ansi(attack_id)
                status_info = strip_ansi(status_info)

                if attack_id not in self.task_bars:
                    bar = notebook_tqdm(
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

                # Обновляем состояние прогресса
                bar.total = int(total)
                delta = int(progress) - bar.n
                if delta > 0:
                    bar.update(delta)

                if progress >= total:
                    # Выводим финальную строку и закрываем бар
                    bar.write(
                        f"Worker #{self.worker_id:02}: {action}: {attack_id} "
                        f"[{int(progress)}/{int(total)}] [B:{breach_count} | R:{resilient_count} | E:{error_count}] Finished"
                    )
                    bar.close()
                    del self.task_bars[attack_id]

        else:
            # ------------------ Консольный вариант -----------------------
            if not self.progress_bar:
                return

            with self.progress_bar.get_lock():
                # Обновляем счётчики
                self.breach_count = breach_count
                self.resilient_count = resilient_count
                self.error_count = error_count

                status_info = (
                    f"[{BRIGHT}{RED}B:{breach_count}{RESET} | "
                    f"{BRIGHT}{GREEN}R:{resilient_count}{RESET} | "
                    f"{BRIGHT}{YELLOW}E:{error_count}{RESET}]"
                )
                progress_text = f"{task_name + ' ':.<40} [{int(progress)}/{int(total)}] {status_info}"

                self.progress_bar.set_description(
                    f"Worker #{self.worker_id:02}: {progress_text}{RESET}",
                    refresh=True,
                )
                self.progress_bar.colour = colour
                self.progress_bar.n = int(progress)
                self.progress_bar.total = int(total)
                self.progress_bar.refresh()


class WorkProgressPool:
    """
    A thread pool that executes tasks in parallel, each worker having its own ProgressWorker.
    """

    def __init__(self, num_workers):
        """
        Parameters
        ----------
        num_workers : int
            Number of parallel workers.
        """
        # Ниже часть логики из консольного кода, где включались бары:
        enable_per_test_progress_bars = True
        self.num_workers = num_workers
        self.progress_workers = [
            ProgressWorker(worker_id, progress_bar=enable_per_test_progress_bars)
            for worker_id in range(self.num_workers)
        ]
        self.tasks_count = None
        self.semaphore = threading.Semaphore(
            self.num_workers
        )  # Used to ensure that at most this number of tasks are immediately pending waiting for free worker slot

    def worker_function(self, worker_id, tasks):
        """
        Worker loop: execute each task using the assigned ProgressWorker.
        """
        progress_worker = self.progress_workers[worker_id]
        for task in tasks:
            self.semaphore.acquire()
            if task is None:
                break
            try:
                # В консольном режиме сбрасываем бар перед задачей
                if not progress_worker.notebook_mode and progress_worker.progress_bar:
                    progress_worker.progress_bar.n = 0
                    progress_worker.progress_bar.total = 1
                    progress_worker.progress_bar.refresh()

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

        # Завершаем прогресс-бары
        for pw in self.progress_workers:
            pw.flush()
            pw.shutdown()


class ThreadSafeTaskIterator:
    """This is a thread-safe iterator for tasks"""

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