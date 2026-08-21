"""Merge the existing schema and pgvector migration branches.

Revision ID: 20260821_merge_deployment_heads
Revises: 20260718_0001, 20260813_enable_pgvector
Create Date: 2026-08-21
"""

from collections.abc import Sequence


revision: str = "20260821_merge_deployment_heads"
down_revision: tuple[str, str] = ("20260718_0001", "20260813_enable_pgvector")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Merge point only; never alters either already-deployed branch."""


def downgrade() -> None:
    """Merge point only; no schema change to reverse."""
