# -*- coding: utf-8 -*-

import json
from dataclasses import dataclass
from typing import Iterable, List, Optional, Tuple
from uuid import UUID

__all__ = tuple(["Respondent", "Person",])


class Respondent(object):
    """
    A class describing OpenMedia respodent
    """

    def __init__(
        self,
        openmedia_id: str,
        given_name: str,
        family_name: Optional[str],
        affiliation: str,
        gender: int,
        foreigner: int,
        labels: List[str],
        matching_ids: List[str],
    ):
        self._openmedia_id = openmedia_id
        self._given_name = given_name
        self._family_name = family_name
        self._affiliation = affiliation
        self._gender = gender
        self._foreigner = foreigner
        self._labels = labels
        self._matching_ids = matching_ids

    def __hash__(self) -> int:
        return hash(self._openmedia_id)

    def __eq__(self, that) -> bool:
        return self._openmedia_id == that._openmedia_id

    def asdict(self):
        return {
            "openmedia_id": self._openmedia_id,
            "given_name": self._given_name,
            "family_name": self._family_name,
            "affiliation": self._affiliation,
            "gender": self._gender,
            "foreigner": self._foreigner,
            "labels": self._labels,
            "matching_ids": self._matching_ids,
        }

    # def serialize(self, values_only = False):
    #    if values_only:
    #        return self.__dict__.values()
    #    return self.__dict__

    # def serialize(self):
    #    return {
    #        "openmedia_id": self.openmedia_id(),
    #        "given_name": self.given_name(),
    #        "family_name": self.family_name(),
    #        "affiliation": self.affiliation(),
    #       "gender": self.gender(),
    #        "foreigner": self.foreigner(),
    #        "labels": self.labels(),
    #        "matching_ids": self.matching_ids(),
    #    }

    @property
    def openmedia_id(self) -> str:
        return self._openmedia_id

    @property
    def given_name(self) -> str:
        return self._given_name

    @property
    def family_name(self) -> str | None:
        return self._family_name

    @property
    def affiliation(self) -> str:
        return self._affiliation

    @property
    def gender(self) -> int:
        return self._gender

    @property
    def foreigner(self) -> int:
        return self._foreigner

    @property
    def labels(self) -> List[str]:
        return self._labels

    @property
    def matching_ids(self) -> List[str]:
        return self._matching_ids

    def add_matching_id(self, matching_id: str):
        self._matching_ids.append(matching_id)


Person = Respondent
