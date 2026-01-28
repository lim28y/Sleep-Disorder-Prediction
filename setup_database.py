import mysql.connector

# 1. Connect to MySQL Server
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '217522' 
}

try:
    print("Connecting to MySQL Server...")
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # 2. Create the Database
    print("Creating Database 'sleep_app'...")
    cursor.execute("CREATE DATABASE IF NOT EXISTS sleep_app")
    
    # 3. Select the Database
    cursor.execute("USE sleep_app")

    # 4. Create Users Table
    print("Creating 'users' table...")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        email VARCHAR(100)
    )
    """)

    # 5. Create Sleep Data Table
    print("Creating 'user_sleep_data' table...")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_sleep_data (
        entry_id        INT AUTO_INCREMENT PRIMARY KEY,
        user_id         INT NOT NULL,
        log_date        DATE DEFAULT (CURRENT_DATE),
        gender          TINYINT,
        age             INT,
        sleep_duration  FLOAT,
        quality_sleep   INT,
        activity_level  INT,
        stress_level    INT,
        bmi_category    INT
    )
    """)

    print("SUCCESS! Database and Tables created successfully.")
    conn.commit()
    conn.close()

except mysql.connector.Error as err:
    print(f"Error: {err}")
    print("If Access is Denied, check password in this script.")