from tinydb import TinyDB, Query
import os
from serializer import serializer

class MasterClass:
    db_connector = None  # Wird in den Subklassen definiert

    def __init__(self):
        raise NotImplementedError("MasterClass should not be instantiated directly")

    def store_data(self):
        print("Storing data...")
        # Check if the instance already exists in the database
        RecordQuery = Query()
        result = self.db_connector.search(RecordQuery[self.unique_key()] == getattr(self, self.unique_key()))
        if result:
            # Update the existing record with the current instance's data
            self.db_connector.update(self.__dict__, doc_ids=[result[0].doc_id])
            print("Data updated.")
        else:
            # If the instance doesn't exist, insert a new record
            self.db_connector.insert(self.__dict__)
            print("Data inserted.")

    def delete(self):
        print("Deleting data...")
        # Check if the instance exists in the database
        RecordQuery = Query()
        result = self.db_connector.search(RecordQuery[self.unique_key()] == getattr(self, self.unique_key()))
        if result:
            # Delete the record from the database
            self.db_connector.remove(doc_ids=[result[0].doc_id])
            print("Data deleted.")
        else:
            print("Data not found.")

    @classmethod
    def find_by_attribute(cls, by_attribute: str, attribute_value: str, num_to_return=1):
        RecordQuery = Query()
        result = cls.db_connector.search(RecordQuery[by_attribute] == attribute_value)
        if result:
            data = result[:num_to_return]
            instances = [cls(**d) for d in data]
            return instances if num_to_return > 1 else instances[0]
        else:
            return None

    @classmethod
    def find_all(cls) -> list:
        records = []
        for record_data in cls.db_connector.all():
            records.append(cls(**record_data))
        return records

    def unique_key(self):
        raise NotImplementedError("Subclasses must define a unique_key method")


class Device(MasterClass):
    db_connector = TinyDB(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.json'), storage=serializer).table('devices')

    def __init__(self, device_name: str, managed_by_user_id: str, is_active: bool = True):
        self.device_name = device_name
        self.managed_by_user_id = managed_by_user_id
        self.is_active = is_active

    def __str__(self):
        return f"Device (Object) {self.device_name} ({self.managed_by_user_id})"

    def __repr__(self):
        return self.__str__()

    def set_managed_by_user_id(self, managed_by_user_id: str):
        self.managed_by_user_id = managed_by_user_id

    def unique_key(self):
        return "device_name"


class User(MasterClass):
    db_connector = TinyDB(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.json'), storage=serializer).table('users')

    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name

    def __str__(self):
        return f"User {self.id} - {self.name}"

    def __repr__(self):
        return self.__str__()

    def unique_key(self):
        return "id"
