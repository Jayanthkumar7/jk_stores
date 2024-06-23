import sqlite3
import csv

# Connect to SQLite database
sqlite_conn = sqlite3.connect('products_details_limited.db')
sqlite_cursor = sqlite_conn.cursor()

# Query to select all data from products_details
sqlite_cursor.execute("SELECT * FROM products_details")

# Fetch all data
rows = sqlite_cursor.fetchall()

# Get column names
column_names = [description[0] for description in sqlite_cursor.description]

# Write data to CSV file with UTF-8 encoding
with open('products_details.csv', 'w', newline='', encoding='utf-8') as csvfile:
    csvwriter = csv.writer(csvfile)
    
    # Write column names as the first row
    csvwriter.writerow(column_names)
    
    # Write data rows
    csvwriter.writerows(rows)

# Close SQLite connection
sqlite_conn.close()
