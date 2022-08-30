# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Iterable, List, Optional, Tuple
from uuid import UUID

__all__ = tuple(["Respondent"])


@dataclass(frozen=True, order=True, slots=True)
class Respondent:
    """
    A class describing OpenMedia respodent
    """

    openmedia_id: str
    given_name: str
    family_name: Optional[str]
    affiliation: str
    gender: int
    foreigner: int
    labels: List[str]
    matching_ids: List[str]
