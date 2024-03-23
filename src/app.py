from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from werkzeug.utils import secure_filename
import os
import ipfsapi

client = MongoClient('127.0.0.1', 27017)
db = client.insurance_fraud_detection

hospitals_db=db['hospitals']
patients_db=db['patients']

c = db.c 
claims_collection = db.c  # MongoDB collection for claims

app = Flask(__name__)
app.secret_key = 'sai@'
app.config["uploads"] = "uploads/"


@app.route('/')
def home():
    return render_template('Index.html')

@app.route('/about')
def about():
    return render_template('about.html')

# Routes for login pages
@app.route('/patient_login')
def login():
    return render_template('Patient_l.html')

@app.route('/hospital_login')
def hospital_management_login():
    return render_template('Hospital_Management_l.html')

@app.route('/insurance_login')
def insurance_company_login():
    return render_template('Insurance_company_l.html')

@app.route('/patient_home')
def Patient_home_page():
    return render_template('Patient_Home.html')

# Routes for signup pages
@app.route('/patient_signup')
def signup():
    hos_data=hospitals_db.find()
    data=[]
    for i in hos_data:
        dummy=[]
        dummy.append(i['hospital'])
        dummy.append(i['username'])
        data.append(dummy)
    return render_template('Patient_s.html',data=data)

@app.route('/hospital_signup')
def hospital_management_signup():
    return render_template('Hospital_s.html')

@app.route('/insurance_signup')
def insurance_company_signup():
    return render_template('Insurance_s.html')

patients_and_claims = []

@app.route('/hos_home')
def home_page():
    patients_and_claims=c.find()
    return render_template('hospital_home.html', patients_and_claims=patients_and_claims)

@app.route('/upload_claim', methods=['POST'])
def hospital_home():
    data=request.form
    claims_collection.insert_one(dict(data))
    patients_and_claims=claims_collection.find()
    chooseFile=request.files['chooseFile']
    doc=secure_filename(chooseFile.filename)
    chooseFile.save(app.config['uploads']+'/'+doc)
    client=ipfsapi.Client('127.0.0.1',5001)
    print(app.config['uploads']+'/'+doc)
    response=client.add(app.config['uploads']+'/'+doc)
    print(response)
    return render_template('hospital_home.html', patients_and_claims=patients_and_claims)

# Handling form submissions for login
@app.route('/patient_login', methods=['POST'])
def login_data():
    patient_name = request.form['patient_name']
    password = request.form['password']
    user_data = patients_db.find_one({'patient_name': patient_name, 'password': password})
    print(patient_name,password)
    print(user_data)
    if user_data:
        session['patient_name'] = patient_name
        user_data = c.find_one({'patient_name': patient_name})
        if user_data:
            diagnosis = user_data.get('diagnosis', '')
            age = user_data.get('age', '')
            phone_number = user_data.get('phone_number', '')

            # Sample claim status data (replace with your actual claim status retrieval mechanism)
            claims_data = []
            
            return render_template('/Patient_Home.html', name=patient_name, diagnosis=diagnosis, age=age, phone=phone_number, claims=claims_data)
        else:
            return 'User data not found.'
    else:
        return render_template('Patient_l.html', err1='Invalid Credentials')

# Handling form submissions for signup
@app.route('/patient_signup', methods=['POST'])
def signup_data():
    hospital = request.form['hospital']
    id = request.form['id']
    patient_name = request.form['patient_name']
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    existing_user = patients_db.find_one({'patient_name': patient_name})
    if existing_user:
        return render_template('Patient_s.html', err='You have already registered')
    user_data = {'hospital': hospital, 'id': id, 'patient_name': patient_name, 'password': password, 'confirm_password':confirm_password}
    patients_db.insert_one(user_data)
    return render_template('Patient_l.html', res='You have registered successfully')

@app.route('/hospital_login', methods=['POST'])
def hospital_data():
    username = request.form['username']
    password = request.form['password']
    user_data = hospitals_db.find_one({'username': username, 'password': password})
    if user_data:
        session['username'] = username
        return redirect('/hos_home')
    else:
        return render_template('Hospital_Management_l.html', err1='Invalid Credentials')

@app.route('/hospital_signup', methods=['POST'])
def hospital_signup():
    if request.method == 'POST':
        hospital = request.form['hospital']
        id = request.form['id']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        existing_user = hospitals_db.find_one({'username': username})
        if existing_user:
            return render_template('Hospital_s.html', err='You have already registered')

        user_data = {'hospital': hospital, 'id': id, 'username': username, 'password': password, 'confirm_password': confirm_password}
        hospitals_db.insert_one(user_data)
        return render_template('Hospital_Management_l.html', res='You have registered successfully')

    return render_template('Hospital_s.html')

# @app.route('/upload_claim', methods=['POST'])
# def upload_claim():
#     if 'username' not in session:
#         return redirect(url_for('login'))  # Redirect if user is not logged in

#     patient_name = request.form.get('patient_name')
#     claim_id = request.form.get('claim_id')
#     age = request.form.get('age')
#     phone_number = request.form.get('phone_number')
#     dob = request.form.get('dob')
#     address = request.form.get('address')
#     diagnosis = request.form.get('diagnosis')
#     start_month = request.form.get('start_month')
#     claim_amount = request.form.get('claim_amount')
#     doc = request.files.get('chooseFile')

#     # Check if any of the required form fields are missing
#     if None in (patient_name, claim_id, age, phone_number, dob, address, diagnosis, start_month, claim_amount, doc):
#         return "Missing required form fields", 400

#     if 'username' not in os.listdir():
#         os.mkdir(session['username'])

#     doc1 = secure_filename(doc.filename)
#     doc.save(os.path.join(session['username'], doc1))

#     patients_and_claims.append({
#         'patient_name': patient_name,
#         'claim_id': claim_id,
#         'age': age,
#         'phone_number': phone_number,
#         'dob': dob,
#         'address': address,
#         'diagnosis': diagnosis,
#         'start_month': start_month,
#         'claim_amount': claim_amount
#     })

#     return redirect(url_for('upload_claim'))

@app.route('/patient_home')
def patient_home_page():
    if 'patient_name' in session:
        patient_name = session['patient_name']
        user_data = c.find_one({'patient_name': patient_name})
        print(user_data)
        if user_data:
            diagnosis = user_data.get('diagnosis', '')
            age = user_data.get('age', '')
            phone_number = user_data.get('phone_number', '')
            
            # Sample claim status data (replace with your actual claim status retrieval mechanism)
            claims = []
            
            return render_template('/Patient_Home.html', name=patient_name, diagnosis=diagnosis, age=age, phone_number=phone_number, claims=claims)
        else:
            return 'User data not found.'
    else:
        return redirect(url_for('/patient_login'))  # Redirect to the login page

@app.route('/logout')
def logout():
    session['username']=None
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=9001)
