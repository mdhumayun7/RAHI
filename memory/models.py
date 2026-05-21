"""
RAHI Memory Models
===================
SQLAlchemy ORM models mapping to PostgreSQL tables.
These match the schema we created in memory/schemas/01_init.sql
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
from memory.database import Base


class User(Base):
    __tablename__ = "users"

    id:          Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name:        Mapped[str]       = mapped_column(String(100), nullable=False)
    email:       Mapped[str]       = mapped_column(String(200), unique=True, nullable=True)
    created_at:  Mapped[datetime]  = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    preferences: Mapped[dict]      = mapped_column(JSONB, default=dict)

    conversations: Mapped[list["Conversation"]] = relationship(back_populates="user")
    memories:      Mapped[list["Memory"]]       = relationship(back_populates="user")

    def __repr__(self):
        return f"<User name={self.name}>"


class Conversation(Base):
    __tablename__ = "conversations"

    id:         Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id:    Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    role:       Mapped[str]       = mapped_column(String(20), nullable=False)   # user | assistant | system
    content:    Mapped[str]       = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime]  = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    metadata_:  Mapped[dict]      = mapped_column("metadata", JSONB, default=dict)

    user: Mapped["User"] = relationship(back_populates="conversations")

    def __repr__(self):
        return f"<Conversation role={self.role} content={self.content[:30]}>"


class Memory(Base):
    __tablename__ = "memories"

    id:          Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id:     Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    content:     Mapped[str]       = mapped_column(Text, nullable=False)
    embedding:   Mapped[list]      = mapped_column(Vector(384), nullable=True)   # 384 = all-MiniLM-L6-v2
    memory_type: Mapped[str]       = mapped_column(String(50), default="semantic")
    importance:  Mapped[float]     = mapped_column(Float, default=0.5)
    created_at:  Mapped[datetime]  = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    metadata_:   Mapped[dict]      = mapped_column("metadata", JSONB, default=dict)

    user: Mapped["User"] = relationship(back_populates="memories")

    def __repr__(self):
        return f"<Memory type={self.memory_type} content={self.content[:40]}>"


class AuditLog(Base):
    __tablename__ = "audit_log"

    id:         Mapped[int]            = mapped_column(primary_key=True, autoincrement=True)
    user_id:    Mapped[uuid.UUID]      = mapped_column(ForeignKey("users.id"), nullable=True)
    agent:      Mapped[str]            = mapped_column(String(100), nullable=True)
    action:     Mapped[str]            = mapped_column(Text, nullable=False)
    payload:    Mapped[dict]           = mapped_column(JSONB, nullable=True)
    result:     Mapped[str]            = mapped_column(Text, nullable=True)
    risk_level: Mapped[str]            = mapped_column(String(20), default="low")
    created_at: Mapped[datetime]       = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))