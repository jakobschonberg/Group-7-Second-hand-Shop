# Place an order

The order routes use the existing database and API key setup.

- GET `/orders` lists orders. Use `/orders?customer_id=1` to filter them.
- GET `/orders/1` shows one order and its items.
- POST `/orders` creates an order and reduces stock.
- PATCH `/orders/1` changes only the status.

POST and PATCH require the `X-API-Key` header. Payment is not included,
as agreed by the team. Product prices come from the database and are saved
in order_items so later price changes do not change old orders.

Example POST body:

```json
{
  "customer_id": 1,
  "items": [
    {"product_id": 1, "quantity": 2},
    {"product_id": 3, "quantity": 1}
  ]
}
```

New orders have status NEW. Repeated product IDs are combined into one item.
If a customer or product does not exist, the API returns 404. Not enough stock
returns 409. Invalid input returns 422. Failed orders do not save any order
items or stock changes. A database write lock keeps simultaneous orders from
buying the same last item.

Example PATCH body:

```json
{"status": "DELIVERED"}
```

The implemented status rules for team review are:
- NEW can change to DELIVERED or CANCELLED.
- Cancelling a NEW order restores its stock.
- Sending the same status again does nothing, so stock is not restored twice.
- DELIVERED and CANCELLED orders cannot change to a different status.

## Try it locally

Use a test database, not a database containing data you need to keep.
From this project folder, activate your virtual environment and run:

```bash
export DATABASE_PATH="$PWD/order_test.db"
export API_KEY="local-test-key"
python client.py
```

Choose 3 and confirm with yes to create test data, then choose 1 to quit.
Run `python -m uvicorn main:app --reload` and open
`http://127.0.0.1:8000/docs`. Try the POST example above using the API key,
then GET the returned order ID and check the reduced product stock.
Try ordering product 2 (zero stock) to see the error.

## Automated tests

With project requirements installed, also install the test dependency:

```bash
python -m pip install httpx
python -m unittest discover -s tests -v
```

Tests use temporary databases and simulated supplier responses. They cover
single and multiple products, validation, API keys, saved prices, rollback,
status updates, filtering and simultaneous orders competing for one item.
