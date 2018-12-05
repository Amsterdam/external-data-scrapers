import logging

from django.db import connection
from django.http import HttpResponse

log = logging.getLogger(__name__)


# TODO add check data when relevant

def health(request):
    # check database
    try:
        with connection.cursor() as cursor:
            cursor.execute("select 1")
            assert cursor.fetchone()
    except:  # noqa E722
        log.exception("Database connectivity failed")
        return HttpResponse(
            "Database connectivity failed",
            content_type="text/plain",
            status=500
        )

    return HttpResponse(
        "Connectivity OK",
        content_type="text/plain",
        status=200
    )
