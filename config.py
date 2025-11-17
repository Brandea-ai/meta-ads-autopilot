"""
Configuration management for Meta Ads Autopilot
Handles environment variables and Streamlit secrets
"""
import os
from dotenv import load_dotenv
import streamlit as st
from typing import Optional

load_dotenv()

class Config:
    """Centralized configuration management"""

    @staticmethod
    def get(key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get configuration value from Streamlit secrets or environment variables

        Args:
            key: Configuration key to retrieve
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        # Try Streamlit secrets first (for cloud deployment)
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]

        # Fall back to environment variables
        return os.getenv(key, default)

    @staticmethod
    def get_required(key: str) -> str:
        """
        Get required configuration value, raise error if missing

        Args:
            key: Configuration key to retrieve

        Returns:
            Configuration value

        Raises:
            ValueError: If key is not found
        """
        value = Config.get(key)
        if value is None:
            raise ValueError(f"Required configuration '{key}' not found")
        return value

    @staticmethod
    def is_configured(key: str) -> bool:
        """
        Check if a configuration key is set

        Args:
            key: Configuration key to check

        Returns:
            True if key is set and non-empty
        """
        value = Config.get(key)
        return value is not None and value != ""
