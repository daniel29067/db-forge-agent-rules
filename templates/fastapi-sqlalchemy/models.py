from typing import List
from sqlalchemy import Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base, AuditMixin

# Explicit Junction Table for Post <-> Tag Many-to-Many relationship
class PostTag(Base, AuditMixin):
    __tablename__ = "posts_tags"

    # Composite Primary Key or Composite Unique Index
    post_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("posts.id", ondelete="CASCADE"),
        primary_key=True
    )
    tag_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True
    )

    # Explicit relationships to junction metadata if needed
    post: Mapped["Post"] = relationship(back_populates="post_tags")
    tag: Mapped["Tag"] = relationship(back_populates="tag_posts")


class User(Base, AuditMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    # 1-to-N Relationship (User -> Posts)
    posts: Mapped[List["Post"]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan"
    )


class Post(Base, AuditMixin):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    author_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True  # Index foreign keys to optimize joins and operations
    )

    # Relationships
    author: Mapped["User"] = relationship(back_populates="posts")
    
    # N-to-N through explicit junction model
    post_tags: Mapped[List["PostTag"]] = relationship(
        back_populates="post",
        cascade="all, delete-orphan"
    )


class Tag(Base, AuditMixin):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    # Relationships
    tag_posts: Mapped[List["PostTag"]] = relationship(
        back_populates="tag",
        cascade="all, delete-orphan"
    )
