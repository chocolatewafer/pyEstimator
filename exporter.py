import pandas as pd
from PySide6.QtWidgets import QFileDialog, QMessageBox


def export_to_excel(table, project_name):
    """
    Exports the table data to an Excel file, including the total cost.
    """
    if not project_name:
        QMessageBox.warning(None, "Error", "Please enter a project name.")
        return

    # Get data from the table
    data = []
    total_cost = 0
    for row in range(table.rowCount()):
        row_data = []
        for col in range(table.columnCount() - 1):  # Skip the "Clear" column
            item = table.item(row, col)
            if item:
                row_data.append(item.text())
            else:
                row_data.append("")
        data.append(row_data)
        # Calculate total cost
        cost_item = table.item(row, 3)
        if cost_item and cost_item.text().startswith("NPR"):
            try:
                cost = float(cost_item.text().replace("NPR", "").strip())
                total_cost += cost
            except ValueError:
                pass

    # Create a DataFrame
    df = pd.DataFrame(data, columns=["Product Name", "Quantity", "Price", "Cost", "Link"])

    # Add a row for the total cost
    total_row = ["Total", "", "", f"NPR {total_cost:.2f}", ""]
    df.loc[len(df)] = total_row

    # Save the DataFrame to an Excel file
    file_name, _ = QFileDialog.getSaveFileName(
        None, "Save Excel File", f"{project_name}.xlsx", "Excel Files (*.xlsx)"
    )

    if file_name:
        try:
            df.to_excel(file_name, index=False)
            QMessageBox.information(None, "Success", f"Table exported to {file_name}")
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to export table: {e}")