from typing import Any
from src.backend.label_data import LabelType
from src.backend.makeradmin import UploadedLabel, LoginError


MOCK_PROFILE = {
    'id': 9999,
    'email': 'test@example.com',
    'firstName': 'Firstname',
    'lastName': 'Lastname',
    'fullName': 'Firstname Lastname',
}

MOCK_LABEL_URL = 'https://mock.com/labels/'


class KalmarApiClient:
    """Mock client for development / testing — no real HTTP calls are made."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass

    def login_member(self, username: str, password: str) -> dict:
        # Accept any non-empty credentials in mock mode
        if not username or not password:
            raise LoginError('Username and password are required')
        return MOCK_PROFILE

    def logout(self) -> None:
        pass

    def post_label(self, label: LabelType) -> UploadedLabel:
        return UploadedLabel(
            public_url=f'{MOCK_LABEL_URL}{label.base.id}',
            public_observation_url=f'{MOCK_LABEL_URL}{label.base.id}/observe',
            label=label,
        )
