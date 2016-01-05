def convert_to_str(data):
    if not data or isinstance(data, str):
        return data
    if isinstance(data, dict):
        return {__convert_to_str(k):__convert_to_str(v) for k, v in data.items()}

def __is_unicode(v):
    return isinstance(v, unicode)

def __convert_to_str(v):
    if __is_unicode(v):
        return v.encode('utf-8')
    return v

def ensure_utf8(s):
    return __convert_to_str(s)
