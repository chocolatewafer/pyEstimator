from PySide6.QtWidgets import (
    QMainWindow, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QWidget, QMessageBox
)
from PySide6.QtCore import Qt, QThread, Signal
from logic import Project
from selenium_scraper import get_product_details


class ParseWorker(QThread):
    """
    Worker thread for parsing product details.
    """
    finished = Signal(str, float, str)  # Emits product_name, price, error_message

    def __init__(self, link):
        super().__init__()
        self.link = link

    def run(self):
        try:
            product_name, price = get_product_details(self.link)
            self.finished.emit(product_name, price, "")
        except Exception as e:
            self.finished.emit("", 0, str(e))


class ProductScraperApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Project Cost Calculator")
        self.setGeometry(100, 100, 800, 600)

        # Initialize project
        self.project = None

        # Layout
        self.layout = QVBoxLayout()

        # Project Name Input
        self.project_name_label = QLabel("Enter Project Name:")
        self.layout.addWidget(self.project_name_label)
        self.project_name_input = QLineEdit()
        self.layout.addWidget(self.project_name_input)

        # Link Input
        self.link_label = QLabel("Enter Product Link:")
        self.layout.addWidget(self.link_label)
        self.link_input = QLineEdit()
        self.layout.addWidget(self.link_input)

        # Quantity Input
        self.quantity_label = QLabel("Enter Quantity:")
        self.layout.addWidget(self.quantity_label)
        self.quantity_input = QLineEdit()
        self.layout.addWidget(self.quantity_input)

        # Add Item Button
        self.add_item_button = QPushButton("Add Item")
        self.add_item_button.clicked.connect(self.add_item)
        self.layout.addWidget(self.add_item_button)

        # Table to display items
        self.table = QTableWidget()
        self.table.setColumnCount(5)  # Columns: Product Name, Quantity, Price, Cost, Clear
        self.table.setHorizontalHeaderLabels(["Product Name", "Quantity", "Price", "Cost", ""])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.table)

        # Calculate Total Button
        self.calculate_total_button = QPushButton("Calculate Total")
        self.calculate_total_button.clicked.connect(self.calculate_total)
        self.layout.addWidget(self.calculate_total_button)

        # Set Layout
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

    def add_item(self):
        # Get project name if not already set
        if not self.project:
            project_name = self.project_name_input.text().strip()
            if not project_name:
                QMessageBox.warning(self, "Error", "Please enter a project name.")
                return
            self.project = Project(project_name)

        # Get link and quantity
        link = self.link_input.text().strip()
        quantity = self.quantity_input.text().strip()

        if not link or not quantity:
            QMessageBox.warning(self, "Error", "Please enter both link and quantity.")
            return

        try:
            quantity = int(quantity)
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
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(lambda: self.clear_item(row_position))
        self.table.setCellWidget(row_position, 4, clear_button)

        # Start the parsing thread
        self.worker = ParseWorker(link)
        self.worker.finished.connect(lambda name, price, error: self.update_item(row_position, name, price, error, quantity))
        self.worker.start()

    def update_item(self, row, product_name, price, error, quantity):
        """
        Updates the table row with parsed data or an error message.
        """
        if error:
            self.table.setItem(row, 0, QTableWidgetItem(f"Error: {error}"))
        else:
            self.table.setItem(row, 0, QTableWidgetItem(product_name))
            self.table.setItem(row, 2, QTableWidgetItem(f"NPR {price:.2f}"))
            cost = price * quantity
            self.table.setItem(row, 3, QTableWidgetItem(f"NPR {cost:.2f}"))
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