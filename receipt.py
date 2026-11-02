from datetime import datetime
from decimal import Decimal
from json import dumps

class Receipt_row:
    def __init__(self, product_name: str, quantity: int, row_price: Decimal):
        self.product_name = product_name
        self.quantity = quantity
        self.row_price = row_price

class Receipt:
    def __init__(self, date: datetime, order_id: int, rows: list[Receipt_row]):
        self.date = date
        self.order_id = order_id
        self.rows = rows
        self.total_price = 0

    def add_row(self, row: Receipt_row):
        if isinstance(row, Receipt_row):
            self.rows.append(row)
            self.total_price += row.row_price
