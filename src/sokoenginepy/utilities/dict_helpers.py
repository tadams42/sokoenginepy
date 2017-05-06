def except_keys(dictionary, keys):
    if dictionary:
        key_set = set(dictionary.keys()) - set(keys)
        return {key: dictionary[key] for key in key_set}
    return {}


def inverted(dictionary):
    return dict(zip(dictionary.values(), dictionary.keys()))
