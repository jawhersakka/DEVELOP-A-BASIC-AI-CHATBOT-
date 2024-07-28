import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('chatbot.db')

# Create a cursor object
cursor = conn.cursor()

# Execute a query to retrieve all records from the Question table
cursor.execute('SELECT * FROM Question')

# Fetch all results
rows = cursor.fetchall()

# Print the results
for row in rows:
    print(row)

# Close the connection
conn.close()