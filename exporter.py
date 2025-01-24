import pandas as pd
from PySide6.QtWidgets import QFileDialog, QMessageBox


def export_to_excel(table, project_name):
    """
    Exports the table data to an Excel file.
    """
    if not project_name:
        QMessageBox.warning(None, "Error", "Please enter a project name.")
        return

    # Get data from the table
    data = []
    for row in range(table.rowCount()):
        row_data = []
        for col in range(table.columnCount() - 1):  # Skip the "Clear" column
            item = table.item(row, col)
            if item:
                row_data.append(item.text())
            else:
                row_data.append("")
        data.append(row_data)

    # Create a DataFrame
    df = pd.DataFrame(data, columns=["Product Name", "Quantity", "Price", "Cost"])

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