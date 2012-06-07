import anyjson
import ujson

def patch():
    anyjson._modules.append(('ujson', 'dumps', TypeError, 'loads', ValueError))
    anyjson.force_implementation('ujson')
