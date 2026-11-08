from typing import Any
from dataclasses import dataclass
import typing
from logging import getLogger

if typing.TYPE_CHECKING:
    from src.backend.makeradmin import KalmarApiClient

logger = getLogger('memberbooth')


class BackendParseError(KeyError):
    pass


@dataclass(frozen=True)
class Member:
    first_name: str
    last_name: str
    member_number: int   # maps to user.id from the profile response
    email: str

    def get_name(self) -> str:
        return f'{self.first_name} {self.last_name}'

    def __str__(self) -> str:
        return f'#{self.member_number}, "{self.get_name()}"'

    @classmethod
    def from_profile(cls, data: dict[str, Any]) -> 'Member':
        """Build a Member from a ProfileDetail API response dict."""
        try:
            return cls(
                first_name=data['firstName'],
                last_name=data['lastName'],
                member_number=data['id'],
                email=data['email'],
            )
        except KeyError as e:
            raise BackendParseError(f'Missing field in profile response: {e}')

    @classmethod
    def from_login(cls, client: 'KalmarApiClient', username: str, password: str) -> 'Member':
        """Authenticate and return the logged-in Member."""
        profile = client.login_member(username, password)
        return cls.from_profile(profile)
