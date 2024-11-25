from datetime import datetime
from database import DatabaseManager
from notification import Reminder
import task_config


class TaskManager:
    def __init__(self, reminder: Reminder, database_manager:DatabaseManager):
        self.reminder = reminder
        self.database_manager = database_manager

    def add_task(self, task):
        self.database_manager.write_data(task)
        self.reminder.update()

    def delete_task(self, task):
        self.database_manager.delete_data(task.id)
        self.reminder.update()

    def update_task(self, task):
        self.database_manager.update_data(task)
        self.reminder.update()

    def get_today_tasks(self):
        """获取当日任务"""
        today = datetime.now().date()
        today_str = today.strftime("%Y-%m-%d")  # 转换为字符串，格式为 'YYYY-MM-DD'

        # 通过数据库直接筛选出今天截止的任务
        return self.database_manager.filter_data(
            criteria={"state": task_config.STATE_PENDING, "DATE(deadline)": today_str},
            sort_by="deadline",
            order='ASC'
        )

    def get_all_tasks(self):
        return self.database_manager.filter_data(criteria={"state": task_config.STATE_PENDING}, sort_by='deadline',
                                                 order='ASC')

    def get_tasks_by_type(self, task_type: str):
        return self.database_manager.filter_data(criteria={"state": task_config.STATE_PENDING, "type": task_type},
                                                 sort_by='deadline', order='ASC')



