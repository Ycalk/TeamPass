from typing import ClassVar

from dishka import Provider, Scope, provide
from pydantic_settings import BaseSettings, SettingsConfigDict


class EntrypointSettings(BaseSettings):
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        frozen=True,
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Team Pass"
    api_prefix: str = "/api"
    api_port: int = 8080

    refresh_token_cookie_name: str = "refresh_token"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30
    jwt_encoding_algorithm: str = "HS256"

    @property
    def methods_prefix(self) -> str:
        return f"{self.api_prefix}/v1"

    secret_key: str


class EntrypointSettingsProvider(Provider):
    @provide(scope=Scope.APP)
    def settings(self) -> EntrypointSettings:
        return EntrypointSettings()  # type: ignore # pyright: ignore
