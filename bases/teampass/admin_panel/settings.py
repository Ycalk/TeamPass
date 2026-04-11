from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict


class AdminPanelSettings(BaseSettings):
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        frozen=True,
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Team Pass Admin Panel"
    app_port: int = 8080

    secret_key: str
    super_admin_username: str
    super_admin_password: str
    admin_session_expire_days: int = 10
