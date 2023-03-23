import uuid
import boto3
from boto3.dynamodb.conditions import Key, Attr
from typing import Dict, Any, Optional
import datetime, time
from django.conf import settings
from django.contrib.sessions.backends.base import SessionBase
from django.contrib.sessions.backends.base import CreateError, SessionBase, UpdateError
import math

session = boto3.session.Session()
resource = boto3.resource("dynamodb")

# settings.DDB_TABLE_NAME
# settings.DDB_PARTITION_KEY
# settings.DDB_SORT_KEY ???

table = resource.Table(settings.DDB_TABLE_NAME)

class SessionStore(SessionBase):

    def _prefix_key(self, session_key: str) -> str:
        return "SESSION#{}".format(session_key)

    def exists(self, session_key: str) -> bool:
        key = self._prefix_key(session_key)

        response = table.get_item(
            Key={
                "pk": key
            },
            AttributesToGet=["pk"],
        )
        
        item = response.get("Item")

        if item:
            return True
        
        return False


    def create(self) -> None:
        while True:
            self._session_key = self._get_new_session_key()
            try:
                self.save(must_create=True)
            except CreateError:
                continue
            self.modified = True
            return
    
    def save(self, must_create: bool = False) -> None:
        if self.session_key is None:
            return self.create()
        data = self._get_session(no_load=must_create)

        key = self._prefix_key(self._get_or_create_session_key())

        item = {
            "pk": key,
            "session_data": self.encode(data),
            "expire_date": math.ceil(self.get_expiry_date().timestamp())
        }
        args = {}
        args["Item"] = item
        if must_create:
            args["ConditionExpression"] = Attr("pk").not_exists()
        
        try:
            table.put_item(**args)
        except resource.meta.client.exceptions.ConditionalCheckFailedException as ex:
            if must_create:
                raise CreateError
            raise
        except Exception as ex:
            raise
    
    def delete(self, session_key: Optional[Any] = ...) -> None:
        if session_key is None:
            session_key = self.session_key
            
        key = self._prefix_key(session_key=session_key)

        table.delete_item(
            Key={
                "pk": key
            }
        )
    
    def load(self) -> Dict[str, Any]:
        key = self._prefix_key(self.session_key)
        response = table.get_item(
            Key={
                "pk": key
            },
            AttributesToGet=["pk", "session_data", "expire_date"]
        )

        item = response.get("Item")
        
        if item is not None and "session_data" in item:
            return self.decode(item["session_data"])
        
        return {}
    
    @classmethod
    def clear_expired(cls):
        pass
