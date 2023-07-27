import json
import os
import warnings

from izi18n.utils import po_to_json, are_dicts_equal, Singleton, extract_language, create_file, \
    create_directory_if_not_exist


@Singleton
class I18n(object):

    def __init__(self, language=None, translations_path=None):
        self.language = extract_language(language)
        self._translations_path = translations_path
        self._translations_file = None
        self._translations = {}
        self._po = {}
        if self.language and self._translations_path:
            self.set_translations_path(translations_path)
            self.set_language(self.language)

    def set_translations_path(self, translations_path):
        """
        Set the translations directory
        """
        self._translations_path = translations_path
        create_directory_if_not_exist(self._translations_path)

    def load_translations(self):
        """
        This method load translation by language
        """
        try:
            with open(self._translations_file, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def load_translations_from_po_file(self, po_filename, language, stream=True):
        """
        Load translation from .po file
        """
        self.set_language(language)
        json_po = po_to_json(po_filename)
        self._po[language] = {**self._po.get(language, {}), **json_po}
        if not are_dicts_equal(self._translations, json_po):
            merged_data = {**self._translations, **self._po.get(language, {})}
            self._translations = merged_data
            if not stream:
                self._save_translations()
                self._translations = self.load_translations()

    def _save_translations(self):
        """
        Save translation modification
        """
        create_file(self._translations_file)
        with open(self._translations_file, 'w') as file:
            json.dump(self._translations, file, ensure_ascii=False, indent=2)

    def translate(self, pattern, default_text="", **kwargs):
        """
        Translate value by pattern or key.
        It possible to set default text And parse **kwargs
        """
        _text = self._get(pattern)

        if not _text:
            _text = self._translations.get(pattern)

        if len(kwargs) > 0 and _text:
            _text = str(_text).format(**kwargs)

        return _text if _text else default_text

    def set_language(self, language: str):
        """
        Allowed to change translation language
        """
        self.language = extract_language(language)
        self._translations_file = os.path.join(self._translations_path, self.language + '.json')
        self._translations = self.load_translations()

    def add_translation(self, pattern, value):
        """
        This method is for add new or edit translation to exiting language
        """
        if self._get(pattern):
            warnings.warn(f"Translation for '{value}' already exists in language '{self.language}'")

        self._set(pattern, value)

    def _get(self, pattern):
        try:
            # Split the pattern into keys
            keys = pattern.split('.')

            # Traverse the dictionary using the keys to extract the nested object
            result = self._translations
            for key in keys:
                result = result[key]

            return result
        except (json.JSONDecodeError, KeyError, TypeError):
            return None

    def _set(self, pattern, value):
        try:

            data = self._translations

            # Split the pattern using the dot ('.') as a delimiter
            keys = pattern.split('.')

            # Traverse the dictionary to reach the target object
            result = data
            for key in keys[:-1]:
                if key not in result:
                    result[key] = {}
                result = result[key]

            # Set the new value for the target object
            result[keys[-1]] = value

            # Convert the dictionary back to a JSON string
            self._translations = data

            self._save_translations()

        except (json.JSONDecodeError, KeyError, TypeError):
            raise KeyError(f"Translation error for '{pattern}'")
