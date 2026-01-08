from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ListMembersInput:
    organization_id: int
    include_inactive: bool = False
    search: str | None = None
    role: str | None = None
    is_active: bool | None = None


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


@dataclass
class ExportMembersInput:
    organization_id: int
    include_inactive: bool = False
    search: str | None = None
    role: str | None = None
    is_active: bool | None = None
    format: str = "csv"
