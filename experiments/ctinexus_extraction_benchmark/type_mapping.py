from __future__ import annotations

import re

from .constants import CTINEXUS_ENTITY_TYPES

_DIRECT = {value.casefold(): value for value in CTINEXUS_ENTITY_TYPES}
_ALIASES = {
    "threat_actor": "Attacker",
    "threat_actor_group": "Attacker",
    "actor": "Attacker",
    "user_group": "Attacker",
    "organization_group": "Organization",
    "organization_or_group": "Organization",
    "country": "Location",
    "geography": "Location",
    "region": "Location",
    "malware_family": "Malware",
    "malicious_code": "Malware",
    "indicator_file": "Indicator:File",
    "file": "Indicator:File",
    "url": "Indicator:URL",
    "domain": "Indicator:Domain",
    "exploit_target": "Exploit Target",
    "endpoint": "Infrastructure",
    "endpoint_or_server": "Infrastructure",
    "network_infrastructure": "Infrastructure",
    "command_and_control_server": "Infrastructure",
    "command_and_control_infrastructure": "Infrastructure",
}


def _key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.casefold()).strip("_")


def map_production_entity_type(value: str) -> str | None:
    direct = _DIRECT.get(value.strip().casefold())
    if direct:
        return direct
    return _ALIASES.get(_key(value))
