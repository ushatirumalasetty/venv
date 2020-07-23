__author__ = 'kapeed2091'


def get_absolute_file_name_for_multimedia(file_object):
    from django.conf import settings
    from ib_common.utilities.get_file_name import get_file_name
    offline = getattr(settings, 'ENV_NAME', '') == 'offline'
    media_url = getattr(settings,'MEDIA_URL')

    file_name = get_file_name(file_object)

    if file_name is None or file_name.strip() == '':
        return ''
    else:
        if file_name.startswith('http'):
            if offline:
                file_name = media_url + "/".join(file_name.split('/')[3:])
            return file_name
        return media_url + file_name
