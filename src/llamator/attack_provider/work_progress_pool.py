# llamator/src/llamator/attack_provider/work_progress_pool.py
import logging
import threading
import sys  # добавлен импорт для вывода в sys.stdout
from concurrent.futures import ThreadPoolExecutor

from tqdm.auto import tqdm

from llamator.format_output.color_consts import BRIGHT, GREEN, RED, RESET, YELLOW
from llamator.format_output.box_drawing import strip_ansi  # <-- Импорт функции для удаления ANSI-кодов

logger = logging.getLogger(__name__)


def _is_notebook_environment() -> bool:
    """
    Простая проверка на то, запущен ли код в Jupyter Notebook/колабе или нет.
    Если мы в Jupyter, возвращаем True, иначе False.
    """
    try:
        from IPython import get_ipython

        if get_ipython() is not None:
            return True
    except ImportError:
        pass
    return False


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
        """
        Функция обновляет прогресс-бар и описание задачи.

        Параметры:
        ----------
        task_name : str
            Название задачи, отображаемое пользователю.
        progress : float
            Текущее количество выполненных итераций.
        total : float
            Общее количество итераций.
        breach_count : int
            Количество успешных взломов (нарушений).
        resilient_count : int
            Количество заблокированных атак.
        error_count : int
            Количество ошибок.
        colour : str
            Цвет (tqdm позволяет менять цвет прогресс-бара).
        """
        if not self.progress_bar:
            return

        # Update tracking counts
        self.breach_count = breach_count
        self.resilient_count = resilient_count
        self.error_count = error_count

        # Format status info
        status_info = f"[{BRIGHT}{RED}B:{breach_count}{RESET} | {BRIGHT}{GREEN}R:{resilient_count}{RESET} | {BRIGHT}{YELLOW}E:{error_count}{RESET}]"

        # Если в Jupyter, удаляем ANSI-коды из task_name и status_info,
        # чтобы в прогресс-баре не было «кракозябр».
        if _is_notebook_environment():
            task_name = strip_ansi(task_name)
            status_info = strip_ansi(status_info)

        # Update the progress bar
        with self.progress_bar.get_lock():  # Ensure thread-safe updates
            progress_text = f"{task_name + ' ':.<40} [{progress}/{total}] {status_info}"
            # Если вы хотите совсем убрать цвет из описания даже вне Jupyter, можете также вызвать strip_ansi(progress_text)
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
        """
        Параллельный пул для выполнения тестов с отображением прогресса.

        Параметры:
        ----------
        num_workers : int
            Количество параллельных потоков (воркеров).
        """
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
        """
        Цикл для одного воркера:
        - Получаем задачу из итератора
        - Выполняем (task) в контексте ProgressWorker
        - Сигнализируем освобождение
        """
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
                # Task caused exception. Мы не можем напрямую распечатать ошибку через print в консоль,
                # так как это может конфликтовать с выводом tqdm. Используем логгер.
                logger.error(f"Task caused exception: {e}", exc_info=True)
                raise
            finally:
                self.semaphore.release()

    def run(self, tasks, tasks_count=None):
        """
        Запуск пула с воркерами для выполнения списка задач.

        Параметры:
        ----------
        tasks : итератор (generator) задач
        tasks_count : int
            Количество задач (используется для условного общего прогресс-бара).
        """
        self.tasks_count = tasks_count

        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            # Запускаем worker_function в каждом потоке
            futures = [executor.submit(self.worker_function, worker_id, tasks) for worker_id in range(self.num_workers)]
            # Ждём завершения всех воркеров
            for future in futures:
                future.result()

        # Закрываем прогресс-бары корректно
        for pw in self.progress_workers:
            pw.shutdown()


class ThreadSafeTaskIterator:
    """Это потокобезопасный итератор для задач."""

    def __init__(self, generator):
        """
        Параметры:
        ----------
        generator : iterable
            Источник задач.
        """
        self.generator = generator
        self.lock = threading.Lock()

    def __iter__(self):
        return self

    def __next__(self):
        """
        Извлекаем задачу из generator в потокобезопасном режиме.
        """
        with self.lock:
            return next(self.generator)