"""Слой хранения данных"""
from .interfaces import (
    TaskRepository, SettingsRepository, ReferencesRepository, 
    LogRepository, DataManager
)
from .json_repository import JSONDataManager

__all__ = [
    'TaskRepository', 'SettingsRepository', 'ReferencesRepository',
    'LogRepository', 'DataManager', 'JSONDataManager'
]

