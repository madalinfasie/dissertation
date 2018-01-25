from django.template import Library
import math 

register = Library()

def sub(first, second):
    return first - second

register.filter('sub', sub)
