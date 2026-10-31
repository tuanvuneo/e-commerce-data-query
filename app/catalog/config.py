from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ConfigEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")


class TableConfig(ConfigEntry):
    role: Literal["dimension", "fact"]
    grain: str = Field(min_length=1)
    description: str = Field(min_length=1)


class ColumnConfig(ConfigEntry):
    description: str | None = Field(default=None, min_length=1)
    aliases: list[str] = Field(default_factory=list)
    allowed_values: list[str] = Field(default_factory=list)


class MetricConfig(ConfigEntry):
    base_table: str = Field(min_length=1)
    description: str = Field(min_length=1)
    unit: str = Field(min_length=1)
    sql_expression: str = Field(min_length=1)
    filters: dict[str, str]
    referenced_columns: list[str] = Field(min_length=1)
    aliases: list[str] = Field(default_factory=list)


class CatalogConfig(ConfigEntry):
    tables: dict[str, TableConfig] = Field(min_length=1)
    columns: dict[str, ColumnConfig] = Field(default_factory=dict)
    metrics: dict[str, MetricConfig] = Field(min_length=1)