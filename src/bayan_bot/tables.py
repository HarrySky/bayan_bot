from __future__ import annotations

from typing import Final

from sqlalchemy import (  # type: ignore[import]
    ARRAY,
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Integer,
    MetaData,
)
from sqlalchemy.orm import declarative_base  # type: ignore[import]
from sqlalchemy.sql import func  # type: ignore[import]

metadata: Final = MetaData()
Base: Final = declarative_base(metadata=metadata)


class State(Base):  # type: ignore[misc,valid-type]
    __tablename__ = "state"

    id = Column(Integer, primary_key=True)
    dt_added = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    offset = Column(BigInteger, nullable=False, server_default="0")


class ImageHash(Base):  # type: ignore[misc,valid-type]
    __tablename__ = "image_hashes"

    id = Column(Integer, primary_key=True)
    hash = Column(ARRAY(Boolean, dimensions=2), nullable=False)
    dt_added = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
