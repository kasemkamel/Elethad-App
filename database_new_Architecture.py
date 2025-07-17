
import sqlite3
import hashlib
import logging
from datetime import datetime, timedelta
from tkinter import messagebox
from contextlib import contextmanager


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_name='medicine_warehouse.db'):
        self.db_name = db_name
        self.setup_database()

    def connect_db(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        return conn, cursor

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_name)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            yield conn
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def setup_database(self):
        """Initialize database with all tables"""
        self.create_database()
        self.create_default_admin()

    def create_database(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Enhanced Medicines table with additional fields
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS Medicines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                quantity INTEGER NOT NULL DEFAULT 0,
                price FLOAT NOT NULL CHECK (price >= 0),
                supplier_id INTEGER,
                batch_number TEXT,
                expiry_date DATE,
                minimum_stock INTEGER DEFAULT 10,
                maximum_stock INTEGER DEFAULT 1000,
                location TEXT,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (supplier_id) REFERENCES Suppliers(id),
                CHECK (maximum_stock >= minimum_stock)
            )
            ''')

            # Enhanced Suppliers table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS Suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                contact_info TEXT,
                email TEXT,
                phone TEXT,
                address TEXT,
                status TEXT DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')

            # Enhanced Transactions table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS Transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                medicine_id INTEGER NOT NULL,
                transaction_type TEXT NOT NULL CHECK (transaction_type IN ('incoming', 'outgoing')),
                quantity INTEGER NOT NULL CHECK (quantity > 0),
                unit_price FLOAT,
                total_amount FLOAT,
                batch_number TEXT,
                expiry_date DATE,
                reason TEXT,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER NOT NULL,
                FOREIGN KEY (medicine_id) REFERENCES Medicines(id),
                FOREIGN KEY (user_id) REFERENCES Users(id)
            )
            ''')

            # Enhanced Users table with additional security
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('admin', 'warehouse_worker', 'accountant')),
                full_name TEXT,
                email TEXT,
                is_active BOOLEAN DEFAULT 1,
                last_login TIMESTAMP,
                failed_login_attempts INTEGER DEFAULT 0,
                account_locked_until TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')

            # Remove Stock table - redundant with Medicines quantity
            cursor.execute('DROP TABLE IF EXISTS Stock')

            # Create audit trail table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS AuditLog (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_name TEXT NOT NULL,
                record_id INTEGER NOT NULL,
                action TEXT NOT NULL CHECK (action IN ('INSERT', 'UPDATE', 'DELETE')),
                old_values TEXT,
                new_values TEXT,
                user_id INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES Users(id)
            )
            ''')

            # Create alerts table for low stock notifications
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS StockAlerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                medicine_id INTEGER NOT NULL,
                alert_type TEXT NOT NULL CHECK (alert_type IN ('low_stock', 'expiry_warning', 'expired')),
                message TEXT NOT NULL,
                is_resolved BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP,
                FOREIGN KEY (medicine_id) REFERENCES Medicines(id)
            )
            ''')

            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_medicines_name ON Medicines(name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_medicines_supplier ON Medicines(supplier_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_medicine ON Transactions(medicine_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_user ON Transactions(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_date ON Transactions(date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON Users(username)')
            
            conn.commit()

    def create_default_admin(self):
        """Create default admin user if none exists"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM Users WHERE role = "admin"')
            if cursor.fetchone()[0] == 0:
                user_manager = User(self)
                user_manager.create_user('admin', 'admin123', 'admin', 'System Administrator')
                logger.info("Default admin user created")


class SecurityMixin:
    """Mixin class for password hashing and security features"""
    
    @staticmethod
    def hash_password(password, salt=None):
        """Hash password with salt"""
        if salt is None:
            salt = hashlib.sha256(str(datetime.now()).encode()).hexdigest()[:16]
        
        password_hash = hashlib.pbkdf2_hmac('sha256', 
                                          password.encode('utf-8'), 
                                          salt.encode('utf-8'), 
                                          100000)
        return password_hash.hex(), salt

    @staticmethod
    def verify_password(password, stored_hash, salt):
        """Verify password against stored hash"""
        password_hash, _ = SecurityMixin.hash_password(password, salt)
        return password_hash == stored_hash

    def check_account_lockout(self, user_data):
        """Check if account is locked due to failed attempts"""
        if user_data['account_locked_until']:
            lockout_time = datetime.fromisoformat(user_data['account_locked_until'])
            if datetime.now() < lockout_time:
                return True
        return False


class User(SecurityMixin):
    def __init__(self, db):
        self.db = db
        self.max_failed_attempts = 5
        self.lockout_duration = timedelta(minutes=15)

    def create_user(self, username, password, role, full_name=None, email=None):
        """Create new user with hashed password"""
        password_hash, salt = self.hash_password(password)
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                INSERT INTO Users (username, password_hash, salt, role, full_name, email) 
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (username, password_hash, salt, role, full_name, email))
                conn.commit()
                logger.info(f"User {username} created successfully")
                return cursor.lastrowid
            except sqlite3.IntegrityError as e:
                logger.error(f"Error creating user {username}: {e}")
                messagebox.showerror("Error", f"Username already exists: {username}")
                return None

    def authenticate(self, username, password):
        """Authenticate user with security checks"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM Users WHERE username = ? AND is_active = 1', (username,))
            user_data = cursor.fetchone()
            
            if not user_data:
                logger.warning(f"Authentication failed for {username}: User not found")
                return None
            
            user_dict = dict(user_data)
            
            # Check account lockout
            if self.check_account_lockout(user_dict):
                logger.warning(f"Authentication failed for {username}: Account locked")
                messagebox.showerror("Error", "Account is temporarily locked due to multiple failed attempts")
                return None
            
            # Verify password
            if self.verify_password(password, user_dict['password_hash'], user_dict['salt']):
                # Reset failed attempts and update last login
                cursor.execute('''
                UPDATE Users 
                SET failed_login_attempts = 0, last_login = CURRENT_TIMESTAMP,
                    account_locked_until = NULL
                WHERE id = ?
                ''', (user_dict['id'],))
                conn.commit()
                logger.info(f"User {username} authenticated successfully")
                return user_dict
            else:
                # Increment failed attempts
                new_attempts = user_dict['failed_login_attempts'] + 1
                lockout_time = None
                
                if new_attempts >= self.max_failed_attempts:
                    lockout_time = datetime.now() + self.lockout_duration
                    
                cursor.execute('''
                UPDATE Users 
                SET failed_login_attempts = ?, account_locked_until = ?
                WHERE id = ?
                ''', (new_attempts, lockout_time, user_dict['id']))
                conn.commit()
                
                logger.warning(f"Authentication failed for {username}: Invalid password")
                return None

    def update_user(self, user_id, username=None, password=None, role=None, full_name=None, email=None):
        """Update user with proper validation"""
        updates = []
        parameters = []
        
        if username:
            updates.append("username = ?")
            parameters.append(username)
        if password:
            password_hash, salt = self.hash_password(password)
            updates.append("password_hash = ?")
            updates.append("salt = ?")
            parameters.extend([password_hash, salt])
        if role:
            updates.append("role = ?")
            parameters.append(role)
        if full_name:
            updates.append("full_name = ?")
            parameters.append(full_name)
        if email:
            updates.append("email = ?")
            parameters.append(email)
        
        if updates:
            updates.append("updated_at = CURRENT_TIMESTAMP")
            parameters.append(user_id)
            
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f'''
                UPDATE Users SET {', '.join(updates)} WHERE id = ?
                ''', parameters)
                conn.commit()
                logger.info(f"User {user_id} updated successfully")
        else:
            messagebox.showerror("Error", "No fields to update")

    def deactivate_user(self, user_id):
        """Soft delete - deactivate user instead of hard delete"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE Users SET is_active = 0 WHERE id = ?', (user_id,))
            conn.commit()
            logger.info(f"User {user_id} deactivated")

    def get_all_users(self):
        """Get all active users"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, username, role, full_name, email, last_login FROM Users WHERE is_active = 1')
            return cursor.fetchall()

    def get_user_by_id(self, user_id):
        """Get user by ID"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM Users WHERE id = ? AND is_active = 1', (user_id,))
            return cursor.fetchone()


class Medicine:
    def __init__(self, db):
        self.db = db

    def add_medicine(self, name, description, price, supplier_id=None, batch_number=None, 
                    expiry_date=None, minimum_stock=10, maximum_stock=1000, location=None, category=None):
        """Add new medicine with validation"""
        if price < 0:
            messagebox.showerror("Error", "Price cannot be negative")
            return None
            
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO Medicines (name, description, price, supplier_id, batch_number, 
                                 expiry_date, minimum_stock, maximum_stock, location, category)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, description, price, supplier_id, batch_number, expiry_date, 
                  minimum_stock, maximum_stock, location, category))
            conn.commit()
            medicine_id = cursor.lastrowid
            logger.info(f"Medicine {name} added with ID {medicine_id}")
            return medicine_id

    def update_stock(self, medicine_id, quantity_change, transaction_type, user_id, 
                    batch_number=None, expiry_date=None, reason=None):
        """Update medicine stock with transaction logging"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get current stock
            cursor.execute('SELECT quantity, price FROM Medicines WHERE id = ?', (medicine_id,))
            result = cursor.fetchone()
            if not result:
                messagebox.showerror("Error", "Medicine not found")
                return False
            
            current_quantity, unit_price = result
            
            # Calculate new quantity
            if transaction_type == 'incoming':
                new_quantity = current_quantity + quantity_change
            else:  # outgoing
                if current_quantity < quantity_change:
                    messagebox.showerror("Error", "Insufficient stock")
                    return False
                new_quantity = current_quantity - quantity_change
            
            # Update medicine quantity
            cursor.execute('''
            UPDATE Medicines 
            SET quantity = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
            ''', (new_quantity, medicine_id))
            
            # Log transaction
            total_amount = quantity_change * unit_price if unit_price else None
            cursor.execute('''
            INSERT INTO Transactions (medicine_id, transaction_type, quantity, unit_price, 
                                    total_amount, batch_number, expiry_date, reason, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (medicine_id, transaction_type, quantity_change, unit_price, total_amount,
                  batch_number, expiry_date, reason, user_id))
            
            conn.commit()
            
            # Check for low stock alerts
            self.check_stock_alerts(medicine_id)
            
            logger.info(f"Stock updated for medicine {medicine_id}: {transaction_type} {quantity_change}")
            return True

    def check_stock_alerts(self, medicine_id):
        """Check and create stock alerts"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT name, quantity, minimum_stock, expiry_date 
            FROM Medicines WHERE id = ?
            ''', (medicine_id,))
            result = cursor.fetchone()
            
            if result:
                name, quantity, min_stock, expiry_date = result
                
                # Low stock alert
                if quantity <= min_stock:
                    cursor.execute('''
                    INSERT OR IGNORE INTO StockAlerts (medicine_id, alert_type, message)
                    VALUES (?, 'low_stock', ?)
                    ''', (medicine_id, f"Low stock alert: {name} has only {quantity} units left"))
                
                # Expiry alerts
                if expiry_date:
                    expiry_dt = datetime.strptime(expiry_date, '%Y-%m-%d')
                    days_to_expiry = (expiry_dt - datetime.now()).days
                    
                    if days_to_expiry <= 0:
                        cursor.execute('''
                        INSERT OR IGNORE INTO StockAlerts (medicine_id, alert_type, message)
                        VALUES (?, 'expired', ?)
                        ''', (medicine_id, f"EXPIRED: {name} expired on {expiry_date}"))
                    elif days_to_expiry <= 30:
                        cursor.execute('''
                        INSERT OR IGNORE INTO StockAlerts (medicine_id, alert_type, message)
                        VALUES (?, 'expiry_warning', ?)
                        ''', (medicine_id, f"Expiry warning: {name} expires in {days_to_expiry} days"))
                
                conn.commit()

    def get_low_stock_medicines(self):
        """Get medicines with low stock"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT id, name, quantity, minimum_stock 
            FROM Medicines 
            WHERE quantity <= minimum_stock AND quantity > 0
            ORDER BY (quantity * 1.0 / minimum_stock) ASC
            ''')
            return cursor.fetchall()

    def get_expired_medicines(self):
        """Get expired medicines"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT id, name, expiry_date, quantity 
            FROM Medicines 
            WHERE expiry_date IS NOT NULL AND expiry_date < date('now')
            ORDER BY expiry_date ASC
            ''')
            return cursor.fetchall()

    def get_all_medicines(self):
        """Get all medicines with supplier info"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT m.*, s.name as supplier_name 
            FROM Medicines m 
            LEFT JOIN Suppliers s ON m.supplier_id = s.id
            ORDER BY m.name
            ''')
            return cursor.fetchall()

    def get_medicine_count(self):
        """Get total count of medicines"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM Medicines')
            return cursor.fetchone()[0]

    def search_medicines(self, search_term):
        """Search medicines by name or description"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT m.*, s.name as supplier_name 
            FROM Medicines m 
            LEFT JOIN Suppliers s ON m.supplier_id = s.id
            WHERE m.name LIKE ? OR m.description LIKE ?
            ORDER BY m.name
            ''', (f'%{search_term}%', f'%{search_term}%'))
            return cursor.fetchall()


class Supplier:
    def __init__(self, db):
        self.db = db

    def add_supplier(self, name, contact_info=None, email=None, phone=None, address=None):
        """Add new supplier"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                INSERT INTO Suppliers (name, contact_info, email, phone, address)
                VALUES (?, ?, ?, ?, ?)
                ''', (name, contact_info, email, phone, address))
                conn.commit()
                supplier_id = cursor.lastrowid
                logger.info(f"Supplier {name} added with ID {supplier_id}")
                return supplier_id
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", f"Supplier {name} already exists")
                return None

    def get_all_suppliers(self):
        """Get all active suppliers"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM Suppliers WHERE status = "active" ORDER BY name')
            return cursor.fetchall()

    def get_supplier_count(self):
        """Get total count of suppliers"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM Suppliers WHERE status = "active"')
            return cursor.fetchone()[0]

    def get_supplier_medicines(self, supplier_id):
        """Get all medicines from a specific supplier"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT * FROM Medicines WHERE supplier_id = ? ORDER BY name
            ''', (supplier_id,))
            return cursor.fetchall()


class Reports:
    def __init__(self, db):
        self.db = db

    def get_stock_report(self):
        """Generate comprehensive stock report"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT 
                m.name,
                m.quantity,
                m.minimum_stock,
                m.maximum_stock,
                m.price,
                (m.quantity * m.price) as stock_value,
                s.name as supplier_name,
                m.expiry_date,
                CASE 
                    WHEN m.quantity <= m.minimum_stock THEN 'LOW'
                    WHEN m.quantity >= m.maximum_stock THEN 'OVERSTOCKED'
                    ELSE 'NORMAL'
                END as stock_status
            FROM Medicines m
            LEFT JOIN Suppliers s ON m.supplier_id = s.id
            ORDER BY stock_value DESC
            ''')
            return cursor.fetchall()

    def get_transaction_report(self, start_date=None, end_date=None):
        """Generate transaction report for date range"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            query = '''
            SELECT 
                t.date,
                m.name as medicine_name,
                t.transaction_type,
                t.quantity,
                t.unit_price,
                t.total_amount,
                u.username,
                t.reason
            FROM Transactions t
            JOIN Medicines m ON t.medicine_id = m.id
            JOIN Users u ON t.user_id = u.id
            '''
            
            params = []
            if start_date and end_date:
                query += ' WHERE t.date BETWEEN ? AND ?'
                params = [start_date, end_date]
            
            query += ' ORDER BY t.date DESC'
            
            cursor.execute(query, params)
            return cursor.fetchall()

    def get_financial_summary(self, start_date=None, end_date=None):
        """Generate financial summary"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total stock value
            cursor.execute('SELECT SUM(quantity * price) FROM Medicines')
            total_stock_value = cursor.fetchone()[0] or 0
            
            # Transaction totals
            query = '''
            SELECT 
                transaction_type,
                SUM(total_amount) as total_amount,
                COUNT(*) as transaction_count
            FROM Transactions
            WHERE total_amount IS NOT NULL
            '''
            
            params = []
            if start_date and end_date:
                query += ' AND date BETWEEN ? AND ?'
                params = [start_date, end_date]
            
            query += ' GROUP BY transaction_type'
            
            cursor.execute(query, params)
            transactions = cursor.fetchall()
            
            return {
                'total_stock_value': total_stock_value,
                'transactions': transactions
            }
        
    def get_total_monthly_sales_report(self, month=None, year=None) -> float:
        """
        Generate total monthly sales report for specified month and year.
        
        Args:
            month (int, optional): Month (1-12). Defaults to current month.
            year (int, optional): Year. Defaults to current year.
        
        Returns:
            float: Total sales amount for the specified month
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT 
                SUM(COALESCE(t.total_amount, t.quantity * t.unit_price, 0)) as total_sales,
                COUNT(*) as transaction_count,
                SUM(t.quantity) as total_quantity_sold
            FROM Transactions t
            WHERE t.transaction_type = 'outgoing'
            AND strftime('%Y', t.date) = ?
            AND strftime('%m', t.date) = ?
            AND t.total_amount IS NOT NULL
            ''', (str(year), f"{month:02d}"))
            
            result = cursor.fetchone()
            
            if result and result[0]:
                total_sales = float(result[0])
                transaction_count = result[1]
                total_quantity = result[2]
                
                logger.info(f"Monthly sales report for {month}/{year}: "
                        f"Total Sales: ${total_sales:.2f}, "
                        f"Transactions: {transaction_count}, "
                        f"Items Sold: {total_quantity}")
                
                return total_sales
            else:
                logger.info(f"No sales data found for {month}/{year}")
                return 0.0
    
    def get_detailed_monthly_sales_report(self, now, month=None, year=None) -> dict:
        """
        Generate detailed monthly sales report with breakdown by medicine.
        
        Args:
            month (int, optional): Month (1-12). Defaults to current month.
            year (int, optional): Year. Defaults to current year.
        
        Returns:
            dict: Detailed sales report including total, breakdown by medicine, and summary stats
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT 
                m.name as medicine_name,
                m.category,
                SUM(t.quantity) as total_quantity_sold,
                AVG(t.unit_price) as avg_unit_price,
                SUM(COALESCE(t.total_amount, t.quantity * t.unit_price, 0)) as total_revenue,
                COUNT(*) as transaction_count,
                s.name as supplier_name
            FROM Transactions t
            JOIN Medicines m ON t.medicine_id = m.id
            LEFT JOIN Suppliers s ON m.supplier_id = s.id
            WHERE t.transaction_type = 'outgoing'
            AND strftime('%Y', t.date) = ?
            AND strftime('%m', t.date) = ?
            AND t.total_amount IS NOT NULL
            GROUP BY m.id, m.name, m.category, s.name
            ORDER BY total_revenue DESC
            ''', (str(year), f"{month:02d}"))
            
            medicine_breakdown = cursor.fetchall()

            cursor.execute('''
            SELECT 
                SUM(COALESCE(t.total_amount, t.quantity * t.unit_price, 0)) as total_sales,
                COUNT(*) as total_transactions,
                SUM(t.quantity) as total_quantity_sold,
                COUNT(DISTINCT t.medicine_id) as unique_medicines_sold
            FROM Transactions t
            WHERE t.transaction_type = 'outgoing'
            AND strftime('%Y', t.date) = ?
            AND strftime('%m', t.date) = ?
            AND t.total_amount IS NOT NULL
            ''', (str(year), f"{month:02d}"))
            
            totals = cursor.fetchone()
            
            cursor.execute('''
            SELECT 
                m.name,
                SUM(t.quantity) as quantity_sold,
                SUM(COALESCE(t.total_amount, t.quantity * t.unit_price, 0)) as revenue
            FROM Transactions t
            JOIN Medicines m ON t.medicine_id = m.id
            WHERE t.transaction_type = 'outgoing'
            AND strftime('%Y', t.date) = ?
            AND strftime('%m', t.date) = ?
            AND t.total_amount IS NOT NULL
            GROUP BY m.id, m.name
            ORDER BY quantity_sold DESC
            LIMIT 10
            ''', (str(year), f"{month:02d}"))
            
            top_selling = cursor.fetchall()
            
            cursor.execute('''
            SELECT 
                m.category,
                SUM(COALESCE(t.total_amount, t.quantity * t.unit_price, 0)) as category_revenue,
                SUM(t.quantity) as category_quantity,
                COUNT(*) as category_transactions
            FROM Transactions t
            JOIN Medicines m ON t.medicine_id = m.id
            WHERE t.transaction_type = 'outgoing'
            AND strftime('%Y', t.date) = ?
            AND strftime('%m', t.date) = ?
            AND t.total_amount IS NOT NULL
            GROUP BY m.category
            ORDER BY category_revenue DESC
            ''', (str(year), f"{month:02d}"))
            
            category_breakdown = cursor.fetchall()
            
            report = {
                'month': month,
                'year': year,
                'total_sales': float(totals[0]) if totals[0] else 0.0,
                'total_transactions': totals[1] if totals[1] else 0,
                'total_quantity_sold': totals[2] if totals[2] else 0,
                'unique_medicines_sold': totals[3] if totals[3] else 0,
                'medicine_breakdown': [dict(row) for row in medicine_breakdown],
                'top_selling_medicines': [dict(row) for row in top_selling],
                'category_breakdown': [dict(row) for row in category_breakdown],
                'generated_at': now.isoformat()
            }
            
            logger.info(f"Detailed monthly sales report generated for {month}/{year}: "
                    f"Total Sales: ${report['total_sales']:.2f}")
            
            return report








# # Example usage and testing
# if __name__ == "__main__":
#     # Initialize database
#     db = Database()
    
#     # Create managers
#     user_manager = User(db)
#     medicine_manager = Medicine(db)
#     supplier_manager = Supplier(db)
#     reports = Reports(db)
    
#     # Test authentication
#     admin_user = user_manager.authenticate('admin', 'admin123')
#     if admin_user:
#         print("Admin authenticated successfully")
        
#         # Add sample data
#         supplier_id = supplier_manager.add_supplier("MediCorp", "contact@medicorp.com", "medicorp@example.com", "123-456-7890")
#         if supplier_id:
#             medicine_id = medicine_manager.add_medicine("Aspirin", "Pain reliever", 5.99, supplier_id, "BATCH001", "2025-12-31", 50, 500, "A1-01", "Analgesic")
#             if medicine_id:
#                 # Add stock
#                 medicine_manager.update_stock(medicine_id, 100, 'incoming', admin_user['id'], "BATCH001", "2025-12-31", "Initial stock")
                
#                 # Test reports
#                 stock_report = reports.get_stock_report()
#                 print(f"Stock report generated with {len(stock_report)} items")
#     else:
#         print("Authentication failed")



