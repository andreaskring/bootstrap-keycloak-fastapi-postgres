from typing import Any

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWKClient, decode, InvalidTokenError
from pydantic import ValidationError
from starlette.status import HTTP_401_UNAUTHORIZED
from structlog import get_logger

logger = get_logger()


class AuthenticationError(Exception):
    """
    Raised if the user is not authenticated.
    """

    def __init__(self, exc: Exception):
        self.__exc = exc

    @property
    def exc(self) -> Exception:
        return self.__exc

    def is_client_side_error(self) -> bool:
        """
        Return True if the error is a client side error (e.g. an expired
        token) and False otherwise (e.g. if Keycloak is unreachable)
        """
        if isinstance(self.__exc, InvalidTokenError):
            return True
        if isinstance(self.__exc, ValidationError):
            return True
        if (
            isinstance(self.__exc, HTTPException)
            and self.__exc.status_code == HTTP_401_UNAUTHORIZED
        ):
            return True
        return False


def get_auth_dependency(
    host: str,
    port: int,
    realm: str,
    http_schema: str,
    alg: str = "RS256",
    verify_audience: bool = True,
    audience: str | list[str] | None = None,
):
    keycloak_base_url = f"{http_schema}://{host}:{port}/auth"

    # URI for obtaining JSON Web Key Set (JWKS), i.e. the public Keycloak key
    jwks_uri = keycloak_base_url + f"/realms/{realm}/protocol/openid-connect/certs"
    token_url_path = keycloak_base_url + f"/realms/{realm}/protocol/openid-connect/token"

    # JWKS client for fetching and caching JWKS
    jwks_client = PyJWKClient(jwks_uri)

    # For getting and parsing the Authorization header
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl=token_url_path)

    async def keycloak_auth(token: str = Depends(oauth2_scheme)) -> dict[str, Any]:
        """
        Ensure the caller has a valid OIDC token, i.e. that the Authorization
        header is set with a valid bearer token.

        :param token: encoded Keycloak token
        :return: selected JSON values from the Keycloak token

        **Example return value**

        .. sourcecode:: json

            {
                "acr": "1",
                "allowed-origins": ["http://localhost:5001"],
                "azp": "mo",
                "email": "bruce@kung.fu",
                "email_verified": false,
                "exp": 1621779689,
                "family_name": "Lee",
                "given_name": "Bruce",
                "iat": 1621779389,
                "iss": "http://localhost:8081/auth/realms/mo",
                "jti": "25dbb58d-b3cb-4880-8b51-8b92ada4528a",
                "name": "Bruce Lee",
                "preferred_username": "bruce",
                "realm_access": {
                    "roles": [
                      "admin"
                  ]
                },
                "scope": "email profile",
                "session_state": "d94f8dc3-d930-49b3-a9dd-9cdc1893b86a",
                "sub": "c420894f-36ba-4cd5-b4f8-1b24bd8c53db",
                "typ": "Bearer",
                "uuid": "99e7b256-7dfa-4ee8-95c6-e3abe82e236a"
            }

        """

        try:
            # Get the public signing key from Keycloak. The JWKS client uses an
            # lru_cache, so it will not make an HTTP request to Keycloak each time
            # get_signing_key_from_jwt() is called.

            signing = jwks_client.get_signing_key_from_jwt(token)

            # The jwt.decode() method raises an exception (e.g.
            # InvalidSignatureError, ExpiredSignatureError,...) in case the OIDC
            # token is invalid. These exceptions will be caught by the
            # auth_exception_handler below which is used by the FastAPI app.

            # The audience verification can be disabled (aud
            # claim in the token) when all services in the stack trust
            # each other
            # (see https://www.keycloak.org/docs/latest/server_admin/index.html#_audience)
            decoded_token: dict[str, Any] = decode(
                token,
                signing.key,
                algorithms=[alg],
                audience=audience,
                options={"verify_aud": verify_audience},
                leeway=5,
            )

            return decoded_token

        except Exception as err:
            raise AuthenticationError(err)

    return keycloak_auth
