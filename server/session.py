import time

from server.orm import LoginCookie


def has_valid_session(request):
    access_key = request.cookies.get("access_key", "empty")
    if access_key != "empty":
        cookie: LoginCookie = LoginCookie.find_cookie_by_value(access_key)
        print("found:" + str(cookie))
        if cookie.expiration_date < int(time.time()):
            return False
        return True

    cookie: LoginCookie = LoginCookie.find_cookie_by_value(access_key)
    if cookie is None:
        return False

    if cookie.expiration_date < int(time.time()):
        return False

    return True


def get_cookie_from_session(request):
    access_key = request.cookies.get("access_key", "empty")
    if access_key != "empty":
        return access_key
    return None


