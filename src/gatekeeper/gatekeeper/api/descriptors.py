from mongoengine.errors import DoesNotExist, NotUniqueError

from gatekeeper.exceptions import (DescriptorNotFoundError,
                                   DuplicateDescriptorNameError)
from gatekeeper.models.descriptors import Descriptor, DescriptorType


def getDescriptorsByType(type: DescriptorType):
    """
    Returns all descriptors of a given type.
    """
    return Descriptor.objects(type=type)


def getDescriptorById(id):
    """
    Returns a given descriptor by its ID, or a 404 error if no descriptor matching the
    given id exists.
    """
    try:
        return Descriptor.objects(id=id).get()
    except DoesNotExist:
        raise DescriptorNotFoundError()


def addDescriptor(body):
    try:
        return Descriptor(**body).save(), 201
    except NotUniqueError:
        raise DuplicateDescriptorNameError()


def updateDescriptor(id, body):
    """
    Updates a given descriptor by its ID, or returns a 404 error if no descriptor matching the given
    id exists.
    """
    try:
        descriptor: Descriptor = Descriptor.objects(id=id).get()
        descriptor.descriptor = body["descriptor"]
        descriptor.save()
        return descriptor
    except DoesNotExist:
        raise DescriptorNotFoundError()
    except NotUniqueError:
        raise DuplicateDescriptorNameError()


def deleteDescriptorById(id):
    """
    Deletes a descriptor by its ID, or returns a 404 error if no descriptor matching the given id
    exists.
    """
    try:
        descriptor = Descriptor.objects(id=id).get()
        descriptor.delete()
        return descriptor
    except DoesNotExist:
        raise DescriptorNotFoundError()
