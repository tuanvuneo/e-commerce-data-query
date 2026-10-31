from pathlib import Path

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        hide_input_in_errors=True,
    )

    mysql_host: str = "127.0.0.1"
    mysql_port: int = Field(default=3307, ge=1, le=65535)
    mysql_database: str = "ecommerce_dw"
    mysql_reader_user: str = "ecommerce_reader"
    mysql_reader_password: SecretStr

    @field_validator("mysql_reader_password")
    @classmethod
    def validate_reader_password(cls, value: SecretStr) -> SecretStr:
        password = value.get_secret_value()

        if not password.strip() or password.lower().startswith("replace_"):
            raise ValueError(
                "Set MYSQL_READER_PASSWORD to your reader account password."
            )

        return value


class MetadataSettings(Settings):
    metadata_database: str = "ecommerce_meta"
    metadata_writer_user: str = "ecommerce_meta_writer"
    metadata_writer_password: SecretStr

    @field_validator("metadata_writer_password")
    @classmethod
    def validate_metadata_password(cls, value: SecretStr) -> SecretStr:
        password = value.get_secret_value()

        if not password.strip() or password.lower().startswith("replace_"):
            raise ValueError(
                "Set METADATA_WRITER_PASSWORD to your metadata account password."
            )

        return value