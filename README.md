# Group-7-Second-hand-Shop
The project is based on fictional paragraph:
"ReLoop sells second-hand clothes and electronics online. We want an API for products, customers and orders, and we want to import test products from a supplier's API instead of typing them in."

The project is also steered by some technical requirements that we won't list here.

## Product Goal
Group 7 second hand shop app for managing lifecycle (viewing, purchasing, receipt and statistics) of second hand clothing and electronics products. Help shop administrator to help and manages product and owner to see revenue details.

## HOW TO RUN
1. Clone the repo:<br>
```git clone https://blablab```
2. Navigate to the directory:<br>
```cd blabal```
3. Create virtual enviornment
4. Install requirements
5. Create the .env according to the structure shown in .env-example<br>
```API_KEY=your_key```
```DATABASE_PATH=your_path```
6. Seed the database
7. Start FastAPI dev

## API Endpoints

## Personal data
Even though the store is fictional, in structuring the project we have tried to comply with GDPR principles of data minimization, the system only stores essential customer data required for order processing:

Stored Personal Data:<br>
The name of the customer, used for customer identification and receipts.<br>
The email of the customer, required for order confirmations and communication.<br>
The phone number of the customer, used for order notifications and customer service.<br>
The city of the customer, used for regional tracking and logistics.<br>

Excluded Data (Privacy by Design):<br>
We do not store full street addresses, personal identity numbers, or payment/credit card details in the database to minimize security risks and protect user privacy.

To comply with GDPR's 'right to be forgotten', we have written a function that will delete or pseudonymize customers that requests this. The pseudonymization is used when a customer requests deletion but has an order newer than 7 years, this is to comply with the bokföringslag/BFL (1999:1078).<br>
To comply with GDPR's 'right of access', we have created an endpoint that will, if authorized, show all the information stored about a singular customer.

By design most stored data should not be retrievable by unauthorized actors, confirmed by an api key. And access to personal customer data is authorized for the very few.

## ER Diagram
<img width="1036" height="637" alt="image" src="https://github.com/user-attachments/assets/c3ee89e6-a47a-4ba7-996f-02a17eef3aeb" />


## Project & Team Process
This is a group project for the educational programme called "Python AI & ML system developer" provided by Lexicon. The project is an exercise in combining what has been included in the education so far. In the project we utilize tools such as python programming, SQL, API's. An important requirement to this project was to run it according to the praxis of Scrum and the doxa of Agile development philosophy. This forces the group to work 'slow and steady' and take strategic choices from start, every single day and within every sprint while at the same time reevaluate often. <br> While the team, a gang of four, mainly took decisions out of respect to the socratic method and consensus, some roles were required for the project to be in line with the praxis of scrum. For the first sprint, the product owner was Saranya and the scrum master was Alve. As of the second sprint, we switched up our roles and had Jakob as product owner and Yetnayet as scrum master.

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

- 3 categories
- 5 products
- 4 customers
- 4 orders
- 5 order items

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
