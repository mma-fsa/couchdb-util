def make_enum(**enums):
    return type('Enum', (), enums)

def props(x):
    return dict((key, getattr(x, key)) for key in dir(x) if key not in dir(x.__class__))