import pymysql

# Database connection configuration
config = {
    'user': 'avnadmin',
    'password': 'AVNS_7JH-2ruzIie96bkdhcs',
    'host': 'mysql-279450c7-rajkisanssvrs-16fb.k.aivencloud.com',
    'port': 22461,
    'database': 'defaultdb',
}

# Connect to the database
conn = pymysql.connect(**config)
cursor = conn.cursor()

try:
    # Disable foreign key checks
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

    # Get the list of all tables in the database
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()

    # Drop each table
    for (table_name,) in tables:
        try:
            cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")
            print(f"Table {table_name} dropped successfully.")
        except Exception as e:
            print(f"Error dropping table {table_name}: {e}")

    # Commit the changes
    conn.commit()

finally:
    # Re-enable foreign key checks
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    cursor.close()
    conn.close()

print("All tables dropped successfully.")
