# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Any, Mapping


def _defaultdict_of_sets() -> dict[str, set[Any]]:
    return defaultdict(set)


def _defaultdict_of_defaultdict_of_sets() -> dict[str, dict[str, set[Path]]]:
    return defaultdict(_defaultdict_of_sets)


def _defaultdict_of_dict() -> dict[Path, dict[str, str]]:
    return defaultdict(dict)


@dataclass
class FileIndex:
    paths_by_tags: dict[str, dict[str, set[Path]]] = field(default_factory=_defaultdict_of_defaultdict_of_sets)
    tags_by_paths: dict[Path, dict[str, str]] = field(default_factory=_defaultdict_of_dict)

    @cached_property
    def paths(self) -> set[Path]:
        return set(self.tags_by_paths.keys())

    def _get_phenotypes_without_key(self, key: str) -> set[Path]:
        if key not in self.paths_by_tags:
            return self.paths.copy()
        else:
            cache = self.__dict__.setdefault("_phenotypes_without_key", dict())
            phenotypes = cache.get(key)
            if phenotypes is None:
                phenotypes = self.paths.difference(*self.paths_by_tags[key].values())
                cache[key] = phenotypes
            return phenotypes

    def _invalidate_caches(self) -> None:
        if "phenotypes" in self.__dict__:
            del self.__dict__["phenotypes"]
        if "_phenotypes_without_key" in self.__dict__:
            del self.__dict__["_phenotypes_without_key"]

    def get(self, **tags: str | None) -> set[Path]:
        """
        Find all paths that match the query tags.

        Args:
            **tags: A dictionary of tags to match against. The keys are the tag names
                    and the values are the tag values. Pass a value of `None` to
                    select paths without that tag.

        Returns:
            A set of `Path` objects that match all the specified tags.
        """

        matches: set[Path] | None = None
        for key, query in tags.items():
            if key not in self.paths_by_tags:
                return set()

            values = self.paths_by_tags[key]
            if query is None:
                paths = self._get_phenotypes_without_key(key)
            elif query in values:
                paths = values[query]
            else:
                return set()

            if matches is not None:
                matches.intersection_update(paths)
            else:
                matches = paths.copy()

        if not matches:
            return set()
        else:
            return matches

    def get_tags(self, path: Path) -> Mapping[str, str | None]:
        if path in self.tags_by_paths:
            return self.tags_by_paths[path]
        else:
            return dict()

    def get_tag_value(self, path: Path, key: str) -> str | None:
        return self.get_tags(path).get(key)

    def set_tag_value(self, path: Path, key: str, value: str) -> None:
        # remove previous value
        if self.get_tag_value(path, key) is not None:
            previous_value = self.tags_by_paths[path].pop(key)
            self.paths_by_tags[key][previous_value].remove(path)
        if value is not None:
            self.tags_by_paths[path][key] = value
            self.paths_by_tags[key][value].add(path)

    def get_tag_mapping(self, key: str) -> Mapping[str, set[Path]]:
        return self.paths_by_tags[key]

    def get_tag_values(self, key: str, paths: set[Path] | None = None) -> set[str]:
        if key not in self.paths_by_tags:
            return set()

        if paths is None:
            return set(self.paths_by_tags[key].keys())

        return set(k for k, v in self.paths_by_tags[key].items() if not paths.isdisjoint(v))

    def get_associated_paths(self, path: Path, **tags: str) -> set[Path]:
        matches = self.get(**tags)
        for key, value in self.get_tags(path).items():
            if key == "extension":
                continue
            valid = self.get(**{key: value}) | self.get(**{key: None})
            matches &= valid
        return matches
