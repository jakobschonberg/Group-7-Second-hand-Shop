# ReLoop second-hand store
This project is based on a fictional world built from just a sentence:
"ReLoop sells second-hand clothes and electronics online. We want an API for products, customers and orders, and we want to import test products from a supplier's API instead of typing them in."

The project is also steered by some technical requirements that we won't list here.

We? Who? The *we* behind this project consists of a small group of students attending the educational program 'Python AI/ML developer'. More about this under the Project & Team process header.

## Product Goal
Group 7 second hand shop app for managing lifecycle (viewing, purchasing, receipt and statistics) of second hand clothing and electronics products. Help shop administrator to help and manages product and owner to see revenue details.

## HOW TO RUN
Prerequisites
Make sure you have Python installed on your system.

1. Clone the repository:<br>
```git clone https://github.com/jakobschonberg/Group-7-Second-hand-Shop.git```
2. Navigate to the directory
```cd Group-7-Second-hand-Shop```
4. Create virtual environment (recommended)
```python -m venv .venv``` 
5. Install requirements
```pip install -r requirements.txt```
6. Create the .env according to the structure shown in .env-example<br>
```API_KEY=your_key```
```DATABASE_PATH=your_path```
```REST_API_URL=your_path```
8. Seed the database
```python client.py``` (option 3 and type "yes")
9. Start FastAPI and run client
```uvicorn main:app --reload``` or ```fastapi dev main.py```

## API Endpoints

Start the API and open `http://127.0.0.1:8000/docs` to try the endpoints and see the request fields.
For endpoints that require an API key, send your `.env` `API_KEY` value in the `X-API-Key` header.

| Method | Endpoint | What it does | API key required |
| --- | --- | --- | --- |
| GET | `/products` | List, search, filter and sort products | No |
| GET | `/products/{product_id}` | Show one product | No |
| POST | `/products` | Create a product | Yes |
| PATCH | `/products/{product_id}` | Update product details | Yes |
| DELETE | `/products/{product_id}` | Delete a product if it has no related order items | Yes |
| POST | `/categories` | Create a category or return an existing one with the same name | Yes |
| GET | `/customers` | List customers | Yes |
| POST | `/customers` | Create a customer | Yes |
| PUT | `/customers/{customer_id}` | Update customer details | Yes |
| DELETE | `/customers/{customer_id}` | Delete or pseudonymize a customer depending on their orders | Yes |
| GET | `/customers/{customer_id}/data` | Export a customer's details and orders | Yes |
| GET | `/orders` | List orders, optionally filtered by `customer_id` | Yes |
| GET | `/orders/{order_id}` | Show one order and its items | Yes |
| POST | `/orders` | Place an order and decrease stock | Yes |
| PATCH | `/orders/{order_id}` | Update only the order status | Yes |
| GET | `/orders/{order_id}/receipt` | Show the order receipt | Yes |
| GET | `/reports/revenue` | Show revenue by category, excluding cancelled orders | Yes |

`GET /products` accepts these optional query parameters: `name`, `category`,
`minimum_price`, `maximum_price`, `in_stock`, `sort_by`, `order`, `limit` and `offset`.
For example: `/products?category=electronics&in_stock=true`.


## ER Diagram
<img width="1036" height="637" alt="image" src="https://github.com/user-attachments/assets/c3ee89e6-a47a-4ba7-996f-02a17eef3aeb" />

## Personal data
Even though the store is fictional, in structuring the project we have tried to comply with GDPR principles of data minimization, the system only stores essential customer data required for order processing:

Stored Personal Data:<br>
The name of the customer, used for customer identification and receipts.<br>
The email of the customer, required for order confirmations and communication.<br>
The phone number of the customer, used for order notifications and customer service.<br>
The city of the customer, used for regional tracking and logistics.<br>

Excluded Data (Privacy by Design):<br>
We do not store full street addresses, personal identity numbers, or payment/credit card details in the database to minimize security risks and protect user privacy.

How GDPR requests are handled:<br>
Because these administrative endpoints (deletion and data export) are protected by an X-Api-Key, they are designed to be used by store administrators or support staff on behalf of the customer, rather than as unprotected self-service endpoints. This prevents unauthorized exposure of personal data.

Edge Case Handling (Mixed Orders):<br>
In scenarios where a customer requests deletion and has a mix of orders—some older than 7 years and some newer—the system applies a hybrid approach to balance GDPR and BFL:

The expired orders (older than 7 years) are permanently deleted to respect data minimization.
The customer profile and any active orders (newer than 7 years) are pseudonymized rather than deleted, keeping the accounting records intact while stripping away the physical identity.

In a real-world scenario, a script should be scheduled to run ever so often to check if there are orders older than 7 years, and automatically delete them, as well as saved customer data for customers lacking newer orders. 

## Project & Team Process
To repeat ourselves: This is a group project by students attending the education "Python AI & ML system developer" provided by Lexicon. The project is an exercise in combining what has been included in the education so far. In the project we utilize tools such as python programming, SQL, API's. An important requirement to this project was to run it according to the praxis of Scrum and the doxa of Agile. This forces the group to work 'slow and steady' and take strategic choices from start, every single day and within every sprint while at the same time reevaluate often. <br> While the team, consisting of just four stundents, mainly took decisions out of respect to the socratic method and group consensus, some roles were required for the project to be in line with the praxis of scrum. For the first sprint, the product owner was Saranya and the scrum master was Alve. As of the second sprint, we switched up our roles and had Jakob as product owner and Yetnayet as scrum master.

## Create or reset test data

We use `seed.py` to fill the database with test data so we can try out our features.
It uses the tables from `db_schema.sql`.

To run it:

1. Install the packages from `requirements.txt` in your virtual environment.
2. Set `DATABASE_PATH=shop.db` in the project's `.env` file.
3. Open a terminal in the project folder and run `python client.py`.
4. Choose **3**, then type **yes** to reset the database with test data.
   Any other answer cancels the reset and returns to the menu.

This removes the existing data in the five shop tables, so only use it on a test database.
Run the API from the same folder with the same database setting so it can see this data.
Do not push your `.env` or database files to GitHub.

The test data includes:

- 4 categories
- 6 products
- 4 customers
- 8 orders
- 10 order items

We included examples like a product with no stock, a product with a price of zero,
and a customer with no phone number or city. There are also orders with different
statuses and an order with more than one product. Alex has only an old order,
dated `2018-01-01`, so we can test a customer whose orders are older than seven years.

You can choose **3** again to start over with the same test data. It works without
internet access. If something fails during the reset, the changes are undone
and the previous data is kept.

Category names are required. Names such as `Electronics` and `electronics`
count as the same category. This schema change applies to newly created or
reset databases; existing databases are not changed automatically. Reset only
a test database, because resetting removes its existing shop data.
