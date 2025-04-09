"""
Task package for geoservice.
Contains task implementations specific to the geoservice module.
"""

from .health_check import HealthCheckTask

__all__ = ['HealthCheckTask'] 