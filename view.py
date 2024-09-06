from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import datetime

# Database connection details
DATABASE_URL = 'mysql+pymysql://avnadmin:AVNS_7JH-2ruzIie96bkdhcs@mysql-279450c7-rajkisanssvrs-16fb.k.aivencloud.com:22461/defaultdb'

# Create an engine and a session
engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)
session = Session()

# Define the time range
from_time = 1325516000
to_time = 1825517200

# Execute the query
query = text("SELECT id, created_at FROM user WHERE created_at BETWEEN :from_time AND :to_time")
result = session.execute(query, {'from_time': from_time, 'to_time': to_time})

# Fetch and print results
for row in result:
    user_id, created_at = row
    print(f"User ID: {user_id}, Created At: {datetime.datetime.fromtimestamp(created_at)}")

# Close the session
session.close()
