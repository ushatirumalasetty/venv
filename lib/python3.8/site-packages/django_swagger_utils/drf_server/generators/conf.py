from jinja2 import Environment, PackageLoader

env = Environment(
    loader=PackageLoader(
        'django_swagger_utils.drf_server',
        'templates'
    ),
    autoescape=False,
    trim_blocks=False
)


def render(name, context):
    return env.get_template(name).render(context)
