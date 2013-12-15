def make_enum(**enums):
    return type('Enum', (), enums)