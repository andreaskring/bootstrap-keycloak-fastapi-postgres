import asyncio
import unittest.mock
from datetime import datetime

import jwt
from cryptography.hazmat.primitives import serialization
from fastapi.exceptions import HTTPException
from jwt.exceptions import ExpiredSignatureError
from jwt.exceptions import InvalidAudienceError
from jwt.exceptions import InvalidSignatureError
from jwt.exceptions import InvalidTokenError
from jwt.exceptions import PyJWTError
from starlette.status import HTTP_401_UNAUTHORIZED
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from backend.auth import AuthenticationError, get_auth_dependency


class TestOIDC(unittest.TestCase):
    def setUp(self) -> None:
        # Used for mocking the Keycloak public key
        with open("tests/mocking/auth/jwtRS256.key.pub", "rb") as fp:
            public_key = serialization.load_pem_public_key(fp.read())
        self.signing = jwt.PyJWT({"kty": "RSA"})
        # self.signing.key = public_key
        setattr(self.signing, "key", public_key)

        # Used for mocking the Keycloak private key
        with open("tests/mocking/auth/jwtRS256.key", "rb") as fp:
            self.private_key = fp.read()

        # Used for mocking the OIDC token
        self.parsed_token = {
            "acr": "1",
            "allowed-origins": ["http://localhost:5001"],
            "azp": "mo",
            "email": "bruce@kung.fu",
            "email_verified": False,
            "exp": int(datetime.now().timestamp()) + 300,
            "family_name": "Lee",
            "given_name": "Bruce",
            "iat": int(datetime.now().timestamp()),
            "iss": "http://localhost:8081/auth/realms/mo",
            "jti": "25dbb58d-b3cb-4880-8b51-8b92ada4528a",
            "name": "Bruce Lee",
            "preferred_username": "bruce",
            "scope": "email profile",
            "session_state": "d94f8dc3-d930-49b3-a9dd-9cdc1893b86a",
            "sub": "c420894f-36ba-4cd5-b4f8-1b24bd8c53db",
            "typ": "Bearer",
            "uuid": "99e7b256-7dfa-4ee8-95c6-e3abe82e236a",
        }

        self.auth = get_auth_dependency(
            host="keycloak",
            port=8080,
            realm="mo",
            http_schema="http",
        )

        # For the async tests
        self.loop = asyncio.get_event_loop()

    @staticmethod
    def generate_token(parsed_token: dict, key: str) -> str:
        """
        Generate a request containing an auth header with a OIDC Bearer token
        :param parsed_token: parsed token (see example above)
        :param key: The JWK to sign the token with
        """
        token = jwt.encode(parsed_token, key, algorithm="RS256")
        return token

    # def test_auth_exception_handler_return_401_for_client_side_error(self):
    #     exc = AuthenticationError(InvalidSignatureError())
    #      authentication_exception_handler = get_auth_exception_handler(get_logger())
    #
    #     self.assertEqual(
    #         HTTP_401_UNAUTHORIZED,
    #         authentication_exception_handler(None, exc).status_code,
    #     )
    #
    # def test_auth_exception_handler_return_500_for_server_side_error(self):
    #     exc = AuthenticationError(PyJWTError())
    #     authentication_exception_handler = get_auth_exception_handler(get_logger())
    #
    #     self.assertEqual(
    #         HTTP_500_INTERNAL_SERVER_ERROR,
    #         authentication_exception_handler(None, exc).status_code,
    #     )

    @unittest.mock.patch(
        "backend.auth.oidc.jwt.PyJWKClient.get_signing_key_from_jwt"
    )
    def test_auth_decodes_token(self, mock_get_signing_key_from_jwt):
        # Mock the public signing.key used in the auth function
        mock_get_signing_key_from_jwt.side_effect = [self.signing]

        # Create auth request with token signed by correct key
        token = TestOIDC.generate_token(self.parsed_token, self.private_key)

        actual_token = self.loop.run_until_complete(self.auth(token))

        self.assertEqual(self.parsed_token, actual_token)

    @unittest.mock.patch(
        "backend.auth.oidc.jwt.PyJWKClient.get_signing_key_from_jwt"
    )
    def test_leeway(self, mock_get_signing_key_from_jwt):
        # Mock the public signing.key used in the auth function
        mock_get_signing_key_from_jwt.side_effect = [self.signing]

        # Set "exp" to a slightly expired timestamp
        self.parsed_token["exp"] = int(datetime.now().timestamp()) - 3

        # Create auth request with token signed by correct key
        token = TestOIDC.generate_token(self.parsed_token, self.private_key)

        assert self.loop.run_until_complete(self.auth(token))

    @unittest.mock.patch(
        "backend.auth.oidc.jwt.PyJWKClient.get_signing_key_from_jwt"
    )
    def test_raise_exception_for_invalid_signature(
        self,
        mock_get_signing_key_from_jwt
    ):
        # Mock the public signing.key used in the auth function
        mock_get_signing_key_from_jwt.side_effect = [self.signing]

        with open("tests/mocking/auth/hackers-jwtRS256.key", "rb") as fp:
            hackers_key = fp.read()

        # Create auth request with token signed with hackers key
        token = TestOIDC.generate_token(self.parsed_token, hackers_key)

        with self.assertRaises(AuthenticationError) as err:
            self.loop.run_until_complete(self.auth(token))
            assert isinstance(err.exception.exc, InvalidSignatureError)

    @unittest.mock.patch(
        "backend.auth.oidc.jwt.PyJWKClient.get_signing_key_from_jwt"
    )
    def test_raise_exception_for_expired_token(
        self,
        mock_get_signing_key_from_jwt
    ):
        # Mock the public signing.key used in the auth function
        mock_get_signing_key_from_jwt.side_effect = [self.signing]

        # Set "exp" to an expired timestamp
        self.parsed_token["exp"] = int(datetime.now().timestamp()) - 6

        # Create auth request with token signed by correct key
        token = TestOIDC.generate_token(self.parsed_token, self.private_key)

        with self.assertRaises(AuthenticationError) as err:
            self.loop.run_until_complete(self.auth(token))
            assert isinstance(err.exception.exc, ExpiredSignatureError)

    @unittest.mock.patch(
        "backend.auth.oidc.jwt.PyJWKClient.get_signing_key_from_jwt"
    )
    def test_ensure_get_signing_from_jwt_called(
        self,
        mock_get_signing_key_from_jwt
    ):
        # Mock the public signing.key used in the auth function
        mock_get_signing_key_from_jwt.side_effect = [self.signing]
        token = TestOIDC.generate_token(self.parsed_token, self.private_key)

        self.loop.run_until_complete(self.auth(token))

        token = jwt.encode(
            self.parsed_token, self.private_key, algorithm="RS256"
        )

        mock_get_signing_key_from_jwt.assert_called_once_with(token)

    @unittest.mock.patch(
        "backend.auth.oidc.jwt.PyJWKClient.get_signing_key_from_jwt"
    )
    def test_exception_when_aud_in_token_and_audience_is_not_set(
        self, mock_get_signing_key_from_jwt
    ):
        # Mock the public signing.key used in the auth function
        mock_get_signing_key_from_jwt.side_effect = [self.signing]

        # Set aud in token
        self.parsed_token["aud"] = "mo"
        token = TestOIDC.generate_token(self.parsed_token, self.private_key)

        with self.assertRaises(AuthenticationError) as err:
            self.loop.run_until_complete(self.auth(token))
            assert isinstance(err.exception.exc, InvalidAudienceError)

    @unittest.mock.patch(
        "backend.auth.oidc.jwt.PyJWKClient.get_signing_key_from_jwt"
    )
    def test_token_accepted_when_aud_in_token_and_audience_is_set(
        self, mock_get_signing_key_from_jwt
    ):
        # Mock the public signing.key used in the auth function
        mock_get_signing_key_from_jwt.side_effect = [self.signing]

        # Set aud in token
        self.parsed_token["aud"] = "mo"
        token = TestOIDC.generate_token(self.parsed_token, self.private_key)

        auth = get_auth_dependency(
            host="keycloak",
            port=8080,
            realm="mo",
            http_schema="http",
            audience="mo",
        )

        assert self.loop.run_until_complete(auth(token))

    @unittest.mock.patch(
        "backend.auth.oidc.jwt.PyJWKClient.get_signing_key_from_jwt"
    )
    def test_token_accepted_when_aud_in_token_and_verify_aud_is_false(
        self, mock_get_signing_key_from_jwt
    ):
        # Mock the public signing.key used in the auth function
        mock_get_signing_key_from_jwt.side_effect = [self.signing]

        # Set aud in token
        self.parsed_token["aud"] = "mo"
        token = TestOIDC.generate_token(self.parsed_token, self.private_key)

        auth = get_auth_dependency(
            host="keycloak",
            port=8080,
            realm="mo",
            http_schema="http",
            verify_audience=False,
        )

        assert self.loop.run_until_complete(auth(token))


class TestAuthError(unittest.TestCase):
    """
    Test that the AuthError exception itself works as expected
    """

    def test_exception_set_correctly(self):
        exc = AuthenticationError(InvalidSignatureError())
        self.assertTrue(InvalidSignatureError, type(exc.exc))

    def test_is_client_side_error_true_for_invalid_token_error(self):
        exc = AuthenticationError(InvalidTokenError())
        self.assertTrue(exc.is_client_side_error())

    def test_is_client_side_error_true_for_http_exception_401(self):
        exc = AuthenticationError(HTTPException(
            status_code=HTTP_401_UNAUTHORIZED)
        )
        self.assertTrue(exc.is_client_side_error())

    def test_is_client_side_error_false_for_http_exception_500(self):
        exc = AuthenticationError(
            HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR)
        )
        self.assertFalse(exc.is_client_side_error())

    def test_is_client_side_error_false_for_server_error(self):
        exc = AuthenticationError(PyJWTError())
        self.assertFalse(exc.is_client_side_error())
