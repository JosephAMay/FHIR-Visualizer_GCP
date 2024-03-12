#Imports
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file,jsonify
from flask_socketio import SocketIO, emit
import mysql.connector
import os
from werkzeug.utils import secure_filename
import csv
import sys
import time  
from google.cloud import bigquery
import matplotlib.pyplot as plt
from collections import Counter
import datetime
#Add folder housing the project to the filepath
bigfolder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(bigfolder_path)



#App settings 
MAX_CLIENTS = 100
OVER_CAPACITY=False
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = 'SoftwareProject'
app.config['SESSION_COOKIE_NAME'] = 'user_session'
socketio = SocketIO(app)
#Possible client connections
available_sockets = list(range(1, MAX_CLIENTS+1))
clients = []
'''
Patient - by gender, by age, ethnicity, 
RACTITIONER: by age, gender, qualification->issuer->organizationId/reference, qualification->period->start/end,
Condition --> bodysite, severity, committimestamp
Medication request->insurance->coverageid, priority,->medication->reference->medicationID
Procedure->basedon->careplanId/servicerequestID,locaion->locationID, performed->dateTime,performed->age

'''

bqClient = bigquery.Client(project='fhir-visualization-project')
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Mandarin143!",
    database="visualization"
)
cursor = db.cursor()
        
def query_database(username, password,tablename):
    global cursor
    if tablename == 'worker':
        query = "SELECT * FROM worker WHERE username=%s AND password=%s"
    elif tablename == 'user':
        query = "SELECT * FROM user WHERE username=%s AND password=%s"
    else:
        print('TableName Not specified')
        return None
    
    cursor.execute(query, (username, password))
    result = cursor.fetchone()
    print('query result is ==',result)
    return result

def bigquery_lookup(qtype):
    project_id = "fhir-visualization-project"
    dataset_id = "dataset1"

    if qtype == 'patient':
        table_id = "Patient"
    elif qtype=='records':
        table_id = 'Records'
    
    # Construct the fully qualified table reference
    table_ref = f"{project_id}.{dataset_id}.{table_id}"
    print('Query Type=', qtype, '\nTableRef = ', table_ref)
    # Construct a BigQuery SQL query
    query = f"SELECT * FROM `{table_ref}` LIMIT 10"
    
    query = f"SELECT id AS patientID, name[safe_offset(0)].given AS given_name,name[safe_offset(0)].family AS family,birthDate AS birth_date, gender as gender from {table_ref}"
    print('QUery Job is:', query)
    # Execute the query
    query_job = bqClient.query(query)

    # Fetch the results
    results = query_job.result()
    names = []
    genders = []
    birth_dates = []
    for item in results:
        names.append(f"Name: {item.given_name}\tFamily:{item.family}")
        genders.append(item.gender)
        birth_dates.append(item.birth_date)

    # Extract birth dates from the results
    for record in zip(names,genders):
        print(record)    
    
    #print(birth_dates)
    birth_dates = [datetime.datetime.strptime(date, '%Y-%m-%d') for date in birth_dates]
    # Count occurrences of each birth date
    birth_date_counts = Counter(birth_dates)

    # Sort the dates for plotting
    sorted_dates = sorted(birth_date_counts.keys())

    # Prepare data for plotting
    x_values = range(len(sorted_dates))
    y_values = [birth_date_counts[date] for date in sorted_dates]

    # Plot the histogram
    plt.figure(figsize=(10, 6))
    plt.bar(x_values, y_values, tick_label=sorted_dates, align='center')
    plt.xlabel('Birth Date')
    plt.ylabel('Frequency')
    plt.title('Histogram of Birth Dates')
    plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for better readability
    plt.tight_layout()
    plt.savefig('GraphName.png')
    return results 

#Handle client connections
@socketio.on('connect')
def handle_connect():
    global OVER_CAPACITY
    #If there is enough space for this client, assign them a socket and add them to the list
    if len(clients) <= MAX_CLIENTS and available_sockets:
        socket_number = available_sockets.pop(0)
        client_sid = request.sid
        clients.append({'sid': client_sid, 'socket_number': socket_number})
        #print(f'Length of clients is: {len(clients)}')
        #print('clients:')
        #for i in clients:
        #    print(i)
    else: #Full
        OVER_CAPACITY = True

#Handle client disconnections
#Remove from clients list, add socket back to list of available sockets. 
@socketio.on('disconnect')
def handle_disconnect():
    global OVER_CAPACITY
    client_sid = request.sid
    disconnected_client = next((client for client in clients if client['sid'] == client_sid), None)
    
    if disconnected_client:
        # Add the socket number back to available_sockets
        available_sockets.append(disconnected_client['socket_number'])
        # Remove the disconnected client from the clients list
        clients.remove(disconnected_client)
        OVER_CAPACITY = False
        print('Disconnect: Length of clients is:', len(clients))


@socketio.on('upload_file')
def handle_upload(data):
    #client = next((client for client in self.clients if client['sid'] == request.sid), None)
    #if client:
        #socket_number = client['socket_number']
        uploaded_file = data['file']
        accept_uploaded_file(uploaded_file, socket_number)
        #result = self.process_csv(f"uploads/{uploaded_file.filename}")
        emit('csv_processed', {'socket_number': socket_number, 'result': result})

@app.route('/login', methods=['GET', 'POST'])
def login():
    global OVER_CAPACITY
    if (OVER_CAPACITY):
        return render_template('about.html', full = True)

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = query_database(username, password, 'user')
        worker = query_database(username, password, 'worker')
        if worker is not None:
            session['username'] = username
            session['role'] = 'employee'
            return redirect(url_for('results'))
        elif user is not None:
            session['username'] = username
            session['role'] = 'user'
            return redirect(url_for('results'))
        
    return render_template('login.html')


@app.route('/FHIR-Visualization', methods=['GET', 'POST'])
def results():
    global OVER_CAPACITY
    #IF website at max client capacity, send to wait area
    if(OVER_CAPACITY):
        return render_template('about.html', full = True)
    
    #if user is logged in take their file
    if 'username' in session:
        username = session['username']
    print('Trying BQ Func')
    result = bigquery_lookup('patient')
    print(result)
    return render_template('fhir_vizualizer.html', username=username)
    #return render_template('about.html')

#After the user has submitted a file and it is classified, send modified folder to their downloads folder
@app.route('/download/<filename>')
def download_file(filename):
    #Get user home directory and path to downloads folder, send modified file there
    downloads_folder = os.path.expanduser("~")
    file_path = os.path.join(downloads_folder, filename)
    return send_file(file_path, as_attachment=True)


#home page
@app.route('/')
def about():
    global OVER_CAPACITY
    
    #If full let client know to wait a bit
    if(OVER_CAPACITY):
        return render_template('about.html', full = True)
    
    if(not OVER_CAPACITY):
        return render_template('about.html')
    

if __name__ == '__main__':
    socketio.run(app, debug=True)
