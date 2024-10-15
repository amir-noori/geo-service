import os
import json

class Localization:
    def __init__(self, language_code=os.environ["locale"]):
        locale_dir = os.path.join(os.path.dirname(__file__))
        file_path = os.path.join(locale_dir, f"{language_code}.json")
        
        # Load the language file
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                self.translations = json.load(file)
        else:
            raise FileNotFoundError(f"Localization file not found: {file_path}")

    def translate(self, messageId):
        # Return the translated string if found, otherwise fallback to msgid
        return self.translations.get(messageId, messageId)