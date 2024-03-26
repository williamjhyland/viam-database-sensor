"""
A basic example of how to wrap a sensor into the Viam sensor component in Python and query a MySQL Database
"""

from typing import Any, ClassVar, Dict, Mapping, Optional, Sequence, List

from typing_extensions import Self

from viam.components.sensor import Sensor
from viam.logging import getLogger
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName
from viam.resource.base import ResourceBase
from viam.resource.registry import Registry, ResourceCreatorRegistration
from viam.resource.types import Model, ModelFamily
from viam.utils import ValueTypes, struct_to_dict, from_dm_from_extra
from viam.errors import NoCaptureToStoreError

import mysql.connector
import asyncio
import os
import json

# Activate the logger to send log entries to app.viam.com, visible under the logs tab
LOGGER = getLogger(__name__)


class MySensor(Sensor):
    """
    Class representing the sensor to be implemented/wrapped.
    Subclass the Viam Sensor component and implement the required functions
    """

    MODEL: ClassVar[Model] = Model(ModelFamily("bill", "db"), "mysql-select")

    @classmethod
    def validate_config(cls, config: ComponentConfig) -> Sequence[str]:
        """
        Validates the configuration added to the Viam RDK and executed before new(). 
        Implement any specific attribute validation required by your component.
        """
        attributes_dict = struct_to_dict(config.attributes)
        """Validates JSON configuration"""
        
        required_attributes = ["host", "user", "password", "database", "table", "query"]

        for attribute in required_attributes:
            if attribute not in attributes_dict or not attributes_dict[attribute].string_value.strip():
                raise Exception(f"{attribute} attribute is required for mysql select-sensor")
                
        return []

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

    def __init__(self, name: str):
        """
        Actual component instance constructor
        """
        super().__init__(name)

    def reconfigure(
        self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ):
        """
        This method is executed whenever a new mysensor instance is created or
        configuration attributes are changed
        """
        attributes_dict = struct_to_dict(config.attributes)
        # Define the keys for the database credentials
        credential_keys = ["host", "user", "password", "database", "table", "query"]

        # Iterate over the credential keys and set them as attributes of 'self'
        for key in credential_keys:
            if key in attributes_dict:
                setattr(self, key, attributes_dict[key])

        # Handle the optional 'filtered-data-capture-parameters' if present
        filtered_params_key = "filtered-data-capture-parameters"
        if filtered_params_key in attributes_dict:
            # Ensure the value is a dictionary as expected
            if isinstance(attributes_dict[filtered_params_key], dict):
                filtered_params = attributes_dict[filtered_params_key]
                # Process the nested parameters, mapping them to valid Python attribute names
                mapping = {
                    'filter-query': 'filter_query',
                    'action-query': 'action_query',
                }
                for param_key, attr_name in mapping.items():
                    if param_key in filtered_params:
                        setattr(self, attr_name, filtered_params[param_key])
        
        LOGGER.debug("%s is reconfiguring...", self.name)


    async def close(self):
        """
        Optional function to include. This will be called when the resource
        is removed from the config or the module is shutting down.
        """
        LOGGER.info("%s is closed.", self.name)

    async def do_command(
        self,
        command: Mapping[str, ValueTypes],
        *,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Mapping[str, ValueTypes]:
        """
        Optional general purpose method to be used for additional
        device specific operations e.g. reseting a sensor.
        """
        raise NotImplementedError()

    async def get_readings(
        self, extra: Optional[Dict[str, Any]] = None, **kwargs
    ) -> Mapping[str, Any]:
        """
        Required method to be implemented for a sensor component.
        This method now runs a database query and returns the results.
        """
        # Ensure that all necessary credentials are available
        if all(hasattr(self, attr) for attr in ['host', 'user', 'password', 'database', 'table', 'query']):
            if from_dm_from_extra(extra):
                if all(hasattr(self, attr) for attr in ['filter_query', 'action_query']):
                    # Run the query using the credentials
                    primary_key, keys, result = await self.run_query(
                        host=self.host,
                        user=self.user,
                        password=self.password,
                        database=self.database,
                        table=self.table,
                        query=self.filter_query
                    )
                    # Process the result as needed to fit the structure of sensor readings
                    readings = self.process_readings(primary_key, keys, result)
                    LOGGER.debug(f"Readings: {readings} ***** Count: {len(readings)}")
                    if len(readings) <= 0 or len(readings) > 1:
                        raise NoCaptureToStoreError()
                    elif len(readings) == 1:
                        primary_key, keys, result = await self.run_query(
                        host=self.host,
                        user=self.user,
                        password=self.password,
                        database=self.database,
                        table=self.table,
                        query=self.action_query
                    )
                    return readings
                else:
                    raise NoCaptureToStoreError()
            elif not from_dm_from_extra(extra):
                # Run the query using the credentials
                primary_key, keys, result = await self.run_query(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    table=self.table,
                    query=self.query
                )
                # Process the result as needed to fit the structure of sensor readings
                readings = self.process_readings(primary_key, keys, result)
                return readings
        else:
            # Handle the case where some credentials are missing
            return {"error": "Database credentials are incomplete or missing"}

    async def run_query(
        self,
        host: str,
        user: str,
        password: str,
        database: str,
        table: str,
        query: str
    ) -> Mapping[str, Any]:
        # Establish a database connection
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        # Create a cursor object
        cursor = conn.cursor()

        try:
            # Execute the query
            cursor.execute(query)

            # If the query is a SELECT statement, fetch the results
            if query.strip().upper().startswith("SELECT"):
                # Fetch all the rows
                rows = cursor.fetchall()
                all_keys = [column[0] for column in cursor.description]

                # Query to get the primary key column name of the specified table
                primary_key_query = f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE WHERE TABLE_SCHEMA = '{database}' AND TABLE_NAME = '{table}' AND CONSTRAINT_NAME = 'PRIMARY'"

                # Get Primary Key
                # Execute the query
                cursor.execute(primary_key_query)
                # Fetch the result
                primary_key = cursor.fetchone()

                # Return the data
                return primary_key[0], all_keys, rows
            else:
                # For non-SELECT queries, return the number of affected rows
                conn.commit()  # Commit the transaction
                return None, None, cursor.rowcount
        finally:
            # Ensure the cursor and connection are closed
            cursor.close()
            conn.close()
        
    def process_readings(self, primary_key, keys, query_result) -> Dict[str, Any]:
        """
        Process the raw query result into a structured format for sensor readings.
        """
        readings = {}

        # Check if primary_key is None or not in keys
        if primary_key is None or primary_key not in keys:
            LOGGER.error("Primary key is None or not found in the keys list.")
            return readings

        key_index = keys.index(primary_key)

        for row in query_result:
            # Ensure that the row has enough columns as expected
            if len(row) != len(keys):
                LOGGER.error("Row length does not match keys length.")
                continue

            row_data = {keys[i]: str(row[i]) for i in range(len(row)) if i != key_index}
            readings[str(row[key_index])] = row_data

        return readings


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