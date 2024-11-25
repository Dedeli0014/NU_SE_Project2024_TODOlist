from datetime import datetime, timedelta
from enum import Enum

# Constants for Priority
PRIORITY_HIGH = "High"
PRIORITY_MEDIUM = "Medium"
PRIORITY_LOW = "Low"

# Constants for Task Type
TYPE_WORK = "Work"
TYPE_STUDY = "Study"
TYPE_LIFE = "Life"
TYPE_HEALTH = "Health"
TYPE_SOCIALIZING = "Socializing"
TYPE_ENTERTAINMENT = "Entertainment"

# Constants for Task State
STATE_PENDING = "Pending"
STATE_FINISHED = "Finished"
STATE_OVERDUE = "Overdue"

# 定义允许的优先级、类型和状态的集合
ALLOWED_PRIORITIES = {PRIORITY_HIGH, PRIORITY_MEDIUM, PRIORITY_LOW}
ALLOWED_TYPES = {TYPE_WORK, TYPE_STUDY, TYPE_LIFE, TYPE_HEALTH, TYPE_SOCIALIZING, TYPE_ENTERTAINMENT}
ALLOWED_STATES = {STATE_PENDING, STATE_FINISHED, STATE_OVERDUE}

# # Enum for Priority
# class Priority(Enum):
#     HIGH = "High"
#     MEDIUM = "Medium"
#     LOW = "Low"
#
#
# # Enum for Task Type
# class Type(Enum):
#     WORK = "Work"
#     STUDY = "Study"
#     LIFE = "Life"
#     HEALTH = "Health"
#     SOCIALIZING = "Socializing"
#     ENTERTAINMENT = "Entertainment"
#
#
# # Enum for Task State
# class State(Enum):
#     PENDING = "Pending"
#     FINISHED = "Finished"
#     OVERDUE = "Overdue"
#

# Task 类定义
class Task:
    def __init__(self, title, description, deadline, priority, task_type, state=STATE_PENDING, next_time=None, id=None):
        self.__id = id
        self.__title = title
        self.__description = description
        self.__deadline = deadline
        self.__priority = priority
        self.__type = task_type
        self.__state = state
        if next_time:
            self.__next_time = next_time
        else:
            self.__next_time = deadline - timedelta(minutes=5)

    # ID属性仅提供getter，初始化后不能修改
    @property
    def id(self):
        return self.__id

    # Title属性
    @property
    def title(self):
        return self.__title

    @title.setter
    def title(self, value):
        if isinstance(value, str) and len(value) > 0:
            self.__title = value
        else:
            raise ValueError("Title must be a non-empty string.")

    # Description属性
    @property
    def description(self):
        return self.__description

    @description.setter
    def description(self, value):
        if isinstance(value, str):
            self.__description = value
        else:
            raise ValueError("Description must be a string.")

    # Deadline属性
    @property
    def deadline(self):
        return self.__deadline

    @deadline.setter
    def deadline(self, value):
        if isinstance(value, datetime):
            self.__deadline = value
            self.__next_time = self.__deadline - timedelta(minutes=5)
        else:
            raise ValueError("Deadline must be a datetime object.")

    # nextTime属性
    @property
    def next_time(self):
        return self.__next_time

    # Priority属性
    @property
    def priority(self):
        return self.__priority

    @priority.setter
    def priority(self, value):
        if value in ALLOWED_PRIORITIES:
            self.__priority = value
        else:
            raise ValueError("Priority must be a Priority enum value.")

    # Type属性
    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, value):
        if value in ALLOWED_TYPES:
            self.__type = value
        else:
            raise ValueError("Type must be a Type enum value.")

    # State属性
    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, value):
        if value in ALLOWED_STATES:
            self.__state = value
        else:
            raise ValueError("State must be a State enum value.")

