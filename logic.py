class Project:
    def __init__(self, name):
        self.name = name
        self.items = []

    def add_item(self, product_name, quantity, price):
        """
        Adds an item to the project and updates the total cost.
        """
        item_cost = price * quantity
        self.items.append((product_name, quantity, price, item_cost))

    def get_total_cost(self):
        """
        Returns the total cost of all items in the project.
        """
        return sum(item[3] for item in self.items)