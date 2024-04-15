#Imports
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file,jsonify
import mysql.connector
import os
from werkzeug.utils import secure_filename
import csv
import sys
import time  
import random
from google.cloud import bigquery
import matplotlib.pyplot as plt
from collections import Counter
import datetime
from functools import wraps
#Add folder housing the project to the filepath
bigfolder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(bigfolder_path)



#App settings 
MAX_CLIENTS = 100
OVER_CAPACITY=False
PROJECT_ID = "fhir-visualization-project"
DATASET_ID = "dataset1"
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = 'SoftwareProject'
app.config['SESSION_COOKIE_NAME'] = 'user_session'

#Possible client connections
available_sockets = list(range(1, MAX_CLIENTS+1))
clients = []


bqClient = bigquery.Client(project='fhir-visualization-project')
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Mandarin143!",
    database="visualization"
)

        
def check_credentials(username, password,tablename):
    cursor = db.cursor()
    if tablename == 'worker':
        query = "SELECT * FROM worker WHERE username=%s AND password=%s"
    elif tablename == 'user':
        query = "SELECT * FROM user WHERE username=%s AND password=%s"
    else:
        print('TableName Not specified')
        return None
    
    cursor.execute(query, (username, password))
    result = cursor.fetchone()
    return result

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))


# Define a decorator function to check if the user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if 'username' key exists in the session
        if 'username' not in session:
            # If user is not logged in, redirect to the login page
            return redirect(url_for('login'))
        # If user is logged in, proceed with the original function
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    global OVER_CAPACITY
    if (OVER_CAPACITY):
        return render_template('about.html', full = True)

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = check_credentials(username, password, 'user')
        worker = check_credentials(username, password, 'worker')
        if worker is not None:
            session['username'] = username
            session['role'] = 'admin'
            return redirect(url_for('vizHomepage'))
        elif user is not None:
            session['username'] = username
            session['role'] = 'user'
            return redirect(url_for('vizHomepage'))
        
    return render_template('login.html')

#Page showing options for Visualization
@app.route('/FHIR-Visualization', methods=['GET', 'POST'])
@login_required
def vizHomepage():
    global OVER_CAPACITY
    #IF website at max client capacity, send to wait area
    if(OVER_CAPACITY):
        return render_template('about.html', full = True)
    
    #if user is logged in take their file
    if 'username' in session:
        username = session['username']
        role = session['role']
    return render_template('fhir_vizualizer.html', username=username, role=role)
    #return render_template('about.html')

#home page
@app.route('/')
def about():
    global OVER_CAPACITY
    
    #If full let client know to wait a bit
    if(OVER_CAPACITY):
        return render_template('about.html', full = True)
    
    if(not OVER_CAPACITY):
        return render_template('about.html')

#Pages for each individual query option
@app.route('/patient', methods=['GET', 'POST'])
@login_required
def patient():
    return render_template('patient.html', username=session['username'],role=session['role'])

@app.route('/practitioner', methods=['GET', 'POST'])
@login_required
def practitioner():
    return render_template('practitioner.html', username=session['username'],role=session['role'])

@app.route('/claim', methods=['GET', 'POST'])
@login_required
def claim():
    return render_template('claim.html', username=session['username'],role=session['role'])

@app.route('/medRequest', methods=['GET', 'POST'])
@login_required
def medrequest():
    return render_template('medRequest.html', username=session['username'],role=session['role'])

@app.route('/procedure', methods=['GET', 'POST'])
@login_required
def procedure():
    return render_template('procedure.html', username=session['username'],role=session['role'])

@app.route('/process_form', methods=['POST'])
def process_form():
    
    #Grab data sent from webpage
    data = request.get_json()
    
    #Get domain, query & chart Type
    domain = data.get('domain', None)
    uniqueDom = set(domain)
    values = data.get('checkedValues',[])
    print(data)
    adminData = data.get('adminData',{})
    adminQuery = adminData.get('query','')
    adminGraphyType = adminData.get('graphType','')
    if adminQuery:
        adminData = [adminQuery,adminGraphyType]
    else:
        adminData = None
    
    #Send to chart Making code
    results,numGraphs = visualizeData(uniqueDom,values,adminData)
    
    #Send back data
    return jsonify({'result': results, 'numGraphs': numGraphs})

#Based on queries, domain, and chart type asked for, graph results and send back to webpage
def visualizeData(domains,values,adminData):

    POSSIBLE_DOMAINS = {'Patient','Procedure','Practitioner','MedicationRequest','Condition','Claim'}
    #Grab GCP daatsetID and project ID to use for queries
    global DATASET_ID
    global PROJECT_ID

    queryResults = [] #Hold query results to pass into chart code
    #print('Domain =', type(domains),"\t",domains,'\t',values)
    
    returnedData = []
    numGraphs = 0

    uniqueDom = domains.intersection(POSSIBLE_DOMAINS)
    #print('Unsupported domains in request: ', domains - POSSIBLE_DOMAINS)

    #Route to query based on domain
    for domain in uniqueDom:
    
        #set table id, which should match with domain name
        table_id = domain
        table_ref = f"{PROJECT_ID}.{DATASET_ID}.{table_id}"
        #print('ChartVisualizer table refrence is:',table_ref)

        #Match with domain, Loop through different query options associated with domain
        #For any query option slected, execute query, connect query results with desired 
        #Chart type to be charted and sent back to webpage. 
        if domain == 'Patient':
            for item in values:
                qran = True
                if item['query'] == 'birthdate':
                    query = f"select birthDate from {table_ref} LIMIT 1000;"
                elif item['query'] == 'gender':
                    query = f"SELECT us_core_birthsex.value.code FROM {table_ref} LIMIT 1000;"
                elif item['query'] == 'ethnicity':
                    query = f"select us_core_ethnicity.text.value from {table_ref} LIMIT 1000;"
                elif item['query'] == 'birthPlace':
                    query = f"select patient_birthPlace.value.address from {table_ref} LIMIT 1000;"
                else:
                    qran=False
                if(qran):
                    query_job = bqClient.query(query)
                    results = query_job.result()
                    queryResults.append([results, item['graphType']])

        elif domain == 'Procedure':
            for item in values:
                qran = True
                if item['query'] == 'type':
                    query = f"select code.text from {table_ref};"
                elif item['query'] == 'performed':
                    query = f"select performed.dateTime, performed.period.start, performed.period.end  from {table_ref};"
                elif item['query'] == 'patient':
                    query = f"select subject.patientId from  {table_ref};"
                else:
                    qran=False
                if(qran):
                    query_job = bqClient.query(query)
                    results = query_job.result()
                    queryResults.append([results, item['graphType']])

        elif domain == 'Practitioner':
            for item in values:
                qran = True
                if item['query'] == 'gender':
                    query = f"select gender from {table_ref} limit 1000;"
                elif item['query'] == 'address':
                    query = f"select a.city, a.postalCode, a.state from {table_ref}, unnest(address) as a limit 1000;"
                
                else:
                    qran=False
                if(qran):
                    query_job = bqClient.query(query)
                    results = query_job.result()
                    queryResults.append([results, item['graphType']])

        elif domain == 'MedicationRequest':
            for item in values:
                qran = True
                if item['query'] == 'orderer':
                    query = f"select requester.display from  {table_ref} LIMIT 1000;"
                elif item['query'] == 'patient':
                    query = f" select subject.patientId from {table_ref} LIMIT 1000;"
                elif item['query'] == 'medType':
                    query = f"select medication.codeableConcept.text from {table_ref} LIMIT 1000;"
                elif item['query'] == 'status':
                    query = f"select status from {table_ref} LIMIT 1000;"
                elif item['query'] == 'time':
                    query = f"SELECT authoredOn FROM {table_ref} LIMIT 1000;"

                else:
                    qran=False
                if(qran):
                    query_job = bqClient.query(query)
                    results = query_job.result()
                    queryResults.append([results, item['graphType']])

        elif domain == 'Condition':
            for item in values:
                qran = True
                if item['query'] == 'patients':
                    query = f"select subject.patientId from {table_ref} limit 1000;"

                elif item['query'] == 'types':
                    query = f"select code.text from {table_ref} limit 1000;"

                elif item['query'] == 'status':
                    query = f"SELECT coding.code FROM {table_ref} limit 1000;"

                elif item['query'] == 'howFound':
                    query = f"select encounter_type.text as FoundBecauseOf, condition.code.text as CurrentCondition from {table_ref} as condition join {table_ref} as encounter on encounter.id = condition.encounter.encounterId cross join unnest(encounter.type) as encounter type;"

                else:
                    qran=False
                if(qran):
                    query_job = bqClient.query(query)
                    results = query_job.result()
                    queryResults.append([results, item['graphType']])

        elif domain == 'Claim':
            for item in values:
                qran = True
                if item['query'] == 'type':
                    query = f"select c.code as claimType from {table_ref}, unnest(type.coding) as c limit 1000;"
                elif item['query'] == 'claimInfo':
                    query = f"select status, created, billablePeriod.end as BillablePeriodEnd from {table_ref} limit 1000;"
                elif item['query'] == 'reason':
                    query = f"select i.productOrService.text as ReasonForClaim from {table_ref}, unnest(item) as i limit 1000;"
                elif item['query'] == 'insurerCoverages':
                    query = f"select provider.display as InsuranceProvider, i.coverage.display as CoverageType from {table_ref}, unnest(insurance) as i group by provider.display, i.coverage.display limit 1000;"
                elif item['query'] == 'claimAmount':
                    query = f"select sum(total.value) as total_sum from {table_ref} where status = 'Active'";

                else:
                    qran=False
                if(qran):
                    query_job = bqClient.query(query)
                    results = query_job.result()
                    queryResults.append([results, item['graphType']])
    
    #If there is an admin Query, run it and grab results and graph type
    if adminData:
        query_job = bqClient.query(adminData[0])
        results = query_job.result()
        queryResults.append([results, adminData[-1]])

    if queryResults: #If something was returned from the query
        for i, result in enumerate(queryResults):
        #Iterate through query results, turn results into dataframe then to json, and associate data with requested chart type to return
        #To webpage for rendering
            returnedData.append({'data': result[0].to_dataframe().to_json(orient='records'),'chartType': result[-1]})
            #returnedData[i] = {'data': result[0].to_dataframe().to_json(orient='records'), 'chartType': result[-1]}
    #Add the number of graphs to display on the webpage
    numGraphs = len(returnedData)
    
    return returnedData, numGraphs

    
if __name__ == '__main__':
    random.seed(0)
    app.run(debug=True)
