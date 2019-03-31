def get_user(object):
    # function returns model-referenced User-object

    if hasattr(object, 'scope'):
        if 'user' in getattr(object, 'scope'):
            return getattr(object, 'scope').get('user')
    else:
        raise TypeError('Can not return user from object {}'.format(type(object)))