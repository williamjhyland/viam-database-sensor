from typing import Any, Dict, Mapping, Optional, Sequence
from viam.components.sensor import Sensor
from viam.logging import getLogger
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName
from viam.resource.base import ResourceBase
from viam.utils import struct_to_dict, from_dm_from_extra
from viam.errors import NoCaptureToStoreError
import mysql.connector
import asyncio
import os
import json

LOGGER = getLogger(__name__)

class MySensor(Sensor):
    REQUIRED_ATTRIBUTES = ["host", "user", "password", "database", "table", "query"]
    FILTERED_PARAMS_MAPPING = {'filter-query': 'filter_query', 'action-query': 'action_query'}

    def __init__(self, name: str):
        super().__init__(name)
        self.connection_details = {}

    @classmethod
    def validate_config(cls, config: ComponentConfig) -> Sequence[str]:
        attributes = struct_to_dict(config.attributes)
        missing_attrs = [attr for attr in cls.REQUIRED_ATTRIBUTES if attr not in attributes or not attributes[attr].strip()]
        if missing_attrs:
            raise ValueError(f"Missing required attributes: {', '.join(missing_attrs)}")
        return []

    def reconfigure(self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]):
        attributes = struct_to_dict(config.attributes)
        self.connection_details = {key: attributes[key] for key in self.REQUIRED_ATTRIBUTES if key in attributes}
        self.handle_filtered_data_capture_params(attributes.get('filtered-data-capture-parameters', {}))
        LOGGER.debug("%s is reconfigured", self.name)

    def handle_filtered_data_capture_params(self, params: Dict[str, Any]):
        for param_key, attr_name in self.FILTERED_PARAMS_MAPPING.items():
            if param_key in params:
                setattr(self, attr_name, params[param_key])

    async def get_readings(self, extra: Optional[Dict[str, Any]] = None, **kwargs) -> Mapping[str, Any]:
        if not self.connection_details:
            return {"error": "Database credentials are incomplete or missing"}

        query = self.determine_query(extra)
        if query:
            return await self.fetch_sensor_readings(query)
        return {}

    def determine_query(self, extra: Optional[Dict[str, Any]]) -> Optional[str]:
        if from_dm_from_extra(extra) and hasattr(self, 'filter_query') and hasattr(self, 'action_query'):
            return getattr(self, 'filter_query')
        elif hasattr(self, 'query'):
            return getattr(self, 'query')
        return None

    async def fetch_sensor_readings(self, query: str) -> Dict[str, Any]:
        async with self.database_connection() as cursor:
            await cursor.execute(query)
            if query.lower().startswith("select"):
                rows = await cursor.fetchall()
                keys = [column[0] for column in cursor.description]
                return self.process_readings(rows, keys)
            return {}

    async def database_connection(self):
        return await mysql.connector.connect(**self.connection_details)

    def process_readings(self, rows: Sequence[Sequence[Any]], keys: Sequence[str]) -> Dict[str, Any]:
        return {str(row[0]): {keys[i]: row[i] for i in range(1, len(row))} for row in rows}

async def main():
    credentials_path = "./credentials.json"
    if not os.path.exists(credentials_path):
        LOGGER.error("Credentials file not found")
        return

    with open(credentials_path, "r") as file:
        credentials = json.load(file)

    sensor = MySensor("test_sensor")
    for query in credentials["queries"]:
        result = await sensor.fetch_sensor_readings(query)
        print(result)

if __name__ == "__main__":
    asyncio.run(main())
