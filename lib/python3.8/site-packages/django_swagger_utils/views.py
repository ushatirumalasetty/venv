import json
import os

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseNotFound
from django.shortcuts import render
from io import open


@login_required
def swagger_ui(request, path, *args, **kwargs):
    app = path.split('/')[0]
    if app in settings.INSTALLED_APPS:
        if app in getattr(settings, 'APPS', []):
            spec_path = os.path.join(settings.BASE_DIR, app, 'api_specs', 'api_spec.json')
        else:
            if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine'):
                third_party_base_dir = settings.BASE_DIR + "/lib"
            elif os.environ.get('VIRTUAL_ENV', ''):
                third_party_base_dir = os.environ.get('VIRTUAL_ENV')
                third_party_base_dir += "/lib/python3.7/site-packages/"
            else:
                third_party_base_dir = settings.BASE_DIR
            spec_path = os.path.join(third_party_base_dir, app, 'api_specs', 'api_spec.json')
        if os.path.exists(spec_path):
            with open(spec_path) as f:
                spec_json = json.loads(f.read())

                default_host = request.META.get("HTTP_HOST")
                host = settings.SWAGGER_UTILS.get('HOST', default_host)
                if host == "127.0.0.1:8000":
                    host = default_host

                http_schemes = "https" if request.is_secure() else "http"
                # if host.find("https://") != -1:
                #     http_schemes = "https"

                host = host.replace("https://", "")

                spec_json['host'] = host
                spec_json["schemes"] = [http_schemes]
                if "oauth" in spec_json["securityDefinitions"]:
                    spec_json["securityDefinitions"]["oauth"]["tokenUrl"] = http_schemes + "://" + host + "/o/token/"

            # validator = get_validator(spec_json)
            # validator.validate_spec(spec_json, spec_url='')
            swagger_ui_url = "swagger-ui-bundle.js"
            if settings.SWAGGER_UTILS["DEFAULTS"]["REQUEST_WRAPPING_REQUIRED"]:
                swagger_ui_url = "custom_swagger_ui/{}".format(swagger_ui_url)
            return render(request, 'index.html', {
                'spec_json': json.dumps(spec_json),
                'swagger_ui_url': swagger_ui_url
            })
        else:
            return HttpResponseNotFound('<h1>"%s" found but api specs not found</h1>' % app)
    else:
        return HttpResponseNotFound('<h1>"%s" not found </h1>' % app)


def chartit(request, *args, **kwargs):
    from chartit import DataPool, Chart, PivotDataPool, PivotChart
    from django.shortcuts import render_to_response
    from django_swagger_utils.models import Latency
    from django.db.models import Avg, Max
    response_time_data = DataPool(
        series=[
            {
                'options': {
                    'source': Latency.objects.all()},
                'terms': [
                    'response_time',
                    'operation_id'
                ]
            }
        ]
    )
    chart1 = Chart(
        datasource=response_time_data,
        series_options=
        [{'options': {
            'type': 'line',
            'stacking': False},
            'terms': {
                'operation_id': ['response_time']
            }}],
        chart_options=
        {'title': {
            'text': 'First Graph'},
            'xAxis': {
                'title': {
                    'text': 'OperationId'}}}
    )
    latency_objects = Latency.objects.all()
    api_detail = PivotDataPool(
        series=[
            {
                'options': {
                    'source': latency_objects,
                    'categories': ['operation_id'],
                    'legend_by': 'operation_id'
                },
                'terms': {
                    'avg_response_time': Avg('response_time'),
                    'avg_db_time': Avg('db_time'),
                    'avg_db_queries_count': Avg('db_queries_count'),
                    'max_response_time': Max('response_time'),
                    'max_db_time': Max('db_time'),
                    'max_db_queries_count': Max('db_queries_count'),
                }
            }
        ]
    )
    chart2 = PivotChart(
        datasource=api_detail,
        series_options=[{
            'options': {
                'type': 'column',
                'stacking': True
            },
            'terms': ['avg_response_time']
        }],
        chart_options={
            'title': {
                'text': 'api vs average_response_time'
            },
            'xAxis': {
                'title': {
                    'text': 'operation_id'
                }
            },
            'yAxis': {
                'title': {
                    'text': 'Average Response Time'
                }
            }
        }

    )
    chart3 = PivotChart(
        datasource=api_detail,
        series_options=[{
            'options': {
                'type': 'column',
                'stacking': True
            },
            'terms': ['avg_db_time']
        }],
        chart_options={
            'title': {
                'text': 'api vs avg_db_time'
            },
            'xAxis': {
                'title': {
                    'text': 'operation_id'
                }
            },
            'yAxis': {
                'title': {
                    'text': 'Average DB Time'
                }
            }
        }

    )
    chart4 = PivotChart(
        datasource=api_detail,
        series_options=[{
            'options': {
                'type': 'column',
                'stacking': True
            },
            'terms': ['avg_db_queries_count']
        }],
        chart_options={
            'title': {
                'text': 'api vs avg_db_hits'
            },
            'xAxis': {
                'title': {
                    'text': 'operation_id'
                }
            },
            'yAxis': {
                'title': {
                    'text': 'Average DB Queries'
                }
            }
        }

    )
    chart5 = PivotChart(
        datasource=api_detail,
        series_options=[{
            'options': {
                'type': 'column',
                'stacking': True
            },
            'terms': ['max_response_time']
        }],
        chart_options={
            'title': {
                'text': 'api vs max_response_time'
            },
            'xAxis': {
                'title': {
                    'text': 'operation_id'
                }
            },
            'yAxis': {
                'title': {
                    'text': 'Max Response Time'
                }
            }
        }

    )
    chart6 = PivotChart(
        datasource=api_detail,
        series_options=[{
            'options': {
                'type': 'column',
                'stacking': True
            },
            'terms': ['max_db_time']
        }],
        chart_options={
            'title': {
                'text': 'api vs max_db_time'
            },
            'xAxis': {
                'title': {
                    'text': 'operation_id'
                }
            },
            'yAxis': {
                'title': {
                    'text': 'Max DB Time'
                }
            }
        }

    )
    chart7 = PivotChart(
        datasource=api_detail,
        series_options=[{
            'options': {
                'type': 'column',
                'stacking': True
            },
            'terms': ['max_db_queries_count']
        }],
        chart_options={
            'title': {
                'text': 'api vs max_db_hits'
            },
            'xAxis': {
                'title': {
                    'text': 'operation_id'
                }
            },
            'yAxis': {
                'title': {
                    'text': 'Max DB Hits'
                }
            }
        }

    )
    charts_for_each_api = [chart1, chart2, chart3, chart4, chart5, chart6, chart7]
    return render_to_response("chart.html", {'chart_list': charts_for_each_api})
