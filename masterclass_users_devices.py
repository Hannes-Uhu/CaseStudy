from tinydb import TinyDB, Query
import os
from serializer import serializer
from datetime import datetime, timedelta

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

    def __init__(self, device_name: str, 
                 managed_by_user_id: str, 
                 is_active: bool = True, 
                 creation_date: datetime = None, 
                 end_of_life: datetime = None,
                 maintenance_interval: int = None,
                 maintenance_costs: float = None,
                 last_updated: datetime = None,
                 next_maintenance: datetime = None,
                 reservations: list = None):
        
        self.device_name = device_name
        self.managed_by_user_id = managed_by_user_id
        self.is_active = is_active
        self.creation_date = datetime.now().date()
        self.end_of_life = end_of_life if end_of_life else datetime.now().date() + timedelta(days=365)
        self.maintenance_interval = maintenance_interval
        self.maintenance_costs = maintenance_costs
        self.last_updated = datetime.now().date()
        self.next_maintenance = next_maintenance
        self.reservations = reservations or []

        if maintenance_interval:
            self.next_maintenance = self.creation_date + timedelta(days=maintenance_interval)
        else:
            self.next_maintenance = None

    def update_last_updated(self):
        self.last_updated = datetime.now().date()

    def set_end_of_life(self, end_of_life: datetime):
        self.end_of_life = end_of_life
        
    def set_maintenance_interval(self, maintenance_interval: int):
        self.maintenance_interval = maintenance_interval
        
    def set_maintenance_costs(self, maintenance_costs: float):
        self.maintenance_costs = maintenance_costs
       
    def calculate_quarterly_maintenance_costs(self):
        if not self.maintenance_interval or not self.maintenance_costs:
            return 0
        
        today = datetime.now().date()
        quarter_end = today + timedelta(days=90)
        
        effective_end_date = min(quarter_end, self.end_of_life) if self.end_of_life else quarter_end
        
        remaining_days = (effective_end_date - today).days
        
        if remaining_days > 0:
            num_maintenances = remaining_days // self.maintenance_interval
        else:
            num_maintenances = 0
        
        return num_maintenances * self.maintenance_costs

    def add_reservation(self, start_date: datetime, end_date: datetime) -> bool:
        if not hasattr(self, 'reservations'):
            self.reservations = []

        for reservation in self.reservations:
            existing_start = datetime.strptime(reservation['start_date'], '%Y-%m-%d').date()
            existing_end = datetime.strptime(reservation['end_date'], '%Y-%m-%d').date()
            if max(existing_start, start_date) <= min(existing_end, end_date):
                return False  

        self.reservations.append({
            "start_date": start_date.strftime('%Y-%m-%d'),
            "end_date": end_date.strftime('%Y-%m-%d')
        })
        self.store_data()
        return True

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
        self.name = name
        self.id = id

    def __str__(self):
        return f"User {self.name} ({self.id})"

    def __repr__(self):
        return self.__str__()

    def unique_key(self):
        return "name"
