"""Доменные модели системы"""
from .task import Task, TaskStatus, TaskType, TIME_SLOTS
from .settings import Settings, ConnectionTestResult
from .references import ReferenceItem, References, ReferenceType
from .log import LogEntry, LogLevel, LogCategory

__all__ = [
    'Task', 'TaskStatus', 'TaskType', 'TIME_SLOTS',
    'Settings', 'ConnectionTestResult',
    'ReferenceItem', 'References', 'ReferenceType',
    'LogEntry', 'LogLevel', 'LogCategory'
]

