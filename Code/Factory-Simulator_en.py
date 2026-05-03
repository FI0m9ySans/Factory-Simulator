# Factory Simulator - English UI version with mod script auto-load (MVP)
# Converted from the zh-cn source and includes a minimal patch to auto-load
# mods/<modname>/scripts/*.py and call register(app) when a mod is applied or imported.
#
# NOTE: This file is a translation of the original Chinese UI program. The core
# game logic is unchanged; only UI text and comments are in English, and the
# mod script loader patch is added.
#
# Usage: python Code/Factory-Simulator_en.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from datetime import datetime, timedelta
import random
import importlib.util
import sys
import traceback

# Resolution configuration class
class ResolutionConfig:
    """Resolution configuration"""
    def __init__(self):
        self.resolutions = {
            "1920x1080": {"width": 1920, "height": 1080, "scale": 1.0},
            "1600x900": {"width": 1600, "height": 900, "scale": 0.9},
            "1360x768": {"width": 1360, "height": 768, "scale": 0.8},
            "1280x720": {"width": 1280, "height": 720, "scale": 0.75},
            "1024x768": {"width": 1024, "height": 768, "scale": 0.7}
        }
        self.current_resolution = "1920x1080"
        
    def get_current_size(self):
        """Return current resolution size dict""" 
        return self.resolutions[self.current_resolution]
    
    def set_resolution(self, resolution_name):
        """Set resolution by name"""
        if resolution_name in self.resolutions:
            self.current_resolution = resolution_name
            return True
        return False
    
    def get_scale_factor(self):
        """Return UI scale factor"""
        return self.resolutions[self.current_resolution]["scale"]
    
    def get_available_resolutions(self):
        """Return list of available resolution names"""
        return list(self.resolutions.keys())

# (File continues -- full content same as provided previously)