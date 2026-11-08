import requests
from requests import JSONDecodeError
from serde import InternalTagging
from serde.json import to_dict
from src.backend.label_data import LabelType
from src.util.logger import get_logger
from urllib.parse import urlparse

logger = get_logger()


class NetworkError(Exception):
    pass


class LoginError(Exception):
    pass


class UploadedLabel:
    def __init__(self, public_url: str, public_observation_url: str, label: LabelType):
        self.public_url = public_url
        self.public_observation_url = public_observation_url
        self.label = label


class KalmarApiClient:
    LOGIN_URL   = '/api/login/'
    LOGOUT_URL  = '/api/logout/'
    PROFILE_URL = '/api/member/'   # Adjust if the profile endpoint path differs
    LABEL_URL   = '/api/labels/'   # Update when label endpoint is confirmed

    def __init__(self, base_url: str):
        url = urlparse(base_url)
        if not url.scheme or not url.netloc:
            raise Exception("API URL is invalid. Must be on the form 'http(s)://...'.")
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()

    # ── Auth helpers ──────────────────────────────────────────────────────────

    def _update_csrf(self) -> None:
        """Copy the csrftoken cookie into request headers after login."""
        token = self.session.cookies.get('csrftoken')
        if token:
            self.session.headers.update({
                'X-CSRFToken': token,
                'Referer': self.base_url,
            })

    # ── Public API ────────────────────────────────────────────────────────────

    def login_member(self, username: str, password: str) -> dict:
        """
        Authenticate with the Django backend and return the profile dict.
        Raises LoginError on bad credentials or unverified email.
        Raises NetworkError on connection problems.
        """
        try:
            r = self.session.post(
                self.base_url + self.LOGIN_URL,
                json={'email': username, 'password': password},
                timeout=5,
            )
        except requests.exceptions.RequestException:
            logger.exception('Network error during login')
            raise NetworkError()

        if r.status_code == 401:
            raise LoginError('Incorrect username or password')
        if r.status_code == 403:
            raise LoginError('Email address has not been verified')
        if r.status_code == 400:
            raise LoginError('Missing username or password')
        if not r.ok:
            raise LoginError(f'Login failed (HTTP {r.status_code})')

        self._update_csrf()

        try:
            profile_r = self.session.get(self.base_url + self.PROFILE_URL, timeout=5)
        except requests.exceptions.RequestException:
            logger.exception('Network error fetching profile')
            raise NetworkError()

        if not profile_r.ok:
            raise NetworkError('Could not fetch profile after login')

        try:
            return profile_r.json()
        except JSONDecodeError:
            raise NetworkError('Invalid JSON in profile response')

    def logout(self) -> None:
        try:
            self.session.post(self.base_url + self.LOGOUT_URL, timeout=5)
        except Exception:
            pass
        self.session = requests.Session()

    def post_label(self, label: LabelType) -> UploadedLabel:
        """
        Upload a label to the backend.
        NOTE: Update LABEL_URL to the correct path when the endpoint is available.
        """
        json_data = to_dict(label, InternalTagging('type', LabelType))
        try:
            r = self.session.post(
                self.base_url + self.LABEL_URL,
                json=json_data,
                timeout=5,
            )
        except requests.exceptions.RequestException:
            logger.exception('Network error uploading label')
            raise NetworkError('Could not upload label')

        if not r.ok:
            logger.error(f'Failed to upload label: {r.text}')
            raise NetworkError('Backend rejected label upload')

        data = r.json().get('data', {})
        return UploadedLabel(
            public_url=data.get('public_url', ''),
            public_observation_url=data.get('public_observation_url', ''),
            label=label,
        )
