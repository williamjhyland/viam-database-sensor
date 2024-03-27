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
  [REQUIRED] "database_config": {
  [REQUIRED] "database": "DATABASE HERE",
  [REQUIRED] "user": "USER HERE",
  [REQUIRED] "password": "PASSWORD HERE",
  [REQUIRED] "host": "HOST HERE"
  },
  [REQUIRED] "table": "TABLE HERE",
  [REQUIRED] "queries": {
    [OPTIONAL] "action_query": "QUERY HERE",
    [REQUIRED] "default_query": "QUERY HERE",
    [OPTIONAL] "filter_query": "QUERY HERE"
  }
}
```
Generalized Example
```json
{
    "database_config": {
    "database": "test_db",
    "user": "user",
    "password": "password",
    "host": "192.168.0.155"
  },
  "table": "test_table",
  "queries": {
    "action_query": "UPDATE test_table SET Uploaded = 1 WHERE Done = 1 AND Uploaded = 0 LIMIT 1;",
    "default_query": "SELECT * FROM test_table;",
    "filter_query": "SELECT * FROM test_table WHERE Done = 1 AND Uploaded = 0 LIMIT 1;"
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