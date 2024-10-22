from localization import BaseLocalization
class Locale:
    @staticmethod
    def get_locale(language_code: str):
        if language_code == 'fa_IR':
            return BaseLocalization('fa_IR')
        else:
            return BaseLocalization('en_US')

