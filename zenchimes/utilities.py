import logging

def logged_class(cls):
    """
    Class Decorator to add a class level logger to the class with module and name
    """
    cls.logger = logging.getLogger("{0}.{1}".format(cls.__module__, cls.__name__))
    return cls
