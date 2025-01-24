import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QWidget, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt, QThread, Signal, QObject, QMutex, QWaitCondition
from PySide6.QtGui import QColor
from logic import Project
from exporter import export_to_excel
from google_search import search_product
from selenium_scraper import get_product_details
from queue import Queue
import pandas as pd


class ParseWorker(QThread):
    """
    Worker thread for parsing product details.
    """
    finished = Signal(str, float, str, int, str)  # Emits product_name, price, error_message, row_position, link

    def __init__(self, queue, mutex, condition):
        super().__init__()
        self.queue = queue
        self.mutex = mutex
        self.condition = condition
        self.running = True

    def run(self):
        while self.running:
            self.mutex.lock()
            while self.queue.empty() and self.running:
                self.condition.wait(self.mutex)
            if not self.running:
                self.mutex.unlock()
                break
            product_name, quantity, row_position, link = self.queue.get()
            self.mutex.unlock()

            try:
                if link:
                    # If a link is provided, parse the price directly using Selenium
                    product_name, price = get_product_details(link)
                    self.finished.emit(product_name, price, "", row_position, link)
                else:
                    # Search for the product on Google, Bing, or DuckDuckGo
                    price, found_link = search_product(product_name)
                    if price:
                        self.finished.emit(product_name, price, "", row_position, found_link)
                    else:
                        self.finished.emit(product_name, 0, "Price not found", row_position, "")
            except Exception as e:
                self.finished.emit(product_name, 0, str(e), row_position, "")

            self.queue.task_done()

    def stop(self):
        """
        Stops the thread gracefully.
        """
        self.running = False
        self.condition.wakeAll()
        self.wait()  # Wait for the thread to finish


class ProductScraperApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Project Cost Calculator")
        self.setGeometry(100, 100, 800, 600)

        # Initialize project
        self.project = None

        # Queue for parsing tasks
        self.queue = Queue()
        self.mutex = QMutex()
        self.condition = QWaitCondition()

        # Worker thread
        self.worker = ParseWorker(self.queue, self.mutex, self.condition)
        self.worker.finished.connect(self.update_item)
        self.worker.start()

        # Layout
        self.layout = QVBoxLayout()

        # Project Name Input
        self.project_name_label = QLabel("Enter Project Name:")
        self.layout.addWidget(self.project_name_label)
        self.project_name_input = QLineEdit()
        self.project_name_input.setPlaceholderText("Enter project name (write once)")
        self.layout.addWidget(self.project_name_input)

        # New Project Button
        self.new_project_button = QPushButton("New Project")
        self.new_project_button.clicked.connect(self.new_project)
        self.layout.addWidget(self.new_project_button)

        # Product Link Input
        self.link_label = QLabel("Enter Product Link:")
        self.layout.addWidget(self.link_label)
        self.link_input = QLineEdit()
        self.layout.addWidget(self.link_input)

        # Product Link Search Button
        self.link_search_button = QPushButton("Search Product via Link")
        self.link_search_button.clicked.connect(self.search_product_via_link)
        self.layout.addWidget(self.link_search_button)

        # Product Name Input
        self.product_name_label = QLabel("Enter Product Name:")
        self.layout.addWidget(self.product_name_label)
        self.product_name_input = QLineEdit()
        self.layout.addWidget(self.product_name_input)

        # Product Name Search Button
        self.product_search_button = QPushButton("Search Product via Name")
        self.product_search_button.clicked.connect(self.search_product_via_name)
        self.layout.addWidget(self.product_search_button)

        # Quantity Input
        self.quantity_label = QLabel("Enter Quantity (Default: 1):")
        self.layout.addWidget(self.quantity_label)
        self.quantity_input = QLineEdit()
        self.quantity_input.setText("1")  # Default quantity
        self.layout.addWidget(self.quantity_input)

        # Add Product Button
        self.add_product_button = QPushButton("Add Product")
        self.add_product_button.clicked.connect(self.add_product)
        self.layout.addWidget(self.add_product_button)

        # Add List Button
        self.add_list_button = QPushButton("Add List from File")
        self.add_list_button.clicked.connect(self.add_list_from_file)
        self.layout.addWidget(self.add_list_button)

        # Table to display items
        self.table = QTableWidget()
        self.table.setColumnCount(6)  # Columns: Product Name, Quantity, Price, Cost, Link, Clear
        self.table.setHorizontalHeaderLabels(["Product Name", "Quantity", "Price", "Cost", "Link", ""])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.table)

        # Calculate Total Button
        self.calculate_total_button = QPushButton("Calculate Total")
        self.calculate_total_button.clicked.connect(self.calculate_total)
        self.layout.addWidget(self.calculate_total_button)

        # Export Button
        self.export_button = QPushButton("Export to Excel")
        self.export_button.clicked.connect(self.export_table)
        self.layout.addWidget(self.export_button)

        # Set Layout
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

    def closeEvent(self, event):
        """
        Handles the window close event to stop the worker thread gracefully.
        """
        self.worker.stop()
        event.accept()

    def new_project(self):
        """
        Resets the project and enables editing the project name.
        """
        self.project = None
        self.project_name_input.setDisabled(False)  # Enable project name input
        self.project_name_input.clear()  # Clear the project name field
        self.table.setRowCount(0)  # Clear the table
        QMessageBox.information(self, "New Project", "A new project has been created. You can now enter a new project name.")

    def search_product_via_link(self):
        """
        Searches for the product using the provided link and adds it to the table.
        """
        # Get project name if not already set
        if not self.project:
            project_name = self.project_name_input.text().strip()
            if not project_name:
                QMessageBox.warning(self, "Error", "Please enter a project name.")
                return
            self.project = Project(project_name)
            self.project_name_input.setDisabled(True)  # Disable project name input after setting

        link = self.link_input.text().strip()
        quantity = self.quantity_input.text().strip()

        if not link:
            QMessageBox.warning(self, "Error", "Please enter a product link.")
            return

        try:
            quantity = int(quantity) if quantity else 1  # Default quantity is 1
            if quantity <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Error", "Quantity must be a positive integer.")
            return

        # Add a loading row to the table
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        self.table.setItem(row_position, 0, QTableWidgetItem("Loading..."))
        self.table.setItem(row_position, 1, QTableWidgetItem(str(quantity)))
        self.table.setItem(row_position, 2, QTableWidgetItem(""))
        self.table.setItem(row_position, 3, QTableWidgetItem(""))
        self.table.setItem(row_position, 4, QTableWidgetItem(link))
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(lambda: self.clear_item(row_position))
        self.table.setCellWidget(row_position, 5, clear_button)

        # Add the task to the queue
        self.mutex.lock()
        self.queue.put(("", quantity, row_position, link))  # Empty product name, link provided
        self.condition.wakeAll()
        self.mutex.unlock()

    def search_product_via_name(self):
        """
        Searches for the product using the provided name and adds it to the table.
        """
        # Get project name if not already set
        if not self.project:
            project_name = self.project_name_input.text().strip()
            if not project_name:
                QMessageBox.warning(self, "Error", "Please enter a project name.")
                return
            self.project = Project(project_name)
            self.project_name_input.setDisabled(True)  # Disable project name input after setting

        product_name = self.product_name_input.text().strip()
        quantity = self.quantity_input.text().strip()

        if not product_name:
            QMessageBox.warning(self, "Error", "Please enter a product name.")
            return

        try:
            quantity = int(quantity) if quantity else 1  # Default quantity is 1
            if quantity <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Error", "Quantity must be a positive integer.")
            return

        # Add a loading row to the table
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        self.table.setItem(row_position, 0, QTableWidgetItem("Loading..."))
        self.table.setItem(row_position, 1, QTableWidgetItem(str(quantity)))
        self.table.setItem(row_position, 2, QTableWidgetItem(""))
        self.table.setItem(row_position, 3, QTableWidgetItem(""))
        self.table.setItem(row_position, 4, QTableWidgetItem(""))
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(lambda: self.clear_item(row_position))
        self.table.setCellWidget(row_position, 5, clear_button)

        # Add the task to the queue
        self.mutex.lock()
        self.queue.put((product_name, quantity, row_position, None))  # No link provided
        self.condition.wakeAll()
        self.mutex.unlock()

    def add_product(self):
        """
        Adds a product to the table using either the product name or link.
        """
        if not self.project:
            QMessageBox.warning(self, "Error", "Please create a project first.")
            return

        product_name = self.product_name_input.text().strip()
        link = self.link_input.text().strip()
        quantity = self.quantity_input.text().strip()

        if not product_name and not link:
            QMessageBox.warning(self, "Error", "Please enter either a product name or a product link.")
            return

        try:
            quantity = int(quantity) if quantity else 1  # Default quantity is 1
            if quantity <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Error", "Quantity must be a positive integer.")
            return

        # Add a loading row to the table
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        self.table.setItem(row_position, 0, QTableWidgetItem("Loading..."))
        self.table.setItem(row_position, 1, QTableWidgetItem(str(quantity)))
        self.table.setItem(row_position, 2, QTableWidgetItem(""))
        self.table.setItem(row_position, 3, QTableWidgetItem(""))
        self.table.setItem(row_position, 4, QTableWidgetItem(link if link else ""))
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(lambda: self.clear_item(row_position))
        self.table.setCellWidget(row_position, 5, clear_button)

        # Add the task to the queue
        self.mutex.lock()
        self.queue.put((product_name, quantity, row_position, link if link else None))
        self.condition.wakeAll()
        self.mutex.unlock()

    def add_list_from_file(self):
        """
        Adds a list of products from a file (CSV, Excel, or plaintext).
        """
        if not self.project:
            QMessageBox.warning(self, "Error", "Please create a project first.")
            return

        # Open file dialog
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "CSV Files (*.csv);;Excel Files (*.xlsx);;Text Files (*.txt)"
        )

        if not file_name:
            return

        try:
            if file_name.endswith(".csv"):
                df = pd.read_csv(file_name)
            elif file_name.endswith(".xlsx"):
                df = pd.read_excel(file_name)
            elif file_name.endswith(".txt"):
                with open(file_name, "r") as file:
                    product_names = file.read().splitlines()
                df = pd.DataFrame(product_names, columns=["Product Name"])
            else:
                QMessageBox.warning(self, "Error", "Unsupported file format.")
                return

            # Add each product to the queue
            for index, row in df.iterrows():
                product_name = row["Product Name"].strip()
                if not product_name:
                    continue

                # Add a loading row to the table
                row_position = self.table.rowCount()
                self.table.insertRow(row_position)
                self.table.setItem(row_position, 0, QTableWidgetItem("Loading..."))
                self.table.setItem(row_position, 1, QTableWidgetItem("1"))  # Default quantity
                self.table.setItem(row_position, 2, QTableWidgetItem(""))
                self.table.setItem(row_position, 3, QTableWidgetItem(""))
                self.table.setItem(row_position, 4, QTableWidgetItem(""))
                clear_button = QPushButton("Clear")
                clear_button.clicked.connect(lambda: self.clear_item(row_position))
                self.table.setCellWidget(row_position, 5, clear_button)

                # Add the task to the queue
                self.mutex.lock()
                self.queue.put((product_name, 1, row_position, None))  # Default quantity is 1, no link
                self.condition.wakeAll()
                self.mutex.unlock()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to read file: {e}")

    def update_item(self, product_name, price, error, row_position, link):
        """
        Updates the table row with parsed data or an error message.
        """
        if error:
            self.table.setItem(row_position, 0, QTableWidgetItem(f"{product_name} (Error: {error})"))
            self.table.item(row_position, 0).setBackground(QColor(255, 200, 200))  # Highlight row in red
        else:
            self.table.setItem(row_position, 0, QTableWidgetItem(product_name))
            self.table.setItem(row_position, 2, QTableWidgetItem(f"NPR {price:.2f}"))
            quantity = int(self.table.item(row_position, 1).text())
            cost = price * quantity
            self.table.setItem(row_position, 3, QTableWidgetItem(f"NPR {cost:.2f}"))
            self.table.setItem(row_position, 4, QTableWidgetItem(link))
            self.project.add_item(product_name, quantity, price)

    def clear_item(self, row):
        """
        Removes an item from the table and updates the project.
        """
        self.table.removeRow(row)
        if row < len(self.project.items):
            self.project.items.pop(row)

    def calculate_total(self):
        if not self.project or not self.project.items:
            QMessageBox.warning(self, "Error", "No items added.")
            return

        total_cost = self.project.get_total_cost()
        QMessageBox.information(self, "Total Cost", f"Total Cost for {self.project.name}: NPR {total_cost:.2f}")

    def export_table(self):
        """
        Exports the table data to an Excel file.
        """
        if not self.project:
            QMessageBox.warning(self, "Error", "Please create a project first.")
            return

        export_to_excel(self.table, self.project.name)