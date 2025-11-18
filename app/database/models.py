from datetime import datetime
from enum import StrEnum

from sqlalchemy import TIMESTAMP, Boolean, ForeignKey, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class PRStatus(StrEnum):
    """Статус Pull Request."""

    OPEN = 'OPEN'
    MERGED = 'MERGED'


class Team(Base):
    """Модель команды."""

    __tablename__ = 'teams'

    team_name: Mapped[str] = mapped_column(String(255), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=func.now())

    members: Mapped[list['User']] = relationship('User', back_populates='team')


class User(Base):
    """Модель пользователя (участника команды)."""

    __tablename__ = 'users'

    user_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default='true')
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=func.now())
    team_name: Mapped[str] = mapped_column(
        String(255),
        ForeignKey('teams.team_name', ondelete='CASCADE'),
        nullable=False,
    )

    team: Mapped['Team'] = relationship('Team', back_populates='members')
    authored_prs: Mapped[list['PullRequest']] = relationship('PullRequest', back_populates='author')
    assigned_reviews: Mapped[list['PullRequestReviewer']] = relationship(
        'PullRequestReviewer', back_populates='reviewer'
    )


class PullRequest(Base):
    """Модель Pull Request."""

    __tablename__ = 'pull_requests'

    pull_request_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    pull_request_name: Mapped[str] = mapped_column(String(500), nullable=False)
    author_id: Mapped[str] = mapped_column(String(255), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=PRStatus.OPEN.value)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=func.now())
    merged_at: Mapped[datetime | None] = mapped_column(TIMESTAMP, nullable=True)

    author: Mapped['User'] = relationship('User', back_populates='authored_prs')
    reviewer_assignments: Mapped[list['PullRequestReviewer']] = relationship(
        'PullRequestReviewer', back_populates='pull_request', cascade='all, delete-orphan'
    )


class PullRequestReviewer(Base):
    """Связующая таблица для назначенных ревьюверов PR (многие-ко-многим)."""

    __tablename__ = 'pull_request_reviewers'

    assigned_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=func.now())
    pull_request_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey('pull_requests.pull_request_id', ondelete='CASCADE'),
        primary_key=True,
    )
    user_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey('users.user_id', ondelete='CASCADE'),
        primary_key=True,
    )

    pull_request: Mapped['PullRequest'] = relationship('PullRequest', back_populates='reviewer_assignments')
    reviewer: Mapped['User'] = relationship('User', back_populates='assigned_reviews')
