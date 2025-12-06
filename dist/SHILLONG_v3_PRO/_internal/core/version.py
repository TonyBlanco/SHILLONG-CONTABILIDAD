# -*- coding: utf-8 -*-
"""
SHILLONG CONTABILIDAD — Version Information
"""

APP_VERSION = "3.8.0"
VERSION = APP_VERSION  # Alias for compatibility

# Build info
BUILD_DATE = "2025-12-05"
ENGINE_VERSION = "4.3.2"

def get_version():
    """Get current application version."""
    return APP_VERSION

def get_full_version():
    """Get full version string with build info."""
    return f"v{APP_VERSION} PRO (Engine {ENGINE_VERSION})"
