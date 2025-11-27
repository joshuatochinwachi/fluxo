from datetime import datetime,timezone
from dataclasses import asdict


class StoreData:
    def __init__(self):
        pass

    def store_protocol_data(self,protocol_data:list,data_name:str)->None:
        from core.config import get_mongo_connection
        mongo_db =  get_mongo_connection()
        if data_name == 'yield_data':
            update_collection = mongo_db['Yield_Protocol']
            store_id = "Mantle_yield_protocol"
        else:
            update_collection = mongo_db['Mantle_Protocol']
            store_id = "Mantle_Protocols"
        if not protocol_data:
            return 

        protocol_data = [asdict(data) for data in protocol_data]
        update_collection.update_one(
            {"_id":f"{store_id}"},
            {
                "$set":{
                    "protocol":protocol_data,
                    'updated_at':datetime.now(timezone.utc)
                },
                
            },
            upsert=True
        )
        print("Updated Yield protocols Data!!")


