from django.template import Library

register = Library()

def sub(first, second):
    return first - second

register.filter('sub', sub)
