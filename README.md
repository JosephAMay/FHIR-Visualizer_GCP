# FHIR-Visualizer_GCP
Web App using GCP to display FHIR data with some role privelages enforced

# Setting up Google Cloud
This project uses GCP Big Query to host the FHIR data, and query it for visualization. 
This requires the user to have an active GCP account, with billing enabled, and other required settings such as enabled APIs, and relevan IAM permissions to access the data. 

1. Use this tutorial to learn how to get FHIR data from a GCP bucket, store it in a FHIR datastore, and connect the datastore to BigQuery: https://www.cloudskillsboost.google/focuses/6104?parent=catalog These were the steps used to initialize the FHIR data for the project as well.
2. Install the Cloud SDK, and initialize.
   Navigate to this website: https://cloud.google.com/sdk/docs/install
   Download the SDK for your OS.
3. Navigate to this website:
  https://cloud.google.com/docs/authentication/provide-credentials-adc
  Select Local development environment from the "How to provide credentials to the ADC."
  Follow the instructions to connect your cloud SDK to the correct project, and to the BigQuery / Healthcare API resources.



# Steps to run:
1. In the SQL folder, open and run the Create_populate_tables.sql. This creates the tables used to authenticate user logins, and populates it with some dummy data. Add in custom credentials if desired.
2. Open the application.py file, and adjust the database connection details of the mysql connector to match with your host,user, and password.
3. If necessarry, connect to the Google Cloud and setup default credentials to ensure the BigQuery connection is valid (see Setting up Google Cloud section for some relevant links).
4. In the directory housing application.py, use the command python application.py.
   This will start the server. Any errors will be the result of faulty database connections and will require credential troubleshooting.
   On successful startup, this will begin the server on the localhost at port 5000.
   Navigate to localhost:5000.
5. Observe the homepage. It has a brief intro to FHIR data, and the purpose of the website. Buttons to the login page may be found there.
6. Click the login button.
7. Login with desired credentials from step 1, successful credentials will automatically forwward you to the visualization page. Invalid credentials will leave you stuck on the login page
8. Select any of the supported query type pages by expanding the menu in the top left of the website.
9. Use the form to select a desired query
10. Select chart type
11. Click submit, and see the chart appear on the website and be avaiable for download
12. If logged in as an admin, Try adding a query and seeing the results!
