import os
from i18n.localization import BaseLocalization


class Locale:
    @staticmethod
    def get_lang(language_code: str):
        if language_code == 'fa_IR':
            return BaseLocalization('fa_IR')
        else:
            return BaseLocalization('en_US')


def get_locale(message,locale=None):
    setLang = locale
    if locale is None:
        setLang = os.getenv('default_locale', 'en_US')
    lang = Locale.get_lang(setLang)
    return lang.translate(message)
