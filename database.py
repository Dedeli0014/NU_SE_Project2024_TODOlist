import sqlite3
import threading
from datetime import datetime
from typing import Dict
from task_config import Task


class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._initialize_database()
        self._lock = threading.Lock()  # 初始化锁

    def _initialize_database(self):
        """Initialize the tasks table in the database if it does not exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    title TEXT,
                    description TEXT,
                    deadline TEXT,  -- 存储为字符串格式
                    priority TEXT,
                    type TEXT,
                    state TEXT,
                    nextTime TEXT  -- 存储为字符串格式
                )
            ''')
            conn.commit()
            print("Initialized database and tasks table if not already present.")

    def _print_data(self):
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # 打印数据库全部数据
                cursor.execute("SELECT * FROM tasks")  # 查询tasks表中所有数据
                rows = cursor.fetchall()  # 获取所有结果
                # 打印表头
                cursor.execute("PRAGMA table_info(tasks)")
                columns = [col[1] for col in cursor.fetchall()]  # 获取列名
                print(" | ".join(columns))  # 打印列名分隔

    def _check_overdue_tasks(self):
        """Check and update the state of overdue tasks to 'OVERDUE' if they are still 'PENDING'."""

        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # # 打印数据库更新过程
                # # 打印更新前的状态
                # cursor.execute("SELECT datetime('now')")
                # print("Current time in SQLite:", cursor.fetchone()[0])
                # print("Before update:")
                # cursor.execute(
                #     "SELECT id, title, state, deadline FROM tasks WHERE state = 'Pending' AND "
                #     "deadline < datetime('now', 'localtime')")
                # overdue_tasks_before = cursor.fetchall()
                # for task in overdue_tasks_before:
                #     print(f"Task ID: {task[0]}, Title: {task[1]}, State: {task[2]}, Deadline: {task[3]}")
                # # 执行更新
                # cursor.execute('''
                #                 UPDATE tasks
                #                 SET state = 'Overdue'
                #                 WHERE deadline < datetime('now', 'localtime')
                #                 AND state = 'Pending'
                #             ''')
                # conn.commit()
                # # 打印更新后的状态
                # print("After update:")
                # cursor.execute("SELECT id, title, state, deadline FROM tasks WHERE state = 'Overdue'")
                # overdue_tasks_after = cursor.fetchall()
                # for task in overdue_tasks_after:
                #     print(f"Task ID: {task[0]}, Title: {task[1]}, State: {task[2]}, Deadline: {task[3]}")

                print("Checked and updated overdue tasks.")
                cursor.execute('''
                    UPDATE tasks
                    SET state = 'Overdue'
                    WHERE deadline < datetime('now', 'localtime')
                    AND state = 'Pending'
                ''')
                conn.commit()
        print("Checked and updated overdue tasks.")

    def write_data(self, task):
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO tasks (title, description, deadline, priority, type, state, nextTime)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    task.title,
                    task.description,
                    task.deadline.strftime("%Y-%m-%d %H:%M:%S"),  # 转为字符串
                    task.priority,
                    task.type,
                    task.state,
                    task.next_time.strftime("%Y-%m-%d %H:%M:%S") if task.next_time else None  # 转为字符串
                ))
                conn.commit()
        print(f"Inserted task: {task.title} into the database.")

    def read_data(self, task_id: int):
        self._check_overdue_tasks()
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
                row = cursor.fetchone()
                if row:
                    print(f"Read task: {task_id} from the database.")
                    return Task(
                        id=row[0],
                        title=row[1],
                        description=row[2],
                        deadline=datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S"),  # 转换为 datetime
                        priority=row[4],
                        task_type=row[5],
                        state=row[6],
                        next_time=datetime.strptime(row[7], "%Y-%m-%d %H:%M:%S") if row[7] else None  # 转换为 datetime
                    )
            return None

    def update_data(self, task):
        self._check_overdue_tasks()
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE tasks SET title=?, description=?, deadline=?, priority=?, type=?, 
                    state=?, nextTime=? WHERE id=?
                ''', (
                    task.title,
                    task.description,
                    task.deadline.strftime("%Y-%m-%d %H:%M:%S"),  # 转为字符串
                    task.priority,
                    task.type,
                    task.state,
                    task.next_time.strftime("%Y-%m-%d %H:%M:%S") if task.next_time else None,  # 转为字符串
                    task.id
                ))
                conn.commit()
            print(f"Updated task{task.id}: {task.title} in the database.")

    # def filter_data(self, criteria: Dict[str, str] = None, sort_by: str = None, order: str = "ASC"):
    #     self._check_overdue_tasks()
    #     with self._lock:
    #         query = 'SELECT * FROM tasks'
    #         conditions = []
    #         params = []
    #
    #         if criteria:
    #             for key, value in criteria.items():
    #                 conditions.append(f"{key} = ?")
    #                 params.append(value)
    #             query += ' WHERE ' + ' AND '.join(conditions)
    #
    #         if sort_by:
    #             query += f' ORDER BY {sort_by} {order.upper()}'
    #
    #         with sqlite3.connect(self.db_path) as conn:
    #             cursor = conn.cursor()
    #             cursor.execute(query, params)
    #             rows = cursor.fetchall()
    #             tasks = [
    #                 Task(
    #                     id=row[0],
    #                     title=row[1],
    #                     description=row[2],
    #                     deadline=datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S"),  # 转换为 datetime
    #                     priority=row[4],
    #                     task_type=row[5],
    #                     state=row[6],
    #                     next_time=datetime.strptime(row[7], "%Y-%m-%d %H:%M:%S") if row[7] else None  # 转换为 datetime
    #                 ) for row in rows
    #             ]
    #             return tasks
    def filter_data(self, criteria: Dict[str, str] = None, sort_by: str = None, order: str = "ASC"):
        # 检查是否有过期任务
        self._check_overdue_tasks()

        # 使用锁确保线程安全
        with self._lock:
            # 初始查询语句
            query = 'SELECT * FROM tasks'
            conditions = []
            params = []

            # 如果有筛选条件，构建条件部分
            if criteria:
                print("Applying filters...")
                for key, value in criteria.items():
                    conditions.append(f"{key} = ?")
                    params.append(value)
                query += ' WHERE ' + ' AND '.join(conditions)

            # 如果有排序条件，添加排序部分
            if sort_by:
                print(f"Sorting by {sort_by} in {order.upper()} order.")
                query += f' ORDER BY {sort_by} {order.upper()}'

            # 打印最终的查询语句
            print(f"Executing query: {query}")
            print(f"With parameters: {params}")

            # 执行查询并返回结果
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute(query, params)
                    rows = cursor.fetchall()

                    # 如果没有找到任何结果，打印信息
                    if not rows:
                        print("No tasks found matching the criteria.")

                    tasks = [
                        Task(
                            id=row[0],
                            title=row[1],
                            description=row[2],
                            deadline=datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S"),  # 转换为 datetime
                            priority=row[4],
                            task_type=row[5],
                            state=row[6],
                            next_time=datetime.strptime(row[7], "%Y-%m-%d %H:%M:%S") if row[7] else None  # 转换为 datetime
                        ) for row in rows
                    ]
                    print(f"Found {len(tasks)} tasks.")
                    return tasks
                except sqlite3.Error as e:
                    # 捕获数据库执行错误并打印错误信息
                    print(f"Error executing query: {e}")
                    return []

    def delete_data(self, task_id: int):
        """删除指定 task_id 的任务"""
        self._check_overdue_tasks()
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
                    conn.commit()
                    print(f"Task with ID {task_id} deleted successfully.")
            except sqlite3.Error as e:
                print(f"Error deleting task with ID {task_id}: {e}")

