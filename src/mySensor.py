"""
A basic example of how to wrap a sensor into the Viam sensor component in Python and query a MySQL Database
"""

from typing import Any, ClassVar, Dict, Mapping, Optional, Sequence, List

from typing_extensions import Self
import json

from viam.components.sensor import Sensor
from viam.logging import getLogger
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName
from viam.resource.base import ResourceBase
from viam.resource.registry import Registry, ResourceCreatorRegistration
from viam.resource.types import Model, ModelFamily
from viam.utils import ValueTypes, struct_to_dict

import mysql.connector
import asyncio

# Activate the logger to send log entries to app.viam.com, visible under the logs tab
LOGGER = getLogger(__name__)


class MySensor(Sensor):
    """
    Class representing the sensor to be implemented/wrapped.
    Subclass the Viam Sensor component and implement the required functions
    """

    MODEL: ClassVar[Model] = Model(ModelFamily("viam-soleng", "mysql"), "select-sensor")

    @classmethod
    def validate_config(cls, config: ComponentConfig) -> Sequence[str]:
        """
        Validates the configuration added to the Viam RDK and executed before new(). 
        Implement any specific attribute validation required by your component.
        """
        attributes_dict = struct_to_dict(config.attributes)
        """Validates JSON configuration"""
        
        required_attributes = ["host", "user", "password", "database_name", "query"]

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
        self.multiplier = 1.0

    def reconfigure(
        self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ):
        """
        This method is executed whenever a new mysensor instance is created or
        configuration attributes are changed
        """
        attributes_dict = struct_to_dict(config.attributes)
        # Define the keys for the database credentials
        credential_keys = ["host", "user", "password", "database", "query"]

        # Iterate over the credential keys and set them as attributes of 'self'
        for key in credential_keys:
            if key in attributes_dict:
                setattr(self, key, attributes_dict[key])

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
        if all(hasattr(self, attr) for attr in ['host', 'user', 'password', 'database', 'query']):
            # Run the query using the credentials
            result = await self.run_query(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                query=self.query
            )
            # Return the result of the query
            return {"query_result": result}
        else:
            # Handle the case where some credentials are missing
            return {"error": "Database credentials are incomplete or missing"}

    async def run_query(
        self,
        host: str,
        user: str,
        password: str,
        database: str,
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

        # Query the table
        cursor.execute(query)

        # Fetch all the rows
        rows = cursor.fetchall()

        for row in rows:
            print(row)

        # Close the connection
        cursor.close()
        conn.close()
        return rows
        

# Register this model with the module.
Registry.register_resource_creator(
    Sensor.SUBTYPE,
    MySensor.MODEL,
    ResourceCreatorRegistration(MySensor.new, MySensor.validate_config),
)

async def main():
    # Create an instance of MySensor
    sensor = MySensor("test_sensor")

    # Load credentials from the JSON file
    with open("../credentials.json", "r") as json_file:
        credentials = json.load(json_file)

    # Database credentials
    host = credentials["database"]["host"]
    user = credentials["database"]["user"]
    password = credentials["database"]["password"]
    database_name = credentials["database"]["database_name"]

    # List of queries
    queries = credentials["queries"]

    # Run the query
    # Print the loaded credentials
    print("Database Host:", host)
    print("Database User:", user)
    print("Database Name:", database_name)
    print("Queries:")
    for query in queries:
        print("------------------------------")
        print("Query: ", query)
        print("------------------------------")
        result = await sensor.run_query(host, user, password, database_name, query)
        print("***** PRESENTED RESULT *****")
        print(result)
        print("------------------------------")


# Run the main function
asyncio.run(main())