"""Repository boundary for opportunity persistence."""

from typing import Protocol

from app.schemas.opportunities import OpportunityRead, OpportunitySearchParams


class OpportunityRepository(Protocol):
    async def search(self, params: OpportunitySearchParams) -> list[OpportunityRead]:
        """Return opportunities matching the student's filters and search query."""
