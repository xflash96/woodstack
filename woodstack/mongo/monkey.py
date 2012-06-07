import mongoengine_bulk
import geventmongo
import pyramid_response

def patch():
    mongoengine_bulk.patch()
    geventmongo.patch()
    pyramid_response.patch()
