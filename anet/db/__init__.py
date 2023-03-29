from tortoise import fields
from anet.utils.crypto import Enigma


class TextCryptoField(fields.TextField):
    def to_db_value(self, value, instance):
        value = super().to_db_value(value, instance)
        return Enigma.encrypt(value)

    def to_python_value(self, value):
        try:
            value = Enigma.decrypt(value)
        except ValueError:
            ...
        return super().to_python_value(value)
