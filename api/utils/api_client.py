from requests import Session, Response
from requests.adapters import HTTPAdapter
from requests.auth import HTTPBasicAuth
from urllib3.util import Retry


class APIClient:

    """A client for making HTTP requests with retry logic."""

    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url
        self.auth = HTTPBasicAuth(username, password)
        self.session = self._create_session()

    def _create_session(self) -> Session:
        """
        Creates a requests session with retry logic.

        Returns:
            Session: A configured requests session with retry capabilities.
        """
        session = Session()
        retry_strategy = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount('https://', adapter)
        return session

    def get(self, endpoint: str, params: dict = None) -> Response:
        """
        Sends a GET request to the specified endpoint.

        Args:
            endpoint (str): The API endpoint to send the GET request to.
            params (dict, optional): Optional parameters to include in the request.

        Returns:
            Response: The response object from the GET request.
        """ # noqa
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.get(url, params=params,
                                    auth=self.auth, verify=False, timeout=10)
        return response
