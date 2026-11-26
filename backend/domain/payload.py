def payload_mapping(data):
    if hasattr(data, 'model_dump'):
        return data.model_dump()
    if isinstance(data, dict):
        return data
    return {key: getattr(data, key, None) for key in dir(data) if not key.startswith('_')}


def pick(data, *names):
    values = payload_mapping(data)
    for name in names:
        if isinstance(values, dict) and name in values:
            value = values[name]
        else:
            value = getattr(data, name, None)
        if value is not None and str(value).strip() != '':
            return value.strip() if isinstance(value, str) else value
    return None
