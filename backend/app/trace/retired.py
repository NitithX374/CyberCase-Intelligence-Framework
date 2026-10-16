from __future__ import annotations


def without_retired(data: object, retired: frozenset[str]) -> object:
    if isinstance(data, dict) and not retired.isdisjoint(data):
        return {key: value for key, value in data.items() if key not in retired}
    return data


__all__ = ["without_retired"]
