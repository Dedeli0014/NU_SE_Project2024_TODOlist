from PyQt5.QtWidgets import QApplication
import sys
from GUI import MainWindow
from database import DatabaseManager
from management import TaskManager
from notification import Reminder

db_path = f"tasks.db"


def main():
    # 初始化应用
    app = QApplication(sys.argv)
    database_manager = DatabaseManager(db_path)
    reminder = Reminder(database_manager)
    task_manager = TaskManager(reminder=reminder, database_manager=database_manager)

    # 创建主窗口并传递任务管理器
    main_window = MainWindow(task_manager)

    reminder.notify_signal.connect(main_window.show_notification)

    # 显示主窗口
    main_window.show()

    # 启动应用的事件循环
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
