# MySQL Database Sensor Integration
## Description

This project demonstrates the integration of a sensor component with a MySQL database, enabling the sensor to read data from the database given a query and data base connection information. This integration allows for advanced data capture scenarios where sensor readings can trigger additional actions, such as updating database records. You can find this module in the [Viam Registry]([https://app.viam.com/registry](https://app.viam.com/module/bill/viam-database-sensor))

## Configuration
  * For this module you need to grant access to the MySQL user from the specific host or any host. 
```sql
CREATE USER 'user'@'host' IDENTIFIED BY 'password';
```
  * Grant privileges... be aware that this is less secure and should be done with caution.
Execute a GRANT command:
```sql
GRANT ALL PRIVILEGES ON *.* TO 'user'@'host' WITH GRANT OPTION;
````

### Attribute Guide:

Provide the necessary credentials and configurations for the database connection in your project's configuration file.

Generic Example
```json
{
  [REQUIRED] "host": "YOUR DATABASE HOST",
  [REQUIRED] "user": "YOUR DATABASE USER",
  [REQUIRED] "password": "YOUR DATABASE PASSWORD",
  [REQUIRED] "database": "YOUR DATABASE NAME",
  [REQUIRED] "query": "YOUR SQL QUERY",
  [OPTIONAL] "filtered-data-capture-parameters": {
    "filter-query": "YOUR SQL QUERY",
    "action-query": "YOUR SQL QUERY",
  }
}
```
Generalized Example
```json
{
  "host": "localhost",
  "user": "root",
  "password": "example_password",
  "database": "sensor_data",
  "table": "sensor_readings",
  "query": "SELECT * FROM sensor_readings",
  "filtered-data-capture-parameters": {
    "filter-query": "SELECT * FROM test_table WHERE Done = 1 AND Uploaded = 0 LIMIT 1;",
    "action-query": "UPDATE test_table SET Uploaded = 1 WHERE Done = 1 AND Uploaded = 0 LIMIT 1;",
  }
}
```
## Setup and Installation
  * Database Setup: Ensure that your MySQL database is running and accessible.
    * 
  * Sensor Configuration: Configure your sensor component with the necessary database connection details.

## Usage
Once the sensor and data capture service is configured, the sensor will periodically query the MySQL database using the provided SQL query and upload the results of the query to the accounts Viam Cloud where it can be accessed broadly.

1. [Configure a new Component](https://docs.viam.com/registry/configure/) in your robot using [app.viam.com](app.viam.com)
2. Search for "mysql-select" and click the "sensor / db:mysql-select" from "bill"
3. Click "Add module"
4. Name the component (ex: `mysql-sensor`)
5. Click "Create"
6. Create the relevant attributes (see [config](#Configuration))

## Additional Information
Always ensure your database credentials are stored securely.
Modify the SQL query based on your specific data retrieval needs.
For more information about MySQL and Python integration, visit:

[MySQL Connector/Python Developer Guide](https://dev.mysql.com/doc/connector-python/en/)