from enum import IntEnum, IntFlag, unique

@unique
class Privileges(IntFlag):
    """Server side user privileges."""

    Normal      = 1 << 0
    Verified    = 1 << 1

    Whitelisted = 1 << 2

    Supporter   = 1 << 4
    Premium     = 1 << 5

    Alumni      = 1 << 7

    Tournament  = 1 << 10
    Nominator   = 1 << 11
    Mod         = 1 << 12
    Admin       = 1 << 13
    Dangerous   = 1 << 14

    Donator = Supporter | Premium
    Staff = Mod | Admin | Dangerous

@unique
class ClientPrivileges(IntFlag):
    """Client side user privileges."""

    Player     = 1 << 0
    Moderator  = 1 << 1
    Supporter  = 1 << 2
    Owner      = 1 << 3
    Developer  = 1 << 4
    Tournament = 1 << 5