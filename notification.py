import threading
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal
import task_config


class Reminder(QObject):
    notify_signal: pyqtSignal = pyqtSignal(object)  # 显式声明信号类型

    def __init__(self, database_manager):
        super().__init__()
        self.database = database_manager
        self.reminders = []
        self.reminders_lock = threading.Lock()
        self.check_interval = 60  # 默认每 60 秒检查一次
        self._running = True
        self._check_thread = threading.Thread(target=self._run_check, daemon=True)
        self._check_thread.start()

    def update(self):
        """从数据库中获取最新的任务数据，并重新生成提醒"""
        new_reminders = self.database.filter_data(criteria={"state": task_config.STATE_PENDING}, sort_by='nextTime',
                                                   order='ASC')  # 提醒按照 nextTime(下次提醒时间) 排序
        with self.reminders_lock:  # 加锁保护
            self.reminders = new_reminders
        print(f"Updated reminders: {len(self.reminders)} task(s) pending.")

    def start(self):
        """启动提醒功能，定时检查任务的提醒时间"""
        self._running = True
        self._check_thread.start()

    def stop(self):
        """停止提醒功能"""
        self._running = False
        if hasattr(self, '_check_thread'):
            self._check_thread.join()

    def _run_check(self):
        """后台线程的主循环，用于检查并发送提醒"""
        while self._running:
            self.check_time()
            threading.Event().wait(self.check_interval)

    def check_time(self):
        """检查当前时间是否有任务需要提醒。如果满足提醒条件则触发提醒。"""
        # TODO：自定义提醒设置
        current_time = datetime.now()
        for task in self.reminders:
            notify_time = task.next_time
            if current_time >= notify_time and task.state == task_config.STATE_PENDING:
                print(f"send notification signal.")
                self.notify_signal.emit(task)  # 发射信号，携带任务对象
            if current_time < notify_time:
                break  # 避免重复提醒






