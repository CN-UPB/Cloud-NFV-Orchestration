import json
from datetime import datetime, timezone
from email.utils import formatdate

from bson import json_util
from flask.json import JSONEncoder
from mongoengine.base import BaseDocument
from mongoengine.queryset import QuerySet


class MongoEngineJSONEncoder(JSONEncoder):
    """
    A JSONEncoder which provides serialization of MongoEngine
    documents and queryset objects.
    """

    def default(self, obj):
        if isinstance(obj, BaseDocument):
            doc: dict = obj.to_mongo()

            # Convert IDs
            if "_id" in doc and "id" not in doc:
                doc["id"] = str(doc.pop("_id"))

            # Convert datetime fields to RFC 3339 format (in UTC time zone)
            for key, value in doc.items():
                if isinstance(value, datetime):
                    doc[key] = value.replace(tzinfo=timezone.utc).isoformat()

            # Remove Mongoengine class field if it exists
            if "_cls" in doc:
                doc.pop("_cls")

            return json_util._json_convert(doc)
        if isinstance(obj, QuerySet):
            return [self.default(entry) for entry in obj]

        return super().default(obj)


def makeErrorDict(status: int, detail: str):
    """
    Given a `detail` string with a message and a `status` integer, returns a dictionary containing
    those two items.
    """
    return {"detail": detail, "status": status}


def makeErrorResponse(status: int, detail: str):
    """
    Given a `detail` string and a `status` integer, returns a tuple containing the result of
    `makeErrorDict()` and the `status` code. This can be returned from flask route handlers.
    """
    return makeErrorDict(status, detail), status
