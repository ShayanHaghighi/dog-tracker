from typing import Any
from ..utils.logger import Logger
from requests import post, codes, Response
from ..utils.config import config

logger = Logger(__name__)

V1_DOMAIN = "https://smartdevicemanagement.googleapis.com/v1/"
TOKEN_DOMAIN = "https://www.googleapis.com/oauth2/v4/token"


class SdmClient:
    def __init__(self):
        pass

    def make_request(
        self,
        endpoint: str,
        params: dict[str, Any] = {},
        payload: dict[str, Any] = {},
        headers: dict[str, Any] = {},
    ) -> Response:
        response = post(
            url=f"{V1_DOMAIN}{endpoint}",
            params=params,
            headers=headers or {"Authorization": f"Bearer {config.access_token}"},
            json=payload,
        )

        if response.status_code == 401:
            logger.warning("access token expired, refreshing")
            self.refresh_access_token()
            response = post(
                url=f"{V1_DOMAIN}{endpoint}",
                params=params,
                headers=headers or {"Authorization": f"Bearer {config.access_token}"},
                json=payload,
            )

        return response

    def refresh_access_token(self) -> None:
        params = {
            "client_id": config.client_id,
            "client_secret": config.client_secret,
            "refresh_token": config.refresh_token,
            "grant_type": "refresh_token",
            "redirect_uri": "https://www.google.com",
        }

        response = post(TOKEN_DOMAIN, params=params)

        if response.status_code == codes.ok:
            logger.info("access token successfully refreshed")

        response_dict = response.json()
        access_token = response_dict["access_token"]
        config.update_access_token(access_token)
