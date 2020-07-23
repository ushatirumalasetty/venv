def get_language_name():
    from django.utils.translation import get_language
    language = get_language()

    supported_languages_list = get_supported_langs()

    if language not in supported_languages_list:
        language = get_default_language()
    return language


def get_request_language_name():
    language = get_language_name()
    return convert_language_code(language)


def get_supported_langs():
    from django.conf import settings
    return [each_lang[0] for each_lang in settings.LANGUAGES]


def get_default_language():
    from django.conf import settings
    return settings.LANGUAGE_CODE.split("-")[0]


def convert_language_code(language):
    from ib_common.constants.language_choices import LanguageEnum
    _dict = {
        "en": LanguageEnum.ENGLISH.value,
        "te": LanguageEnum.TELUGU.value,
        "hi": LanguageEnum.HINDI.value,
    }
    from ib_common.constants.language_choices import DEFAULT_LANGUAGE
    return _dict.get(language, DEFAULT_LANGUAGE)
