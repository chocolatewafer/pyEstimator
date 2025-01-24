import sys
import requests
from bs4 import BeautifulSoup
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QWidget, QMessageBox
)

class ProjectCostCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Project Cost Calculator")
        self.setGeometry(100, 100, 500, 400)

        # Main widget and layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout()

        # Project name input
        self.project_name_label = QLabel("Enter Project Name:")
        self.layout.addWidget(self.project_name_label)
        self.project_name_input = QLineEdit()
        self.layout.addWidget(self.project_name_input)

        # Item link input
        self.item_link_label = QLabel("Enter Item Link:")
        self.layout.addWidget(self.item_link_label)
        self.item_link_input = QLineEdit()
        self.layout.addWidget(self.item_link_input)

        # Quantity input
        self.quantity_label = QLabel("Enter Quantity:")
        self.layout.addWidget(self.quantity_label)
        self.quantity_input = QLineEdit()
        self.layout.addWidget(self.quantity_input)

        # Add item button
        self.add_item_button = QPushButton("Add Item")
        self.add_item_button.clicked.connect(self.add_item)
        self.layout.addWidget(self.add_item_button)

        # Display area for items and total cost
        self.display_area = QTextEdit()
        self.display_area.setReadOnly(True)
        self.layout.addWidget(self.display_area)

        # Total cost label
        self.total_cost_label = QLabel("Total Cost: NRS 0")
        self.layout.addWidget(self.total_cost_label)

        # Finish button
        self.finish_button = QPushButton("Finish Project")
        self.finish_button.clicked.connect(self.finish_project)
        self.layout.addWidget(self.finish_button)

        # Initialize variables
        self.project_name = ""
        self.items = []
        self.total_cost = 0

        # Set layout
        self.main_widget.setLayout(self.layout)

    def parse_item_details(self, link):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(link, headers=headers)
            soup = BeautifulSoup(response.content, "html.parser")

            # Parse item name
            item_name = soup.find("span", {"class": "pdp-mod-product-badge-title"}).text.strip()

            # Parse item price
            item_price = soup.find("span", {"class": "pdp-price_type_normal"}).text.strip()
            item_price = float(item_price.replace("NRS", "").replace(",", "").strip())

            return item_name, item_price
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to parse item details: {e}")
            return None, None

    def add_item(self):
        link = self.item_link_input.text().strip()
        quantity = self.quantity_input.text().strip()

        if not link or not quantity:
            QMessageBox.warning(self, "Input Error", "Please provide both link and quantity.")
            return

        try:
            quantity = int(quantity)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Quantity must be a number.")
            return

        item_name, item_price = self.parse_item_details(link)
        if item_name and item_price:
            total_item_cost = item_price * quantity
            self.items.append((item_name, item_price, quantity, total_item_cost))
            self.total_cost += total_item_cost

            # Update display
            self.display_area.append(
                f"Item: {item_name}\nPrice: NRS {item_price}\nQuantity: {quantity}\nTotal: NRS {total_item_cost}\n"
            )
            self.total_cost_label.setText(f"Total Cost: NRS {self.total_cost}")

            # Clear inputs
            self.item_link_input.clear()
            self.quantity_input.clear()
        else:
            QMessageBox.warning(self, "Error", "Could not retrieve item details.")

    def finish_project(self):
        self.project_name = self.project_name_input.text().strip()
        if not self.project_name:
            QMessageBox.warning(self, "Input Error", "Please provide a project name.")
            return

        if not self.items:
            QMessageBox.warning(self, "Input Error", "No items added to the project.")
            return

        # Display final summary
        summary = f"Project Name: {self.project_name}\n\n"
        for item in self.items:
            summary += (
                f"Item: {item[0]}\nPrice: NRS {item[1]}\nQuantity: {item[2]}\nTotal: NRS {item[3]}\n\n"
            )
        summary += f"Total Project Cost: NRS {self.total_cost}"

        QMessageBox.information(self, "Project Summary", summary)

        # Reset for new project
        self.project_name_input.clear()
        self.item_link_input.clear()
        self.quantity_input.clear()
        self.display_area.clear()
        self.total_cost_label.setText("Total Cost: NRS 0")
        self.items = []
        self.total_cost = 0


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProjectCostCalculator()
    window.show()
    sys.exit(app.exec())