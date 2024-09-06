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

# SQL commands to create tables
commands = [
    """
    CREATE TABLE IF NOT EXISTS organization (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        status INT DEFAULT 0 NOT NULL,
        personal BOOLEAN DEFAULT NULL,
        settings JSON,
        created_at BIGINT DEFAULT NULL,
        updated_at BIGINT DEFAULT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS user (
        id INT AUTO_INCREMENT PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        profile JSON,
        status INT DEFAULT 0 NOT NULL,
        settings JSON,
        created_at BIGINT DEFAULT NULL,
        updated_at BIGINT DEFAULT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS role (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        description VARCHAR(255) DEFAULT NULL,
        org_id INT NOT NULL,
        FOREIGN KEY (org_id) REFERENCES organization(id) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS member (
        id INT AUTO_INCREMENT PRIMARY KEY,
        org_id INT NOT NULL,
        user_id INT NOT NULL,
        role_id INT NOT NULL,
        status INT DEFAULT 0 NOT NULL,
        settings JSON,
        created_at BIGINT DEFAULT NULL,
        updated_at BIGINT DEFAULT NULL,
        FOREIGN KEY (org_id) REFERENCES organization(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
        FOREIGN KEY (role_id) REFERENCES role(id) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS invite (
        id INT AUTO_INCREMENT PRIMARY KEY,
        token VARCHAR(255) UNIQUE NOT NULL,
        user_id INT NOT NULL,
        org_id INT NOT NULL,
        created_at BIGINT DEFAULT NULL,
        FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
        FOREIGN KEY (org_id) REFERENCES organization(id) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS version (
        id INT AUTO_INCREMENT PRIMARY KEY,
        version VARCHAR(255) UNIQUE NOT NULL,
        description VARCHAR(255) DEFAULT NULL,
        created_at BIGINT NOT NULL
    );
    """
]

# Execute the SQL commands
for command in commands:
    cursor.execute(command)

# Commit the changes and close the connection
conn.commit()
cursor.close()
conn.close()

print("Tables created successfully.")
