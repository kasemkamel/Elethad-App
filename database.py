import sqlite3

def create_database():
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('medicine_warehouse.db')
    cursor = conn.cursor()

    # Create Medicines table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Medicines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        quantity INTEGER NOT NULL,
        expiry_date DATE,
        reorder_level INTEGER NOT NULL,
        supplier_id INTEGER,
        FOREIGN KEY (supplier_id) REFERENCES Suppliers(id)
    )
    ''')

    # Create Suppliers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Suppliers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        contact_info TEXT
    )
    ''')

    # Create Transactions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        medicine_id INTEGER,
        transaction_type TEXT NOT NULL CHECK (transaction_type IN ('incoming', 'outgoing')),
        quantity INTEGER NOT NULL,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        user_id INTEGER,
        FOREIGN KEY (medicine_id) REFERENCES Medicines(id),
        FOREIGN KEY (user_id) REFERENCES Users(id)
    )
    ''')

    # Create Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        role TEXT NOT NULL CHECK (role IN ('admin', 'W', 'Ac'))
    )
    ''')

    # Commit the changes
    conn.commit()

    # List of users to add (ensure roles are valid)
    users = [
        ('kasem', 'kasem', 'AC'), 
        ('kasem', 'kasem', 'W'), 
        ('admin', 'admin', 'admin'),
        ("kasem", "kasem", 'admin')  # All roles must be valid according to the CHECK constraint
    ]

    # Insert users into the Users table
    try:
        cursor.executemany('''
        INSERT INTO Users (username, password, role) VALUES (?, ?, ?)
        ''', users)
    except sqlite3.IntegrityError as e:
        print(f"Error inserting users: {e}")

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    print("Database and tables created successfully. Users added.")

if __name__ == "__main__":
    create_database()
