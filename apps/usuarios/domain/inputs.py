from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ListMembersInput:
    organization_id: int
    include_inactive: bool = False


@dataclass
class CreateMemberInput:
    organization_id: int
    email: str
    first_name: str = ""
    last_name: str = ""
    role: str = "member"


@dataclass
class UpdateMemberInput:
    organization_id: int
    member_id: int
    first_name: str
    last_name: str
    role: str
    is_active: bool


@dataclass
class ToggleMemberActiveInput:
    organization_id: int
    member_id: int
    active: bool
