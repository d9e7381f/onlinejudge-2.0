from rest_framework.response import Response as drf_response


def Response(res):
    """Response wrapper for compatible of origin version."""
    if not hasattr(res, 'data'):
        data = res
    else:
        data = res.data

        count = data.pop('count', '')
        if isinstance(count, int):
            data['total'] = count

    return drf_response({
        'error': None,
        'data': data
    })
