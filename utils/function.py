from hashlib import md5


def md5_encode(password):
    return md5(str.encode('utf-8')).hexdigest()


def get_referer_url(request):
    return request.META.get('HTTP_REFERER', '/')
