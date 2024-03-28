from flask import Flask, render_template, url_for, request, redirect, session
import mysql.connector
from cmail import sendmail
from otp import genotp

app = Flask(__name__)
app.secret_key = "my_super_secret_key_that_no_one_should_know"

mydb = mysql.connector.connect(host="localhost", user="root", password="system", database="blog")

with mydb.cursor() as cursor:
    cursor.execute("CREATE TABLE IF NOT EXISTS registration (username VARCHAR(39), mobile VARCHAR(20), email VARCHAR(50), address VARCHAR(50), password VARCHAR(255))")

@app.route('/')
def homepage():
    return render_template('homepage.html')

@app.route('/reg', methods=['GET','POST'])
def reg():
    if request.method == 'POST':
        username = request.form['username']
        mobile = request.form['mobile']
        email = request.form['email']
        address = request.form['address']
        password = request.form['password']
        otp = genotp()
        sendmail(to=email, subject="Thanks for registration", body=f'OTP is: {otp}')
        session['registration_data'] = {
            'username': username,
            'mobile': mobile,
            'email': email,
            'address': address,
            'password': password,
            'otp': otp
        }
        return render_template('verification.html', otp=otp)
    return render_template('registration.html')

@app.route('/otp', methods=['POST'])
def verify_otp():
    uotp = request.form['uotp']
    if 'registration_data' in session:
        registration_data = session.pop('registration_data')
        if uotp == registration_data['otp']:
            with mydb.cursor() as cursor:
                cursor.execute('INSERT INTO registration VALUES (%s, %s, %s, %s, %s)', (registration_data['username'], registration_data['mobile'], registration_data['email'], registration_data['address'], registration_data['password']))
                mydb.commit()
            return redirect(url_for('login'))
    return 'Enter a valid OTP'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with mydb.cursor() as cursor:
            cursor.execute('SELECT COUNT(*) FROM registration WHERE username = %s AND password = %s', (username, password))
            data = cursor.fetchone()[0]
            if data == 1:
                session['username'] = username
                return redirect(url_for('homepage'))
    return render_template('login.html')



@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/addpost', methods=['GET', 'POST'])
def add_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        slug = request.form['slug']
        with mydb.cursor() as cursor:
            cursor.execute('INSERT INTO posts (title, content, slug) VALUES (%s, %s, %s)', (title, content, slug))
            mydb.commit()
    return render_template('add_post.html')

@app.route('/view_posts')
def view_post():
    with mydb.cursor() as cursor:
        cursor.execute("SELECT * FROM posts")
        posts = cursor.fetchall()
    return render_template('view_posts.html', posts=posts)
app.run(debug=True, use_reloader=True)