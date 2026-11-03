one note per person, per Daily Scrum

• What did I finish yesterday?
• What will I do today?
• Is anything blocking me?

Long discussions happen after the meeting, with the people who need them. The Daily Scrum
is for the team, not a status report to the teacher. The Scrum Master writes a short note in
docs/daily.md: the date and one line per person.

**DAY 1**

Alve:
Written import script and save to DB. Updated user story, it should not be import script as this is already done by Jakob. Added /docs and files in /docs, added note structures to the files in docs.

Saranya: 
Have written script for creating local DB.

Jakob: 
Import from products #13 finished, need review. Started a new issue: "View products" #3, close to done.

Yetnayet: 
Managing customer task, validation and routes. 
Questions: should we add functionality to update products or manually add/delete etc.

**DAY 2**

Alve: Reworking on export to DB. blockage cause of confusion surrounding git/hub workflow. removed import code as this already finished by Jakob.

Saranya: 
DB finished looking for adding details, doing code review. REST api endpoints for add/update/del.

Jakob: 
Working on REST api for products. GET products and GET products by ID. Looking through documentation to confirm direction of work.

Yetnayet: Worked on the Manage Customers feature. Added validation for customer details, such as requiring a name and a valid email address. Wrote database functions to save, retrieve, update, and delete customer records, and connected them to four API endpoints.
Today I will test these operations locally and check that the customer fields match our shared database schema today.

**DAY 3**
Yetnayet: Testing customer API, discussed code review. Will follow up on code reviews.

Jakob: Have been testing Yetnayet's code. Suggests to end sprint today and plan next one.

Saranya: Worked on product CRUD. REST API and endpoints. Did reviews and responded to reviews.

Alve: Spent yesterday with code review, worked a bit on export to DB code, and learned to better navigate the git/hub complex. 

Today we chose to rework the DB schema: EXPLAIN LOGICS BEHIND. Alve reworks his code to fit this. We plan to merge and finish the sprint later today.

**DAY 4**
Saranya: testing locally, issues with alves code in PR running in client
together with alve and jakob to use same connection to database DATABASE_PATH

Alve: updated the code for export to db, code reveiw, updated some textual stuff, 

Jakob: added category name to products in the rest api, merged, did reviews.

Yetnayet: seed.py and client database rest options. 

Today: discussing stuctural changes: is the fundamentals correct so we can move on and fix the minor functions? We are going to do another meeting after lunch.

**Day 5** 
Jakob: Work on order receipts and write user stories for splitting the menu program.

Alve: Start code review #19 and continue working on his user story #11.

Saranya: Review the PR and continue working on statistics, especially products that have never been sold.

Yetnayet: Address review feedback on task #19, test the category changes,

**DAY 6** 
Jakob: Created a pull request for order receipts, added receipt tests, and joined three database tables using SQL. And plan/offer to start work on new user story.

Alve: Finished PR #30 and started working on a user story from the Ready section. Wants to take enough time to implement it correctly.

Yetnayet: Working on the Place Order user story and plans to finish it today.

Saranya: Plans to merge the pull request for products that have never been sold. Continuing with revenue calculations and expects to finish today.

Today Discussion: Four user stories were still remaining. We discussed how to distribute them and agreed that each team member would take one story. The team aims to finish the remaining work by Wednesday afternoon.
