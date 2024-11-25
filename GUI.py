from datetime import datetime
from PyQt5.QtWidgets import QPushButton,QVBoxLayout, QDialog, QLabel, \
QLineEdit, QDateEdit, QTimeEdit, QComboBox, QMessageBox
from PyQt5 import QtWidgets, QtCore
import task_config
from management import TaskManager


class MainWindow(QtWidgets.QWidget):
    def __init__(self, task_manager):
        super().__init__()
        self.setWindowTitle("任务单 App")
        self.setGeometry(100, 100, 400, 300)
        self.task_manager = task_manager

        # Main Layout
        layout = QtWidgets.QVBoxLayout()

        # Buttons for main options
        create_task_button = QtWidgets.QPushButton("创建新任务")
        create_task_button.clicked.connect(self.open_create_task)
        layout.addWidget(create_task_button)

        view_today_tasks_button = QtWidgets.QPushButton("查看今日待办事项")
        view_today_tasks_button.clicked.connect(self.view_today_tasks)
        layout.addWidget(view_today_tasks_button)

        # 添加“分类查看任务”按钮
        view_category_tasks_button = QtWidgets.QPushButton("分类查看任务")
        view_category_tasks_button.clicked.connect(self.open_category_window)
        layout.addWidget(view_category_tasks_button)

        self.setLayout(layout)

    def open_create_task(self):
        create_task_window = TaskFormDialog(self.task_manager)
        create_task_window.exec_()  # 模态方式打开窗口

    def view_today_tasks(self):
        tasks = self.task_manager.get_today_tasks()
        task_window = TaskListWindow(tasks=tasks, task_manager=self.task_manager)
        task_window.exec_()

    def open_category_window(self):
        # 打开分类查看菜单
        category_window = CategoryWindow(self.task_manager)
        category_window.show()

    @staticmethod
    def show_notification(task):
        """在主线程中显示通知"""
        print(f"Notification received for task: {task.title}")
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Task Reminder")
        msg.setText(f"'{task.title}'快到截止时间啦！")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

        # TODO:播放声音提醒
        # sound = QSound("path_to_sound_file.wav")  # 替换为你的音频文件路径
        # sound.play()

class TaskFormDialog(QDialog):
    def __init__(self, task_manager, task=None):
        super().__init__()
        self.task_manager = task_manager
        self.task = task

        self.setWindowTitle("编辑任务" if task else "新任务")
        layout = QVBoxLayout(self)

        # 标题输入框
        self.title_input = QLineEdit(task.title if task else "")
        self.title_input.setPlaceholderText("任务名称")
        layout.addWidget(QLabel("标题"))
        layout.addWidget(self.title_input)

        # 描述输入框
        self.description_input = QLineEdit(task.description if task else "")
        self.description_input.setPlaceholderText("任务描述")
        layout.addWidget(QLabel("描述"))
        layout.addWidget(self.description_input)

        # 截止时间选择框
        self.date_edit = QDateEdit(task.deadline.date() if task else datetime.now().date())
        self.date_edit.setCalendarPopup(True)
        layout.addWidget(QLabel("截止日期"))
        layout.addWidget(self.date_edit)

        self.time_edit = QTimeEdit(task.deadline.time() if task else QtCore.QTime.currentTime())
        layout.addWidget(QLabel("截止时间"))
        layout.addWidget(self.time_edit)

        # 优先级选择框
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(task_config.ALLOWED_PRIORITIES)
        if task:
            self.priority_combo.setCurrentText(task.priority)
        layout.addWidget(QLabel("优先级"))
        layout.addWidget(self.priority_combo)

        # 任务类型选择框
        self.type_combo = QComboBox()
        self.type_combo.addItems(task_config.ALLOWED_TYPES)
        if task:
            self.type_combo.setCurrentText(task.type)
        layout.addWidget(QLabel("任务类型"))
        layout.addWidget(self.type_combo)

        # 创建或保存按钮
        action_button = QPushButton("保存" if task else "创建")
        action_button.clicked.connect(self.save_task)
        layout.addWidget(action_button)

        # TODO:自定义提醒时间和频率（当前默认ddl前5分钟发送提醒推送）

        self.setLayout(layout)

    def save_task(self):
        # 获取输入的任务属性
        title = self.title_input.text()
        description = self.description_input.text()
        deadline = datetime.combine(self.date_edit.date().toPyDate(), self.time_edit.time().toPyTime())
        priority = self.priority_combo.currentText()
        task_type = self.type_combo.currentText()

        try:
            if self.task:  # 编辑任务
                self.task.title = title
                self.task.description = description
                self.task.deadline = deadline
                self.task.priority = priority
                self.task.task_type = task_type
                self.task_manager.update_task(self.task)
            else:  # 创建新任务
                new_task = task_config.Task(title=title, description=description, deadline=deadline, priority=priority,
                                            task_type=task_type)
                self.task_manager.add_task(new_task)
            self.accept()  # 成功则关闭窗口

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "任务保存错误", f"添加任务时发生错误：{e}")


class TaskCard(QtWidgets.QWidget):
    def __init__(self, task, task_manager: TaskManager, task_list_window):
        super().__init__()
        self.task = task
        self.task_manager = task_manager
        self.task_list_window = task_list_window

        # 设置卡片布局
        layout = QtWidgets.QVBoxLayout(self)

        title_label = QtWidgets.QLabel(f"任务: {self.task.title}")
        deadline_label = QtWidgets.QLabel(f"截止时间: {self.task.deadline.strftime('%Y-%m-%d %H:%M')}")
        priority_label = QtWidgets.QLabel(f"优先级: {self.task.priority}")
        type_label = QtWidgets.QLabel(f"类型: {self.task.type}")

        layout.addWidget(title_label)
        layout.addWidget(deadline_label)
        layout.addWidget(priority_label)
        layout.addWidget(type_label)

        # 按钮 - 查看描述
        self.view_description_button = QtWidgets.QPushButton("任务详情")
        self.view_description_button.clicked.connect(self.view_description)
        layout.addWidget(self.view_description_button)

        # 按钮 - 修改任务
        self.edit_button = QtWidgets.QPushButton("修改任务")
        self.edit_button.clicked.connect(self.edit_task)
        layout.addWidget(self.edit_button)

        # 按钮 - 删除任务
        self.delete_button = QtWidgets.QPushButton("删除任务")
        self.delete_button.clicked.connect(self.delete_task)
        layout.addWidget(self.delete_button)

        # 按钮 - 勾选完成
        self.complete_button = QtWidgets.QPushButton("勾选完成")
        self.complete_button.clicked.connect(self.mark_completed)
        layout.addWidget(self.complete_button)

        self.setLayout(layout)

    def view_description(self):
        description_dialog = TaskDescriptionDialog(self.task)
        description_dialog.exec_()

    def edit_task(self):
        edit_dialog = TaskFormDialog(self.task_manager, task=self.task)
        edit_dialog.exec_()

    def delete_task(self):
        self.task_manager.delete_task(self.task)
        self.task_list_window.tasks.remove(self.task)  # 从 TaskListWindow 的任务列表中移除
        self.task_list_window.show_page()  # 刷新页面
        self.deleteLater()

    def mark_completed(self):
        self.task.state = task_config.STATE_FINISHED  # 或根据你的逻辑设置状态
        self.task_manager.update_task(self.task)
        self.task_list_window.tasks.remove(self.task)  # 从 TaskListWindow 的任务列表中移除
        self.task_list_window.show_page()  # 刷新页面
        self.deleteLater()


class TaskDescriptionDialog(QDialog):
    def __init__(self, task):
        super().__init__()
        self.setWindowTitle("任务详情")
        layout = QVBoxLayout(self)

        description_label = QLabel(f"任务详情: {task.description}")
        layout.addWidget(description_label)

        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

        self.setLayout(layout)


class TaskListWindow(QtWidgets.QDialog):
    def __init__(self, tasks, task_manager):
        super().__init__()
        self.setWindowTitle("TODO LIST")
        self.setGeometry(200, 200, 400, 300)

        self.tasks = tasks
        self.task_manager = task_manager
        self.page = 0
        self.tasks_per_page = 3  # 每页显示3个任务

        self.layout = QtWidgets.QVBoxLayout(self)

        # 显示任务卡片
        self.card_layout = QtWidgets.QVBoxLayout()
        self.layout.addLayout(self.card_layout)

        # 翻页按钮
        self.pagination_layout = QtWidgets.QHBoxLayout()
        self.prev_button = QtWidgets.QPushButton("上一页")
        self.prev_button.clicked.connect(self.show_previous_page)
        self.next_button = QtWidgets.QPushButton("下一页")
        self.next_button.clicked.connect(self.show_next_page)

        self.pagination_layout.addWidget(self.prev_button)
        self.pagination_layout.addWidget(self.next_button)
        self.layout.addLayout(self.pagination_layout)

        self.setLayout(self.layout)

        self.show_page()

    def show_page(self):
        # 清空当前卡片显示
        for i in reversed(range(self.card_layout.count())):
            widget = self.card_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        # 计算显示的任务范围
        start = self.page * self.tasks_per_page
        end = start + self.tasks_per_page
        tasks_to_display = self.tasks[start:end]

        # 为每个任务创建任务卡片并显示
        for task in tasks_to_display:
            card = TaskCard(task, task_manager=self.task_manager, task_list_window=self)
            self.card_layout.addWidget(card)

        # 更新翻页按钮状态
        self.prev_button.setEnabled(self.page > 0)
        self.next_button.setEnabled(end < len(self.tasks))

    def show_previous_page(self):
        if self.page > 0:
            self.page -= 1
            self.show_page()

    def show_next_page(self):
        if (self.page + 1) * self.tasks_per_page < len(self.tasks):
            self.page += 1
            self.show_page()


class CategoryWindow(QtWidgets.QDialog):
    def __init__(self, task_manager: TaskManager):
        super().__init__()
        self.setWindowTitle("选择任务分类")
        self.setGeometry(150, 150, 300, 200)

        self.task_manager = task_manager
        self.layout = QtWidgets.QVBoxLayout(self)

        # 按钮 - 所有任务
        all_tasks_button = QtWidgets.QPushButton("ALL TASKS")
        all_tasks_button.clicked.connect(self.view_all_tasks)
        self.layout.addWidget(all_tasks_button)

        # 按钮 - 工作类任务
        work_tasks_button = QtWidgets.QPushButton("WORK")
        work_tasks_button.clicked.connect(lambda: self.view_tasks_by_type(task_config.TYPE_WORK))
        self.layout.addWidget(work_tasks_button)


        # 按钮 - 学习类任务
        study_tasks_button = QtWidgets.QPushButton("STUDY")
        study_tasks_button.clicked.connect(lambda: self.view_tasks_by_type(task_config.TYPE_STUDY))
        self.layout.addWidget(study_tasks_button)

        # 按钮 - 健康类任务
        health_tasks_button = QtWidgets.QPushButton("HEALTH")
        health_tasks_button.clicked.connect(lambda: self.view_tasks_by_type(task_config.TYPE_HEALTH))
        self.layout.addWidget(health_tasks_button)

        # 按钮 - 生活类任务
        life_tasks_button = QtWidgets.QPushButton("LIFE")
        life_tasks_button.clicked.connect(lambda: self.view_tasks_by_type(task_config.TYPE_LIFE))
        self.layout.addWidget(life_tasks_button)

        # 按钮 - 社交类任务
        social_tasks_button = QtWidgets.QPushButton("SOCIALIZING")
        social_tasks_button.clicked.connect(lambda: self.view_tasks_by_type(task_config.TYPE_SOCIALIZING))
        self.layout.addWidget(social_tasks_button)

        # 按钮 - 娱乐类任务
        entertainment_tasks_button = QtWidgets.QPushButton("ENTERTAINMENT")
        entertainment_tasks_button.clicked.connect(lambda: self.view_tasks_by_type(task_config.TYPE_ENTERTAINMENT))
        self.layout.addWidget(entertainment_tasks_button)

        # TODO:按年月日视图查看任务

        # TODO:按照优先级查看任务

        self.setLayout(self.layout)

    def view_all_tasks(self):
        tasks = self.task_manager.get_all_tasks()
        task_window = TaskListWindow(tasks=tasks, task_manager=self.task_manager)
        task_window.exec_()

    def view_tasks_by_type(self, task_type: str):
        tasks = self.task_manager.get_tasks_by_type(task_type=task_type)
        task_window = TaskListWindow(tasks=tasks, task_manager=self.task_manager)
        task_window.exec_()


