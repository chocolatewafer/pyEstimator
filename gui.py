import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QWidget, QMessageBox
)
from logic import Project
from selenium_scraper import get_product_details


class ProductScraperApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Project Cost Calculator")
        self.setGeometry(100, 100, 500, 400)

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

        # Display Items
        self.items_display = QTextEdit()
        self.items_display.setReadOnly(True)
        self.layout.addWidget(self.items_display)

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

        # Parse product details
        try:
            product_name, price = get_product_details(link)
            if not product_name or price is None:
                raise ValueError("Could not parse product details.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to parse product details: {e}")
            return

        # Add item to project
        self.project.add_item(product_name, quantity, price)

        # Update display
        self.items_display.setText(self.project.get_summary())

        # Clear inputs
        self.link_input.clear()
        self.quantity_input.clear()

    def calculate_total(self):
        if not self.project or not self.project.items:
            QMessageBox.warning(self, "Error", "No items added.")
            return

        QMessageBox.information(self, "Total Cost", f"Total Cost for {self.project.name}: NPR {self.project.total_cost:.2f}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProductScraperApp()
    window.show()
    sys.exit(app.exec())