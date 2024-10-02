from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

# Database connection details
DATABASE_URL = 'mysql+pymysql://avnadmin:AVNS_7JH-2ruzIie96bkdhcs@mysql-279450c7-rajkisanssvrs-16fb.k.aivencloud.com:22461/defaultdb'

# Create an engine and a session
engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)
session = Session()

# Reflect the database schema
metadata = MetaData()
metadata.reflect(bind=engine)

# Function to display data from all tables
def view_data():
    for table in metadata.sorted_tables:
        print(f"\nTable: {table.name}")

        # Fetch and print rows
        query = session.execute(table.select())
        rows = query.fetchall()
        
        # Check if rows are present
        if rows:
            columns = [column.name for column in table.columns]
            print(f"Columns: {', '.join(columns)}")
            
            for row in rows:
                # Create a dictionary for each row
                row_dict = {columns[i]: row[i] for i in range(len(columns))}
                print(row_dict)  # Print each row as a dictionary
        else:
            print("No rows found.")

# Call the function to view data
view_data()

# Close the session
session.close()