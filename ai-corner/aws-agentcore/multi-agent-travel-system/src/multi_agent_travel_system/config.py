"""Application configuration"""
import os
from typing import Optional


class Config:
    """Application configuration"""

    # AWS Configuration
    AWS_PROFILE: str = os.getenv("AWS_PROFILE", "admin-user")
    AWS_REGION: str = os.getenv("AWS_DEFAULT_REGION", "us-west-2")

    # Bedrock Model
    BEDROCK_MODEL: str = os.getenv(
        "BEDROCK_MODEL",
        "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
    )

    # Optional API Keys (for when you integrate real APIs)
    AMADEUS_API_KEY: Optional[str] = os.getenv("AMADEUS_API_KEY")
    BOOKING_API_KEY: Optional[str] = os.getenv("BOOKING_API_KEY")
    GETYOURGUIDE_API_KEY: Optional[str] = os.getenv("GETYOURGUIDE_API_KEY")

    # Application Settings
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    PORT: int = int(os.getenv("PORT", "8080"))

    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if "AWS_PROFILE" not in os.environ:
            raise ValueError("AWS_PROFILE environment variable is required")


# Create global config instance
config = Config()
