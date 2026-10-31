from sqlalchemy import JSON, Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class CatalogBase(DeclarativeBase):
    pass

class CatalogTable(CatalogBase):
    __tablename__ = "catalog_table"
    __table_args__ = {"mysql_engine": "InnoDB"}

    name: Mapped[str] = mapped_column(String(64), primary_key=True)
    source_database: Mapped[str] = mapped_column(String(64))
    role: Mapped[str] = mapped_column(String(20))
    grain: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    primary_key: Mapped[list[str]] = mapped_column(JSON)

class CatalogColumn(CatalogBase):
    __tablename__ = "catalog_column"
    __table_args__ = {"mysql_engine": "InnoDB"}

    id: Mapped[str] = mapped_column(String(129), primary_key=True)
    table_name: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("catalog_table.name"),
    )
    name: Mapped[str] = mapped_column(String(64))
    data_type: Mapped[str] = mapped_column(String(128))
    nullable: Mapped[bool] = mapped_column(Boolean)
    ordinal_position: Mapped[int] = mapped_column(Integer)
    is_primary_key: Mapped[bool] = mapped_column(Boolean)
    description: Mapped[str] = mapped_column(Text)
    aliases: Mapped[list[str]] = mapped_column(JSON)
    allowed_values: Mapped[list[str]] = mapped_column(JSON)

class CatalogRelationship(CatalogBase):
    __tablename__ = "catalog_relationship"
    __table_args__ = {"mysql_engine": "InnoDB"}

    id: Mapped[str] = mapped_column(String(129), primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    source_table: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("catalog_table.name"),
    )
    target_table: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("catalog_table.name"),
    )
    source_columns: Mapped[list[str]] = mapped_column(JSON)
    target_columns: Mapped[list[str]] = mapped_column(JSON)

class CatalogMetric(CatalogBase):
    __tablename__ = "catalog_metric"
    __table_args__ = {"mysql_engine": "InnoDB"}

    name: Mapped[str] = mapped_column(String(64), primary_key=True)
    base_table: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("catalog_table.name"),
    )
    description: Mapped[str] = mapped_column(Text)
    unit: Mapped[str] = mapped_column(String(20))
    sql_expression: Mapped[str] = mapped_column(Text)
    filters: Mapped[dict[str, str]] = mapped_column(JSON)
    referenced_columns: Mapped[list[str]] = mapped_column(JSON)
    aliases: Mapped[list[str]] = mapped_column(JSON)