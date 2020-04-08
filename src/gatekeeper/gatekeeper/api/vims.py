from mongoengine.errors import DoesNotExist

from connexion.exceptions import ProblemException
from gatekeeper.app import broker
from gatekeeper.models.vims import Aws, Kubernetes, OpenStack, Vim

NO_Vim_FOUND_MESSAGE = "No Vim matching the given id was found."


# Getting the VIMs

def getAllVims():
    """
    Returns the list of added Vims.
    """
    # return Vim.objects()
    return broker.call_sync_safe_yaml("infrastructure.management.compute.list")


# Deleting Vim

def deleteVim(id):
    """
    Delete A VIM by giving its uuid.
    """
    try:
        vim = Vim.objects(id=id).get()
        vim.delete()
        return vim
    except DoesNotExist:
        raise ProblemException(404, "Not Found", NO_Vim_FOUND_MESSAGE)


# ADD vim

def addVim(body):
    if body["type"] == "aws":
        vim = Aws(**body).save()
    elif body["type"] == "kubernetes":
        vim = Kubernetes(**body).save()
    elif body["type"] == "openStack":
        vim = OpenStack(**body).save()
    return vim
