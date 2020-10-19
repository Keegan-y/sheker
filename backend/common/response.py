def success_response(data=None, message="OK"):
    return {
        'code': 0,
        'message': message,
        'data': data
    }


def error_response(code=-1, data=None, message='NOT KNOW'):
    return {
        'code': code,
        'message': message,
        'data': data
    }
