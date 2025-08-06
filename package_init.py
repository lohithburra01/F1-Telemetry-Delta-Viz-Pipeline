"""
F1 Telemetry Delta Calculator

A high-precision Formula 1 telemetry delta calculation engine designed for 
professional race analysis and 3D visualization pipelines.
"""

from .delta_calculator import F1TelemetryDeltaCalculator
from .utils import export_for_3d_pipeline, validate_session
from .visualization import F1PlotStyle

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    "F1TelemetryDeltaCalculator",
    "export_for_3d_pipeline", 
    "validate_session",
    "F1PlotStyle"
]
