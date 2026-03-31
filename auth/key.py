from aiohttp import ClientSession
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.types import PrivateKeyTypes, PublicKeyTypes
from jwcrypto.jwk import JWK
from jwt import PyJWK
from jwt.algorithms import AllowedPrivateKeys, AllowedPublicKeys
from orjson import JSONDecodeError, loads

from os import getenv
from os.path import isfile
from typing import Literal, Optional, overload, Union


class KeyStore:
    _private_key: Optional[PrivateKeyTypes] = None
    _private_key_jwk: Optional[PyJWK] = None
    _private_key_jwk_dict: Optional[dict] = None
    _public_key: Optional[PublicKeyTypes] = None
    _public_key_jwk: Optional[PyJWK] = None
    _public_key_jwk_dict: Optional[dict] = None

    def get_private_key(self) -> "AllowedPrivateKeys":
        if self._private_key is None:
            raise RuntimeError("JWT private key is not loaded.")
        if not isinstance(self._private_key, AllowedPrivateKeys):
            raise RuntimeError("JWT private key type is not allowed.")
        return self._private_key

    @overload
    def get_private_jwk(self) -> PyJWK: ...

    @overload
    def get_private_jwk(self, as_dict: Literal[False]) -> PyJWK: ...

    @overload
    def get_private_jwk(self, as_dict: Literal[True]) -> dict: ...

    def get_private_jwk(self, as_dict: bool = False) -> Union[PyJWK, dict[str, str]]:
        if as_dict:
            if self._private_key_jwk_dict is None:
                raise RuntimeError("JWT private JWK dict is not loaded.")
            return self._private_key_jwk_dict

        if self._private_key_jwk is None:
            raise RuntimeError("JWT private JWK is not loaded.")
        return self._private_key_jwk

    def get_public_key(self) -> "AllowedPublicKeys":
        if self._public_key is None:
            raise RuntimeError("JWT public key is not loaded.")
        if not isinstance(self._public_key, AllowedPublicKeys):
            raise RuntimeError("JWT public key type is not allowed.")
        return self._public_key

    @overload
    def get_public_jwk(self) -> PyJWK: ...

    @overload
    def get_public_jwk(self, as_dict: Literal[False]) -> PyJWK: ...

    @overload
    def get_public_jwk(self, as_dict: Literal[True]) -> dict: ...

    def get_public_jwk(self, as_dict: bool = False) -> Union[PyJWK, dict[str, str]]:
        if as_dict:
            if self._public_key_jwk_dict is None:
                raise RuntimeError("JWT public JWK dict is not loaded.")
            return self._public_key_jwk_dict

        if self._public_key_jwk is None:
            raise RuntimeError("JWT public JWK is not loaded.")
        return self._public_key_jwk

    def _convert_public_key_to_jwk(self) -> None:
        if not isinstance(self._public_key, AllowedPublicKeys):
            raise ValueError("Unsupported public key type.")

        jwcrypto_jwk = JWK.from_pyca(self._public_key)
        self._public_key_jwk_dict = jwcrypto_jwk.export_public(as_dict=True)
        self._public_key_jwk = PyJWK(self._public_key_jwk_dict)

    def _load_private_key(self, path: str, password: Optional[str]) -> None:
        with open(path, "rb") as f:
            private_key_data = f.read()

        self._private_key = serialization.load_pem_private_key(
            private_key_data,
            password=password.encode() if password else None,
            backend=default_backend()
        )
        if not isinstance(self._private_key, AllowedPrivateKeys):
            raise ValueError("Unsupported private key type.")

        jwcrypto_jwk = JWK.from_pyca(self._private_key)
        self._private_key_jwk_dict = jwcrypto_jwk.export_private(as_dict=True)
        self._private_key_jwk = PyJWK(self._private_key_jwk_dict)

        self._public_key = self._private_key.public_key()
        self._convert_public_key_to_jwk()

    def _load_public_key_from_file(self, path: str) -> None:
        with open(path, "rb") as f:
            public_key_data = f.read()

        self._public_key = serialization.load_pem_public_key(
            public_key_data,
            backend=default_backend()
        )
        self._convert_public_key_to_jwk()

    async def _load_public_key_from_url(self, url: str) -> None:
        async with ClientSession() as client:
            async with client.get(url) as resp:
                resp.raise_for_status()
                public_key_data = await resp.read()

        try:
            json_data = loads(public_key_data)

            jwk = JWK(**json_data)
            self._public_key_jwk_dict = jwk.export_public(as_dict=True)
            self._public_key_jwk = PyJWK(self._public_key_jwk_dict)

            pem_data = jwk.export_to_pem()
            self._public_key = serialization.load_pem_public_key(
                pem_data,
                backend=default_backend()
            )
        except JSONDecodeError:
            self._public_key = serialization.load_pem_public_key(
                public_key_data,
                backend=default_backend()
            )
            self._convert_public_key_to_jwk()

    async def load_keys(self):
        private_key_path = getenv("JWT_PRIVATE_KEY")
        if private_key_path is None:
            public_key_path = getenv("JWT_PUBLIC_KEY")
            if public_key_path is None:
                raise RuntimeError(
                    "JWT public key path must be set in environment variables.")

            if isfile(public_key_path):
                self._load_public_key_from_file(public_key_path)
            else:
                await self._load_public_key_from_url(public_key_path)
        else:
            private_key_password = getenv("JWT_PRIVATE_KEY_PASSWORD")
            self._load_private_key(
                path=private_key_path,
                password=private_key_password
            )


KEY_STORE = KeyStore()
