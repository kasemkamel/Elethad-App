import sqlite3

# Create the SQLite database and add some test users
def setup_users_database():
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        role TEXT
    )
    ''')
    
    # Insert test users (e.g., plain text for demo; use hashed passwords in production)
    users = [
        ('accountant_user', 'password1', 'Ac'), # Ac = Accountant
        ('warehouse_user', 'password2', 'W'), # W = Warehouse Worker
        ('admin_user', 'adminpass', 'Admin'),
        ("kasem", "kss1010", 'Admin')
    ]
    
    cursor.executemany('INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)', users)
    connection.commit()
    connection.close()

setup_users_database()




