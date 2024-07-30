import sqlite3
import csv

"""This class is responsible for initialization of database connection"""

class Database:
    #Initialize the database connection
    def __init__(self, db_name):
        self.db_name = db_name
        self.connection = None
        self.cursor = None

    #Connect to the SQLite database and create a cursor
    def connect(self):
        try:
            self.connection = sqlite3.connect(self.db_name)
            self.cursor = self.connection.cursor()
            print(f"Connected to database '{self.db_name}'.")
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")

    #To execute query
    def execute_query(self, query, params=None):
        if not self.cursor:
            raise ConnectionError("Database not connected.")
        
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error executing query: {e}")
            return []

    #To commit 
    def commit(self):
        if self.connection:
            try:
                self.connection.commit()
            except sqlite3.Error as e:
                print(f"Error committing transaction: {e}")

    #To close connection
    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print(f"Connection to database '{self.db_name}' closed.")


"""TableManager class is responsible for managing all tables and operations included in project and queries
    to create tables are written in the functions"""

class TableManager:
    def __init__(self, db):
        #Initializatio of the TableManager with a Database instance
        self.db = db

    def create_tables(self):
        try:
            self.create_customers_table()
            self.create_products_table()
            self.create_orders_table()
            self.create_order_details_table()
        except Exception as e:
            print(f"Error creating tables: {e}")


    #Customer Table
    def create_customers_table(self):
        query = '''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        );
        '''
        self.db.execute_query(query)
        self.db.commit()
        print("Customers table created.")


    #Product Table
    def create_products_table(self):
        query = '''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 0

        );
        '''
        self.db.execute_query(query)
        self.db.commit()
        print("Products table created.")


    #Order Table
    def create_orders_table(self):
        query = '''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            order_date TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        );
        '''
        self.db.execute_query(query)
        self.db.commit()
        print("Orders table created.")


    #Order_Detail Table
    def create_order_details_table(self):
        query = '''
        CREATE TABLE IF NOT EXISTS order_details (
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (product_id) REFERENCES products(id),
            PRIMARY KEY (order_id, product_id)
        );
        '''
        self.db.execute_query(query)
        self.db.commit()
        print("Order Details table created.")
    

    #Add new customr to database
    def add_customer(self, name, email):
        query = '''
        INSERT INTO customers (name, email) VALUES (?, ?)
        '''
        try:
            self.db.execute_query(query, (name, email))
            self.db.commit()
            print(f"Customer '{name}' added.")
        except sqlite3.Error as e:
            print(f"Error adding customer: {e}")


    #Update a customer
    def update_customer(self, customer_id, new_name, new_email):
        query = '''
        UPDATE customers
        SET name = ?, email = ?
        WHERE id = ?
        '''
        try:
            self.db.execute_query(query, (new_name, new_email, customer_id))
            self.db.commit()
            print(f"Customer ID '{customer_id}' updated.")
        except sqlite3.Error as e:
            print(f"Error updating customer: {e}")


    #Delete a customer
    def delete_customer(self, customer_id):
        # PRECAUTION: Check for existing orders before deleting. So, a customer will not be deleted if it's orders exists.
        try:
            orders = self.db.execute_query('SELECT * FROM orders WHERE customer_id = ?', (customer_id,))
            if orders:
                print(f"Cannot delete customer ID '{customer_id}' as there are existing orders.")
                return
            
            query = '''
            DELETE FROM customers
            WHERE id = ?
            '''
            self.db.execute_query(query, (customer_id,))
            self.db.commit()
            print(f"Customer ID '{customer_id}' deleted.")
        except sqlite3.Error as e:
            print(f"Error deleting customer: {e}")


    #Add product
    def add_product(self, name, price):
        query = '''
        INSERT INTO products (name, price) VALUES (?, ?)
        '''
        try:
            self.db.execute_query(query, (name, price))
            self.db.commit()
            print(f"Product '{name}' added.")
        except sqlite3.Error as e:
            print(f"Error adding product: {e}")
    

    #Update Product
    def update_product(self, product_id, new_price):
        query = '''
        UPDATE products
        SET price = ?
        WHERE id = ?
        '''
        try:
            self.db.execute_query(query, (new_price, product_id))
            self.db.commit()
            print(f"Product ID '{product_id}' price updated.")
        except sqlite3.Error as e:
            print(f"Error updating product: {e}")


    #Delete a product
    def delete_product(self, product_id):
        """Delete a product from the database."""
        # CONSISTENCY: Check for existing order details before deleting. So, that product will not be deleted if it's orders exists
        try:
            order_details = self.db.execute_query('SELECT * FROM order_details WHERE product_id = ?', (product_id,))
            if order_details:
                print(f"Cannot delete product ID '{product_id}' as there are existing order details.")
                return

            query = '''
            DELETE FROM products
            WHERE id = ?
            '''
            self.db.execute_query(query, (product_id,))
            self.db.commit()
            print(f"Product ID '{product_id}' deleted.")
        except sqlite3.Error as e:
            print(f"Error deleting product: {e}")


    #Add order
    def add_order(self, customer_id, order_date, order_details):
        try:
            query = '''
            INSERT INTO orders (customer_id, order_date) VALUES (?, ?)
            '''
            self.db.execute_query(query, (customer_id, order_date))
            self.db.commit()
            
            # Get the last inserted order ID
            order_id = self.db.cursor.lastrowid
            
            # Add the order details to the order_details table
            query = '''
            INSERT INTO order_details (order_id, product_id, quantity) VALUES (?, ?, ?)
            '''
            for product_id, quantity in order_details:
                self.db.execute_query(query, (order_id, product_id, quantity))
            self.db.commit()
            
            print(f"Order ID '{order_id}' added for customer ID '{customer_id}'.")
        except sqlite3.Error as e:
            print(f"Error adding order: {e}")


    #Update an order
    def update_order(self, order_id, new_customer_id, new_order_date, new_order_details):
        try:
            query = '''
            UPDATE orders
            SET customer_id = ?, order_date = ?
            WHERE id = ?
            '''
            self.db.execute_query(query, (new_customer_id, new_order_date, order_id))
            self.db.commit()
            
            # Delete the existing order details
            query = '''
            DELETE FROM order_details
            WHERE order_id = ?
            '''
            self.db.execute_query(query, (order_id,))
            self.db.commit()
            
            # Add the new order details
            query = '''
            INSERT INTO order_details (order_id, product_id, quantity) VALUES (?, ?, ?)
            '''
            for product_id, quantity in new_order_details:
                self.db.execute_query(query, (order_id, product_id, quantity))
            self.db.commit()
            
            print(f"Order ID '{order_id}' updated.")
        except sqlite3.Error as e:
            print(f"Error updating order: {e}")


    #delete an order
    def delete_order(self, order_id):
        try:
            query = '''
            DELETE FROM order_details
            WHERE order_id = ?
            '''
            self.db.execute_query(query, (order_id,))
            self.db.commit()
            
            query = '''
            DELETE FROM orders
            WHERE id = ?
            '''
            self.db.execute_query(query, (order_id,))
            self.db.commit()
            
            print(f"Order ID '{order_id}' deleted.")
        except sqlite3.Error as e:
            print(f"Error deleting order: {e}")


    #Fetch all orders
    def fetch_all_orders(self):
        try:
            query = '''
            SELECT id, customer_id, order_date
            FROM orders
            '''
            orders = self.db.execute_query(query)
        
            print("All Orders:")
            for order in orders:
                order_id, customer_id, order_date = order
                print(f"Order ID: {order_id}, Customer ID: {customer_id}, Order Date: {order_date}")

                # Fetch order details for each order
                query = '''
                SELECT product_id, quantity
                FROM order_details
                WHERE order_id = ?
                '''
                order_details = self.db.execute_query(query, (order_id,))
                for detail in order_details:
                    product_id, quantity = detail
                    print(f"    Product ID: {product_id}, Quantity: {quantity}")
        except sqlite3.Error as e:
            print(f"Error fetching orders: {e}")


    #Generate report
    def generate_report(self, file_name='orders_report.csv'):
        try:
            query = '''
            SELECT orders.id, orders.customer_id, customers.name, orders.order_date
            FROM orders
            JOIN customers ON orders.customer_id = customers.id
            '''
            orders = self.db.execute_query(query)
        
            with open(file_name, 'w', newline='') as csvfile:
                fieldnames = ['Order ID', 'Customer ID', 'Customer Name', 'Order Date', 'Product ID', 'Quantity']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                # Write the header row
                writer.writeheader()
            
                for order in orders:
                    order_id, customer_id, customer_name, order_date = order
                
                    # Fetch order details for each order
                    query = '''
                    SELECT product_id, quantity
                    FROM order_details
                    WHERE order_id = ?
                    '''
                    order_details = self.db.execute_query(query, (order_id,))
                
                    for detail in order_details:
                        product_id, quantity = detail
                    
                        # Write order details to CSV
                        writer.writerow({
                            'Order ID': order_id,
                            'Customer ID': customer_id,
                            'Customer Name': customer_name,
                            'Order Date': order_date,
                            'Product ID': product_id,
                            'Quantity': quantity
                        })

            print(f"Report generated and saved to '{file_name}'.")
        except Exception as e:
            print(f"Error generating report: {e}")


    #search_orders_by_customer_name
    def search_orders_by_customer_name(self, customer_name):
        try:
            query = '''
            SELECT orders.id, orders.customer_id, orders.order_date
            FROM orders
            JOIN customers ON orders.customer_id = customers.id
            WHERE customers.name LIKE ?
            '''
            params = (f'%{customer_name}%',)
            orders = self.db.execute_query(query, params)
        
            print(f"Orders for customer '{customer_name}':")
            for order in orders:
                order_id, customer_id, order_date = order
                print(f"Order ID: {order_id}, Customer ID: {customer_id}, Order Date: {order_date}")
        except sqlite3.Error as e:
            print(f"Error searching orders: {e}")

              


def main():
    db_name = 'Order.db'
    db = Database(db_name)
    db.connect()
    manager = TableManager(db)
    manager.create_tables()

    while True:
        print("\nMenu:")
        print("1. Add Customer")
        print("2. Update Customer")
        print("3. Delete Customer")
        print("4. Add Product")
        print("5. Update Product")
        print("6. Delete Product")
        print("7. Add Order")
        print("8. Update Order")
        print("9. Delete Order")
        print("10. Fetch All Orders")
        print("11. Generate Report")
        print("12. Search Orders by Customer Name")
        print("13. Exit")
        
        choice = input("Enter your choice (1-13): ")

        if choice == '1':
            name = input("Enter customer name: ")
            email = input("Enter customer email: ")
            manager.add_customer(name, email)
        elif choice == '2':
            customer_id = int(input("Enter customer ID to update: "))
            new_name = input("Enter new name: ")
            new_email = input("Enter new email: ")
            manager.update_customer(customer_id, new_name, new_email)
        elif choice == '3':
            customer_id = int(input("Enter customer ID to delete: "))
            manager.delete_customer(customer_id)
        elif choice == '4':
            name = input("Enter product name: ")
            price = float(input("Enter product price: "))
            manager.add_product(name, price)
        elif choice == '5':
            product_id = int(input("Enter product ID to update: "))
            new_price = float(input("Enter new price: "))
            manager.update_product(product_id, new_price)
        elif choice == '6':
            product_id = int(input("Enter product ID to delete: "))
            manager.delete_product(product_id)
        elif choice == '7':
            customer_id = int(input("Enter customer ID for the new order: "))
            order_date = input("Enter order date (YYYY-MM-DD): ")
            order_details = []
            while True:
                product_id = int(input("Enter product ID (or 0 to finish): "))
                if product_id == 0:
                    break
                quantity = int(input("Enter quantity: "))
                order_details.append((product_id, quantity))
            manager.add_order(customer_id, order_date, order_details)
        elif choice == '8':
            order_id = int(input("Enter order ID to update: "))
            new_customer_id = int(input("Enter new customer ID: "))
            new_order_date = input("Enter new order date (YYYY-MM-DD): ")
            new_order_details = []
            while True:
                product_id = int(input("Enter product ID (or 0 to finish): "))
                if product_id == 0:
                    break
                quantity = int(input("Enter quantity: "))
                new_order_details.append((product_id, quantity))
            manager.update_order(order_id, new_customer_id, new_order_date, new_order_details)
        elif choice == '9':
            order_id = int(input("Enter order ID to delete: "))
            manager.delete_order(order_id)
        elif choice == '10':
            manager.fetch_all_orders()
        elif choice == '11':
            file_name = input("Enter CSV file name (e.g., 'report.csv'): ")
            manager.generate_report(file_name)
        elif choice == '12':
            customer_name = input("Enter customer name to search for orders: ")
            manager.search_orders_by_customer_name(customer_name)
        elif choice == '13':
            print("Exiting...")
            break
        else:
            print("Invalid choice, please enter a number between 1 and 13.")
    
    db.close()

if __name__ == '__main__':
    main()
