from typing import Any, ClassVar, Dict, Mapping, Optional, Sequence, List
from typing_extensions import Self
from viam.components.sensor import Sensor
from viam.logging import getLogger
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName
from viam.resource.base import ResourceBase
from viam.resource.types import Model, ModelFamily
from viam.utils import struct_to_dict, from_dm_from_extra
from viam.errors import NoCaptureToStoreError
from mysql.connector.aio import connect

LOGGER = getLogger(__name__)

class MySensor(Sensor):
    MODEL: ClassVar[Model] = Model(ModelFamily("bill", "db"), "mysql-select")
    REQUIRED_ATTRIBUTES = ["user", "password", "host", "database"]
    
    def __init__(self, name: str):
        super().__init__(name)    

    @classmethod
    def new(
        cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ) -> Self:
        """
        This constructor instantiates a new "mysensor" component based upon the 
        configuration added to the RDK.
        """
        sensor = cls(config.name)
        sensor.reconfigure(config, dependencies)
        return sensor

    @classmethod
    def validate_config(cls, config: dict) -> Sequence[str]:
        missing_attrs = [attr for attr in cls.REQUIRED_ATTRIBUTES if attr not in config['database_config'] or not config['database_config'][attr].strip()]
        if missing_attrs:
            raise ValueError(f"Missing required attributes in database_config: {', '.join(missing_attrs)}")
        return []

    def reconfigure(self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]):
        self.config = struct_to_dict(config.attributes)
        self.database_config = self.config['database_config']
        self.queries = self.config['queries']
        self.table = self.config['table']
        LOGGER.debug("%s is reconfigured", self.name)

    async def get_readings(self, extra: Optional[Dict[str, Any]] = None, **kwargs) -> Mapping[str, Any]:
        if not self.database_config:
            return {"error": "Database credentials are incomplete or missing"}

        if from_dm_from_extra(extra) and 'filter_query' in self.queries and 'action_query' in self.queries:
            results = await self.run_query(self.queries.get('filter_query'))
            if not results:
                raise NoCaptureToStoreError
            await self.run_query(self.queries.get('action_query'))
            return results
        else:
            return await self.run_query(self.queries.get('default_query'))  

    def determine_query(self, extra: Optional[Dict[str, Any]]) -> Optional[str]:
        if from_dm_from_extra(extra) and 'filter_query' in self.queries and 'action_query' in self.queries:
            return self.queries.get('filter_query')            
        return self.queries.get('default_query')

    async def run_query(self, query: str) -> Dict[str, Any]:
        async with await connect(**self.database_config) as conn:
            async with await conn.cursor() as cursor:
                await cursor.execute(query)
                if query.lower().startswith("select"):
                    rows = await cursor.fetchall()
                    keys = [column[0] for column in cursor.description]
                    primary_key_query = f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE WHERE TABLE_SCHEMA = '{self.database_config['database']}' AND TABLE_NAME = '{self.table}' AND CONSTRAINT_NAME = 'PRIMARY'"
                    await cursor.execute(primary_key_query)
                    primary_key_row = await cursor.fetchone()
                    if primary_key_row:
                        primary_key = primary_key_row[0]
                    else:
                        primary_key = None 
                    await cursor.close()
                    return self.process_readings(primary_key, keys, rows)
                else:
                    await conn.commit()
                    await cursor.close()
                    return {}
            
    def process_readings(self, primary_key, keys, query_result) -> Dict[str, Any]:
        readings = {}
    
        if primary_key not in keys:
            LOGGER.error(f"Primary key '{primary_key}' not found in keys: {keys}")
            return readings
        
        key_index = keys.index(primary_key)

        for row in query_result:
            row_data = {keys[i]: str(row[i]) for i in range(len(row)) if i != key_index}
            readings[str(row[key_index])] = row_data

        return readings
