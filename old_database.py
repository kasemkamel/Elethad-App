import sqlite3
from tkinter import messagebox

# ('admin', 'W', 'Ac') = (admin , Warehouse worker, Accountant)

class Database:
    def __init__(self, db_name='medicine_warehouse_old.db'):
        self.db_name = db_name

    def connect_db(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        return conn, cursor

    def close_db(self, conn):
        conn.commit()
        conn.close()

    def create_database(self):
        conn, cursor = self.connect_db()

        # Create Medicines table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            quantity INTEGER NOT NULL DEFAULT 0,
            price FLOAT,
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

        # Create Stock table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medicine_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (medicine_id) REFERENCES Medicines(id)
        )
        ''')

        self.close_db(conn)


class User:
    def __init__(self, db):
        self.db = db

    def insert(self, username, password, role):
        conn, cursor = self.db.connect_db()
        try:
            cursor.execute('''
            INSERT INTO Users (username, password, role) VALUES (?, ?, ?)
            ''', (username, password, role))
        except sqlite3.IntegrityError as e:
            messagebox.showerror("Error", f"Error inserting user: {e}")
        self.db.close_db(conn)

    def update(self, user_id, username=None, password=None, role=None):
        conn, cursor = self.db.connect_db()
        updates = []
        parameters = []

        if username:
            updates.append("username = ?")
            parameters.append(username)
        if password:
            updates.append("password = ?")
            parameters.append(password)
        if role:
            updates.append("role = ?")
            parameters.append(role)

        if updates:
            parameters.append(user_id)
            cursor.execute(f'''
            UPDATE Users
            SET {', '.join(updates)}
            WHERE id = ?
            ''', parameters)
        else:
            messagebox.showerror("Error", "No fields to update.")
        self.db.close_db(conn)

    def delete(self, user_id):
        conn, cursor = self.db.connect_db()
        cursor.execute('''
        DELETE FROM Users WHERE id = ?
        ''', (user_id,))
        self.db.close_db(conn)

    def select_all(self):
        conn, cursor = self.db.connect_db()
        cursor.execute('''
        SELECT * FROM Users
        ''')
        users = cursor.fetchall()
        self.db.close_db(conn)
        return users

    def select_by_id(self, user_id):
        conn, cursor = self.db.connect_db()
        cursor.execute('''
        SELECT * FROM Users WHERE id = ?
        ''', (user_id,))
        user = cursor.fetchone()
        self.db.close_db(conn)
        return user

    def select_by_credentials(self, username, password):
        conn, cursor = self.db.connect_db()
        cursor.execute('''
        SELECT * FROM Users WHERE username = ? AND password = ?
        ''', (username, password))
        user = cursor.fetchone()
        self.db.close_db(conn)
        return user


class Medicine:
    def __init__(self, db):
        self.db = db

    def insert(self, name, description, price, supplier_id=None):
        conn, cursor = self.db.connect_db()
        cursor.execute('''
        INSERT INTO Medicines (name, description, price, supplier_id) VALUES (?, ?, ?, ?)
        ''', (name, description, price, supplier_id))
        self.db.close_db(conn)

    def update(self, medicine_id, name=None, description=None, price=None, supplier_id=None):
        conn, cursor = self.db.connect_db()
        updates = []
        parameters = []

        if name:
            updates.append("name = ?")
            parameters.append(name)
        if description:
            updates.append("description = ?")
            parameters.append(description)
        if price:
            updates.append("price = ?")
            parameters.append(price)
        if supplier_id is not None:
            updates.append("supplier_id = ?")
            parameters.append(supplier_id)

        if updates:
            parameters.append(medicine_id)
            cursor.execute(f'''
            UPDATE Medicines
            SET {', '.join(updates)}
            WHERE id = ?
            ''', parameters)
        else:
            messagebox.showerror("Error", "No fields to update.")
        self.db.close_db(conn)

    def delete(self, medicine_id):
        conn, cursor = self.db.connect_db()
        cursor.execute('''
        DELETE FROM Medicines WHERE id = ?
        ''', (medicine_id,))
        self.db.close_db(conn)

    def select_all(self):
        conn, cursor = self.db.connect_db()
        cursor.execute('''
        SELECT * FROM Medicines
        ''')
        medicines = cursor.fetchall()
        self.db.close_db(conn)
        return medicines
    
    def select_id_name(self):
        conn, cursor = self.db.connect_db()
        cursor.execute("SELECT id, name FROM Medicines")
        medicines = cursor.fetchall()
        self.db.close_db(conn)
        return medicines


class Supplier:
    def __init__(self, db):
        self.db = db

    def insert(self, name, contact_info):
        conn, cursor = self.db.connect_db()
        cursor.execute('''
        INSERT INTO Suppliers (name, contact_info) VALUES (?, ?)
        ''', (name, contact_info))
        self.db.close_db(conn)

    def update(self, supplier_id, name=None, contact_info=None):
        conn, cursor = self.db.connect_db()
        updates = []
        parameters = []

        if name:
            updates.append("name = ?")
            parameters.append(name)
        if contact_info:
            updates.append("contact_info = ?")
            parameters.append(contact_info)

        if updates:
            parameters.append(supplier_id)
            cursor.execute(f'''
            UPDATE Suppliers
            SET {', '.join(updates)}
            WHERE id = ?
            ''', parameters)
        else:
            messagebox.showerror("Error", "No fields to update.")
        self.db.close_db(conn)

    def delete(self, supplier_id_or_name):
        conn, cursor = self.db.connect_db()
        cursor.execute('''
        DELETE FROM Suppliers WHERE id = ? or name = ?
        ''', (supplier_id_or_name,supplier_id_or_name))
        self.db.close_db(conn)

    def select_all(self):
        conn, cursor = self.db.connect_db()
        cursor.execute('''
        SELECT * FROM Suppliers
        ''')
        suppliers = cursor.fetchall()
        self.db.close_db(conn)
        return suppliers

    def select_id_name(self):
        conn, cursor = self.db.connect_db()
        cursor.execute("SELECT id, name FROM Suppliers")
        suppliers = cursor.fetchall()
        conn.close()
        return suppliers
        
        
      
class Stock: # This class manages the stock of medicines
    """This class manages the stock of medicines in the database.
    It allows inserting, updating, deleting, and selecting stock entries.
    It also updates the Medicines table to reflect changes in stock.
    """
    # The Stock table is used to track the quantity of each medicine in stock.
    def __init__(self, db):
        self.db = db

    # The Stock table has a foreign key relationship with the Medicines table.
    def insert(self, medicine_id, quantity):
        conn, cursor = self.db.connect_db()
        try:
            cursor.execute('''INSERT INTO Stock (medicine_id, quantity) VALUES (?, ?)''', (medicine_id, quantity))
            
            cursor.execute('''
                UPDATE Medicines
                SET quantity = quantity + ?
                WHERE id = ?
            ''', (quantity, medicine_id))
            
            conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error inserting Stock: {e}")
        finally:
            self.db.close_db(conn)

    # The update method allows updating the stock entry for a specific medicine.
    def update(self, stock_id, medicine_id=None, quantity=None):
        conn, cursor = self.db.connect_db()
    
        old_quantity = None

        if quantity is not None:
            cursor.execute('''SELECT quantity, medicine_id FROM Stock WHERE id = ?''', (stock_id,))
            stock_entry = cursor.fetchone()
            if stock_entry:
                old_quantity, medicine_id = stock_entry 
        updates = []
        parameters = []

        if medicine_id is not None:
            updates.append("medicine_id = ?")
            parameters.append(medicine_id)
        if quantity is not None:
            updates.append("quantity = ?")
            parameters.append(quantity)

        if updates:
            parameters.append(stock_id)
            cursor.execute(f'''
            UPDATE Stock
            SET {', '.join(updates)}
            WHERE id = ?
            ''', parameters)

            if quantity is not None:
                quantity_difference = (quantity - old_quantity) if old_quantity is not None else quantity
                cursor.execute('''
                    UPDATE Medicines
                    SET quantity = quantity + ?
                    WHERE id = ?
                ''', (quantity_difference, medicine_id))

            conn.commit() 
        else:
            messagebox.showerror("Error", "No fields to update.")
        self.db.close_db(conn)

    # The delete method allows deleting a stock entry and updates the Medicines table accordingly.
    def delete(self, stock_id):
        conn, cursor = self.db.connect_db()

        # Fetch the quantity and medicine_id before deletion
        cursor.execute('''SELECT quantity, medicine_id FROM Stock WHERE id = ?''', (stock_id,))
        stock_entry = cursor.fetchone()

        if stock_entry:
            quantity, medicine_id = stock_entry

            # Delete the stock entry
            cursor.execute('''DELETE FROM Stock WHERE id = ?''', (stock_id,))
            
            # Update the Medicines table to decrease the total quantity
            cursor.execute('''
                UPDATE Medicines
                SET quantity = quantity - ?
                WHERE id = ?
            ''', (quantity, medicine_id))
            
            conn.commit()  # Commit both operations
        else:
            messagebox.showerror("Error", "No fields to update.")
        self.db.close_db(conn)

    # The select_all method retrieves all stock entries from the Stock table.
    def select_all(self):
        conn, cursor = self.db.connect_db()
        cursor.execute('''
        SELECT * FROM Stock
        ''')
        stock_entries = cursor.fetchall()
        self.db.close_db(conn)
        return stock_entries

    # The select_by_medicine method retrieves stock entries for a specific medicine.    
    def select_by_medicine(self, medicine_id):
        conn, cursor = self.db.connect_db()
        cursor.execute('''
        SELECT * FROM Stock WHERE medicine_id = ?
        ''', (medicine_id,))
        stock_entry = cursor.fetchone()
        self.db.close_db(conn)
        return stock_entry


class Transaction:
    def __init__(self, db):
        self.db = db

    def insert(self, medicine_id, transaction_type, quantity, user_id, date=None):
        conn, cursor = self.db.connect_db()
        cursor.execute('''
        INSERT INTO Transactions (medicine_id, transaction_type, quantity, user_id, date)
        VALUES (?, ?, ?, ?, COALESCE(?, CURRENT_TIMESTAMP))
        ''', (medicine_id, transaction_type, quantity, user_id, date))
        self.db.close_db(conn)

    def select_all(self):
        conn, cursor = self.db.connect_db()
        cursor.execute('''
        SELECT * FROM Transactions
        ''')
        transactions = cursor.fetchall()
        self.db.close_db(conn)
        return transactions

    def select_by_medicine(self, medicine_id):
        conn, cursor = self.db.connect_db()
        cursor.execute('''
        SELECT * FROM Transactions WHERE medicine_id = ?
        ''', (medicine_id,))
        transactions = cursor.fetchall()
        self.db.close_db(conn)
        return transactions

    def select_by_user(self, user_id):
        conn, cursor = self.db.connect_db()
        cursor.execute('''
        SELECT * FROM Transactions WHERE user_id = ?
        ''', (user_id,))
        transactions = cursor.fetchall()
        self.db.close_db(conn)
        return transactions



# db = Database()
# db.create_database()
# user_manager = User(db)
# print(user_manager.select_all())
# # default
# user_manager.insert('admin', 'admin', 'admin')
# print(user_manager.select_all())

