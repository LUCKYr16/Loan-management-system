# Loan-management-system

An API which facilitates the working of a minimal loan management system

## Theme of the API

1. There are three types of users:- Customer, Agent, Admin
2. Customer is the client who makes a request for the loan
3. Agent is the middleman associated with the bank who has certain authourities such as edit loans,
listing users, and making loan request on behalf of customer
4. Before accessing to these functions an agent has to get the approval by the admin of being an agent
5. Admin is the highest authority who can approve or reject a loan and also the request by agent
6. Customers and agents can Sign up
7. Admin, cutomers and agents can login(agent can login only if agent is approved by the admin)
8. When an agent will signup a request will be sent to the admin for approval
9. A loan has entities such as principle, interest rate, months to repay, emi and status
10. The value of interest rate would depend on the value of principle
11. The loan can have 3 kinds of status: Approved, New or Rejected


## Important features
   
. Only customers and agents can signup
. Customer will be created in the database on signup
. When agent would signup a request would to the the admin to approve the agent.
. Admin and customer are by default approved but not agent
. Agent can only login after being approved
. An instance of admin is created initially in the database(username = admin, password = admin)
. All the users can update their passwords and its length should be greater than 6
. Agents can list all customers and admin can list all users
. The interest on a loan would depend on the principle
. Loan can be approved or rejected by admin only
. Only agent can edit a loan if it is still not approved
. Previous instance of the same loan is pushed inside the history before being edited
. Loans can be listed according to filter


## Technology used
 Python, Django, REST API, Rest framework, Postgresql


 ## Commands to run project
 1. Clone the project repo
 2. Go to project
 3. Run the command 'docker-compose up' ont he terminal
 4. All the test cases will run
 5. You can log in to admin using username=admin, password=admin

