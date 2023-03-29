import os
import base64

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.asymmetric.types import (
    PRIVATE_KEY_TYPES, PUBLIC_KEY_TYPES
)


class Enigma:
    private_key: PRIVATE_KEY_TYPES = None
    public_key: PUBLIC_KEY_TYPES = None
    key = None

    @staticmethod
    def create_key(key_size: int, key: str):
        _private = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size
        )
        return _private.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(
                key.encode('utf-8')
            )
        ).decode('utf-8')

    @classmethod
    def load_key(cls, path):
        with open(path, mode='rb') as _key_file:
            cls.private_key = serialization.load_pem_private_key(
                _key_file.read(),
                password=os.environ['KEY_PASS'].encode('utf-8')
            )
            cls.public_key = cls.private_key.public_key()

    @classmethod
    def encrypt(cls, value):
        data = cls.public_key.encrypt(
            value.encode('utf-8') if isinstance(value, str) else value,
            padding=padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA512()),
                algorithm=hashes.SHA512(),
                label=None
            ),
        )
        return (
            base64.b64encode(data).decode('utf-8') if isinstance(value, str)
            else data
        )

    @classmethod
    def decrypt(cls, value):
        data = cls.private_key.decrypt(
            base64.b64decode(value) if isinstance(value, str) else value,
            padding=padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA512()),
                algorithm=hashes.SHA512(),
                label=None
            ),
        )
        return data.decode('utf-8') if isinstance(value, str) else data


if __name__ == '__main__':
    import pathlib

    os.environ['KEY_PASS'] = '1234'
    private_key_path = pathlib.Path(__file__).parent.absolute() / 'tmp_key.pem'
    with open(private_key_path, 'w') as key_f:
        key_f.write(Enigma.create_key(2048, os.getenv('KEY_PASS')))
        Enigma.load_key(private_key_path)
    info = 'text'
    res = Enigma.encrypt(info)
    assert Enigma.decrypt(res) == info
