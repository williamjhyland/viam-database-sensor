# MySQL Database Sensor Integration
## Description

This project demonstrates the integration of a sensor component with a MySQL database, enabling the sensor to read data from the database given a query and data base connection information. You can find this module in the [Viam Registry]([https://app.viam.com/registry](https://app.viam.com/module/bill/viam-database-sensor))

## Configuration

### Attribute Guide:

Provide the necessary credentials and configurations for the database connection in your project's configuration file.

Generic Example
```json
{
  "host": "YOUR DATABASE HOST",
  "user": "YOUR DATABASE USER",
  "password": "YOUR DATABASE PASSWORD",
  "database": "YOUR DATABASE NAME",
  "query": "YOUR SQL QUERY"
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
  "query": "SELECT * FROM sensor_readings"
}
```
## Setup and Installation
  * Database Setup: Ensure that your MySQL database is running and accessible.
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

## Testing Connections
1. Clone this repository
2. Create the "credentials.json" File
    * Create a new JSON file named "credentials.json" in the repository you just cloned.
    * Copy and paste the following JSON structure into "credentials.json" and update it with your database credentials and queries:
### Example "credentials.json" file
```json
{
  "database": {
    "host": "localhost",
    "user": "root",
    "password": "your_mysql_password",
    "database_name": "your_database_name"
  },
  "queries": [
    "SELECT * FROM test_table",
    "SELECT name, age FROM test_table",
    "SELECT * FROM test_table WHERE age > 25",
    "SELECT * FROM test_table ORDER BY age DESC",
    "SELECT * FROM test_table LIMIT 5"
  ]
}
```
3. Testing the Database Connection
    * Build the virtual environment.
    * Run the script.
    * After testing the database connection and queries in the "main" function, you can proceed to create your sensor class and integrate it with the Viam framework. You can use the host, user, password, and database_name variables to establish a database connection using the MySQL connector library.

## Future Efforts:
Add libraries to manage other common database vendors like PostgreSQL, SQLite, MongoDB, MariaDB...

Construct a SQL query from attributes provided in the configuration
```sql
SELECT column1, column2, ...
FROM table_name
JOIN another_table ON table_name.column = another_table.column
WHERE condition
GROUP BY column
HAVING condition
ORDER BY column ASC/DESC
LIMIT number;
```

could be represented as...

```json
{
    "select": ["column1", "column2"],
    "from": "table_name",
    "join": {
        "table": "another_table",
        "on": "table_name.column = another_table.column"
    },
    "where": "condition",
    "groupBy": ["column"],
    "having": "condition",
    "orderBy": {
        "column": "column",
        "order": "ASC"  // or "DESC"
    },
    "limit": "number"
}
```
