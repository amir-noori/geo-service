import json
import os

class BaseLocalization:
    def __init__(self, locale):
        self.locale = locale
        self.translations = self.load_translations()

    def load_translations(self):
        locale_file = os.path.join(os.path.dirname(__file__), 'locales', f'{self.locale}.json')
        if not os.path.exists(locale_file):
            raise FileNotFoundError(f"Locale file for {self.locale} not found.")

        with open(locale_file, 'r', encoding='utf-8') as file:
            return json.load(file)

    def translate(self, key):
        return self.translations.get(key, key)  # Returns key if translation not found
