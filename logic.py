class Project:
    def __init__(self, name):
        self.name = name
        self.items = []
        self.total_cost = 0

    def add_item(self, product_name, quantity, price):
        """
        Adds an item to the project and updates the total cost.
        """
        item_cost = price * quantity
        self.items.append((product_name, quantity, price, item_cost))
        self.total_cost += item_cost

    def get_summary(self):
        """
        Returns a summary of the project as a string.
        """
        summary = f"Project: {self.name}\n"
        summary += "Items:\n"
        for item in self.items:
            summary += f"- {item[0]} (Qty: {item[1]}, Price: NPR {item[2]:.2f}, Cost: NPR {item[3]:.2f})\n"
        summary += f"\nTotal Cost: NPR {self.total_cost:.2f}"
        return summary