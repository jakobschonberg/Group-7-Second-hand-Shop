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