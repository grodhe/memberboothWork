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
    PROFILE_URL = '/api/profile/'
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
        login_url = self.base_url + self.LOGIN_URL
        logger.info(f'POST {login_url}')
        try:
            r = self.session.post(
                login_url,
                json={'email': username, 'password': password},
                timeout=5,
            )
        except requests.exceptions.RequestException:
            logger.exception('Network error during login POST')
            raise NetworkError()

        logger.info(f'Login response: HTTP {r.status_code}')

        if r.status_code == 401:
            raise LoginError('Wrong email or password')
        if r.status_code == 403:
            raise LoginError('Email not verified.\nCheck your inbox.')
        if r.status_code == 400:
            raise LoginError('Enter email and password')
        if not r.ok:
            raise LoginError(f'Login failed ({r.status_code})')

        self._update_csrf()

        profile_url = self.base_url + self.PROFILE_URL
        logger.info(f'GET {profile_url}')
        try:
            profile_r = self.session.get(profile_url, timeout=5)
        except requests.exceptions.RequestException:
            logger.exception('Network error fetching profile')
            raise NetworkError()

        if not profile_r.ok:
            logger.error(f'Profile fetch failed: HTTP {profile_r.status_code} — {profile_r.text[:500]}')
            raise NetworkError(f'Could not fetch profile (HTTP {profile_r.status_code})')

        try:
            return profile_r.json()
        except JSONDecodeError:
            logger.error(f'Profile response was not valid JSON: {profile_r.text[:500]}')
            raise NetworkError('Invalid JSON in profile response')

    def logout(self) -> None:
        try:
            self.session.post(self.base_url + self.LOGOUT_URL, timeout=5)
        except Exception:
            pass
        self.session = requests.Session()

    def post_label(self, label: LabelType) -> UploadedLabel:
        """
        TODO: upload label to backend once the correct endpoint is known.
        For now, create the UploadedLabel locally so printing works without it.
        """
        logger.info('Label upload skipped (endpoint not yet configured) - printing locally')
        return UploadedLabel(
            public_url='',
            public_observation_url='',
            label=label,
        )
