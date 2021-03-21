from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import os
import uuid
import simplejson as json
from datetime import date
from datetime import datetime
from flask_socketio import SocketIO, send, emit
import requests
from flask_wtf.csrf import CSRFProtect
import html
 

app = Flask(__name__)

 
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'kaoutar.benghabrite@gmail.com'
app.config['MAIL_PASSWORD'] = 'wuxpfnsrunczrkjg'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
 

mail = Mail(app)

app.secret_key = '1337'
 
s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
socketio = SocketIO(app)

#  database connection details  
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'db_matcha'

mysql = MySQL(app)
 

@app.errorhandler(404)
def page_not_found(error):
    return render_template('erreur.html')

users_list = {}




@app.route('/')
def index():
    if 'loggedin' in session:
        return redirect(url_for('home'))

    return render_template('index.html' )
# --------------------------------------------------------------------------------------------------
# -------------------------------------#LOGIN--------------------------------------------------------
# --------------------------------------------------------------------------------------------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    
    if 'loggedin' in session:
        return redirect(url_for('home'))
    else :
        
        # Output message error
        msg = ''
        # Check if "username" and "password" POST requests exist  
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
            username = request.form['username']
            password = request.form['password']
           
            #Check if input empty
            if username != '' and password != '':
                # Check if account exists  
                try:
                    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                
                    cursor.execute('SELECT * FROM accounts WHERE username = %s ', [username])
                    account = cursor.fetchone()
                except:
                    msg = "something went wrong please try again"
                    return redirect(url_for('erreur'))
              
                
                if account:
                    if account['validation'] == 0 :
                        msg = 'To enjoy, please verify your account.'
                    else :     
                        if check_password_hash(account['password'], password):
                            session['loggedin'] = True
                            session['id'] = account['id']
                            session['username'] = account['username']
                            
                            # check complete_profile
                            try :
                                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                                cursor.execute('SELECT * FROM profiles WHERE id = %s',
                                    [session['id']])
                                profile = cursor.fetchone()
                            except:
                                msg = "something went wrong please try again"
                                return redirect(url_for('erreur'))

                            if profile:
                                if profile['profile_pic'] == '../static/img/avatar.jpg':
                                    return redirect(url_for('complete_profile'))
                                else :
                                    return redirect(url_for('home'))
                            else:
                                return redirect(url_for('complete_profile'))
                            
                        else:
                            msg = 'Incorrect password!'
                else:
                
                    msg = 'Incorrect username!'
            else:
                msg = 'Please fill all fields !'
        return render_template('login.html', msg=msg)
    # return render_template('login.html')








# --------------------------------------------------------------------------------------------------
# -------------------------------------#LOGOUT-------------------------------------------------------
# --------------------------------------------------------------------------------------------------

@app.route('/logout')
def logout():
    status_log = datetime.now()
    status_log = status_log.strftime("%b-%d-%Y %H:%M")
    try :
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE profiles SET status = %s  WHERE id = %s',
                    [status_log, session['id']])
        mysql.connection.commit()
    except:
        msg = "something went wrong please try again"
        return redirect(url_for('erreur'))

  
    try:
        del users_list[session['id']]  
    except :
        msg = "no user online"
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    

    # me = ''
  
    return redirect(url_for('login'))






# --------------------------------------------------------------------------------------------------
# -------------------------------------#REGISTER-----------------------------------------------------
# --------------------------------------------------------------------------------------------------

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'loggedin' in session:
        return redirect(url_for('home'))
    else:
        msg = ''
        # Check if "username", "password" and "email" POST requests exist  
        if request.method == 'POST' and 'firstname' in request.form and 'lastname' in request.form and 'username' in request.form and 'email' in request.form and 'password' in request.form and 'confrimpass' in request.form:
            try :
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            except:
                msg = "something went wrong please try again"
                return redirect(url_for('erreur'))

            firstname = request.form['firstname']
            lastname = request.form['lastname']
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            confrimpass = request.form['confrimpass']
        
            

            pattern = "^.*(?=.{8,})(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%^&+=]).*$"
            
            # Check if input empty
            if firstname != '' and lastname != '' and username != '' and email != '' and password != '' and confrimpass != '':
                try:
                    cursor.execute('SELECT * FROM accounts WHERE username = %s', [username])
                    found_username = cursor.fetchone()
                    cursor.execute('SELECT * FROM accounts WHERE email = %s', [email])
                    found_email = cursor.fetchone()
                except:
                    msg = "something went wrong please try again"
                    return redirect(url_for('erreur'))
        # --------------------------------------------------------------------------------------------------
                # If account exists show error and VALIDATION checks
        # --------------------------------------------------------------------------------------------------
                if found_username:
                    msg = 'Username already exists!'
                elif found_email:
                    msg = 'Email already exists!'
                elif not re.match("^[a-zA-Z]+$", firstname) or len(firstname) < 2 or len(firstname) > 10:
                    msg = 'Your Firstname must be at least 3 characters contain only characters !'
                elif not re.match("^[a-zA-Z]+$", lastname) or len(lastname) < 2 or len(lastname) > 10:
                    msg = 'Your Lastname must be at least 3 characters contain only characters !'
                elif not re.match("^[a-zA-Z0-9]+$",username) or len(username) < 2 or len(username) > 10:
                    msg = 'Username must be at least 3 characters contain only characters !'
                elif not re.match(r'[^@]+@[^@]+\.[^@]+', email) or len(email) > 50:
                    msg = 'Invalid email address!'
                elif not re.findall(pattern, password):
                    msg = "Password must be contain a number and an uppercase letter ."
                elif (len(password) < 8) or len(password) > 50:
                    msg = "Invalid password"
                elif password != confrimpass:
                    msg = 'Passord not same'
                elif not firstname or not lastname or not username or not email or not password or not confrimpass:
                    msg = 'Please fill out the form!'
                else:
                    hashed_password = generate_password_hash(password, method='sha256')
                    token = s.dumps(str(uuid.uuid4()) + firstname, salt='mytoken')

        # --------------------------------------------------------------------------------------------------
                                # INSERT ACCOUNT
        # --------------------------------------------------------------------------------------------------
                    valid = True
                    try:
                        msg = Message(
                            'Confirm Email', sender='kaoutar.benghabrite@gmail.com', recipients=[email])
                        link = url_for('confirm_email', token=token, _external=True)
                        msg.body = 'Your link is {}'.format(link)
                        mail.send(msg)
                        msg = 'You have successfully registered! CHECK UR MAIL'
                    except :
                        msg = "something went wrong"
                        valid = False

                    if valid :
                        try :
                            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s, %s, %s, %s, 0)',
                                        (firstname, lastname, username, email, hashed_password, token))
                            mysql.connection.commit()
                        except:
                            msg = "something went wrong please try again"
                            return redirect(url_for('erreur'))
 
                    
            else:
                msg = ' Please fill all fields !'    
        return render_template('register.html', msg=msg)
 








# --------------------------------------------------------------------------------------------------
# -------------------------------------#CONFIRM_MAIL-------------------------------------------------
# --------------------------------------------------------------------------------------------------


@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE token = %s',
                    [token])
        account = cursor.fetchone()
    except:
        msg = "something went wrong please try again"
        return redirect(url_for('erreur'))

    if account : 
        new_token = s.dumps(str(uuid.uuid4()) + account['firstname'], salt='mytoken')
       
       
        if account['validation'] == 0:
            try:
                experation = s.loads(token, salt='mytoken', max_age=14400)
            except SignatureExpired:
                return redirect(url_for('erreur'))

            try:
                cursor.execute('UPDATE accounts SET validation = 1 , token = %s  WHERE token = %s',
                            [new_token, token])
                mysql.connection.commit()
            except:
                msg = "something went wrong please try again"
                return redirect(url_for('erreur'))


            return render_template('confirm_email.html')
        else:
            return redirect(url_for('erreur'))
    else :
            return redirect(url_for('erreur'))





# --------------------------------------------------------------------------------------------------
# ----------------------------------#FORGOT_PASSWORD-------------------------------------------------
# --------------------------------------------------------------------------------------------------


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_pass():
    if 'loggedin' in session:
        return redirect(url_for('home'))
    else:
        msgshow = ''
        if request.method == 'POST' and 'username' in request.form:
            username = request.form['username']
            try :
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            except:
                msg = "something went wrong please try again"
                return redirect(url_for('erreur'))

            if username != '':

                try :
                    cursor.execute('SELECT * FROM accounts WHERE username = %s',
                                [username])
                    account = cursor.fetchone()
                except:
                    msg = "something went wrong please try again"
                    return redirect(url_for('erreur'))

                if account:
                    email = account['email']
                    token = account['token']
                    msg = Message(
                        'Email Verfication', sender='kaoutar.benghabrite@gmail.com', recipients=[email])
                    link = url_for('reset_pass', token=token, _external=True)
                    msg.body = 'HELLO {} ! You recently requested to reset your password for your Matcha account . Click the link to reset it. {} \n if you did not request a password reset, please ignore this email or reply to let us know.'.format(username, link)
                    mail.send(msg)
                    msgshow = 'Please check your email !'
                else:
                    msgshow = 'Username not found !'
            else:
                msgshow = 'Please fill all fields !'
        return render_template('forgot_pass.html', msg=msgshow)




# --------------------------------------------------------------------------------------------------
# -------------------------------------#RESET PASSWORD-----------------------------------------------
# --------------------------------------------------------------------------------------------------


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_pass(token):
    if 'loggedin' in session:
        return redirect(url_for('home'))
    else:
        msg = ''
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM accounts WHERE token = %s',
                        [token])
            account = cursor.fetchone()
        except:
            msg = "something went wrong please try again"
            return redirect(url_for('erreur'))

        if account :
            if request.method == 'POST' and 'password' in request.form and 'confirm_password' in request.form:
                password = request.form['password']
                confirm_password = request.form['confirm_password']
                if password != '' and confirm_password != '':
                    pattern = "^.*(?=.{8,})(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%^&+=]).*$"
                        # msg = "good"
                    if not re.findall(pattern, password):
                        msg = "Password must be contain a number and an uppercase letter ."
                    elif (len(password) < 8) or len(password) > 50:
                        msg = "Password must be at least 8 characters long"
                    elif password != confirm_password:
                        msg = 'Passord not same'
                    else:
                        new_token = s.dumps(str(uuid.uuid4()) + account['firstname'], salt='mytoken')
                        hashed_password = generate_password_hash(password, method='sha256')
                        try :
                            cursor.execute('UPDATE accounts SET password = %s , token = %s  WHERE token = %s ',
                                        [hashed_password, new_token, token])

                            mysql.connection.commit()
                        except:
                            msg = "something went wrong please try again"
                            return redirect(url_for('erreur'))
                            
                        return redirect(url_for('login'))
                else:
                    msg = 'Please fill all fields !'
        else :
            return redirect(url_for('erreur'))
        return render_template('reset_pass.html', msg=msg, token=token)

# --------------------------------------------------------------------------------------------------
# ----------------------------------------#HOME PAGE-------------------------------------------------
# --------------------------------------------------------------------------------------------------

@app.route('/home', methods=['GET', 'POST'], defaults={'page':1})
@app.route('/home/<int:page>', methods=['GET', 'POST'])
def home(page):
   
    perpage=8
    startat = (page - 1) * perpage
    # print(request.full_path)
    # print(request.full_path.replace("/home",""))
 
    me = ''
    if 'loggedin' in session:
        try :
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM profiles WHERE id = %s',
                        [session['id']])
            profile = cursor.fetchone()
        except:
            msg = "something went wrong please try again"
            return redirect(url_for('erreur'))

        if not profile:
            return redirect(url_for('complete_profile'))
        if profile:
            if profile['profile_pic'] == '../static/img/avatar.jpg':
                return redirect(url_for('edit_profile'))
            else:
                filterr = request.args.get("filterr")
                sort = request.args.get("sort")
                blocks = block_users(session['id'])
                me = data_prof(session['id'])
                check_reports = check_report(session['id'])
                if check_reports['COUNT(*)'] >= 5:
                    return redirect(url_for('report'))

                notification = notifications(me['username'])
                count_vue_notif = notification_count(me['username'])

                 
                sql = sql_browser()
                sql += ' ORDER BY '
                if filterr == 'age':
                    sql += ' age '
                elif filterr == 'Distance':
                    sql += ' km '
                elif filterr == 'Popularity':
                    sql += ' score   '
                elif filterr == 'Interests':
                    sql += ' hashtag '

                if sort == 'az':
                    sql += ' ASC , '
                elif sort == 'za':
                    sql += ' DESC ,'
                    # sql += ' ASC , ' 
                elif not sort:
                    if filterr:
                        sql += ' ASC , '
                sql += ' km, score '    
                sql += ' limit ' + str(startat) + ',' + str(perpage)
               
               
                try :
                    cursor.execute(sql)
                    users = cursor.fetchall()
                except:
                    msg = "something went wrong please try again"
                    return redirect(url_for('erreur'))
                    
                found_like = []
                try :
                    cursor.execute('SELECT * FROM likes WHERE id_liker = %s',
                                [session['id']])
                    likes = cursor.fetchall()
                except:
                    msg = "something went wrong please try again"
                    return redirect(url_for('erreur'))

                for like in likes:
                    found_like.append(like['id_liked'])

        else:
            return redirect(url_for('complete_profile'))

        

    else:
        return redirect(url_for('login'))
    return render_template('home.html', users=users, filterr=filterr,sort = sort,  found_like=found_like, me=me, users_list=users_list, notification=notification, blocks=blocks , count_vue_notif=count_vue_notif , check_report=check_report,page=page )

  
 # --------------------------------------------------------------------------------------------------
# -------------------------------------#EDIT PROFILE-------------------------------------------------
# --------------------------------------------------------------------------------------------------

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    

    if 'loggedin' in session:
        msg = ''
        
        msg = request.args.get('msg')
        if msg == None:
            msg = ''
        try :
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM profiles WHERE id = %s',
                            [session['id']])
            profile = cursor.fetchone()
        except:
            msg = "something went wrong please try again"
            return redirect(url_for('erreur'))

        if not profile:
            return redirect(url_for('complete_profile'))

        if profile:
            if profile['profile_pic'] == '../static/img/avatar.jpg':
                msg = "To enjoy, you need to add a profile picture"
        check_reports = check_report(session['id'])
        if check_reports['COUNT(*)'] >= 5 :
            return redirect(url_for('report'))
        blocks = block_users(session['id'])
        try :
            cursor.execute('SELECT id_blocked FROM blocks WHERE id_blocker = %s  ',
                    [session['id']])
            blocked_user = cursor.fetchall()
        except:
            msg = "something went wrong please try again"
            return redirect(url_for('erreur'))
 
        
        try :
            cursor.execute('SELECT * FROM accounts WHERE id = %s',
                        [session['id']])
            data_myaccount = cursor.fetchone()
        except:
            msg = "something went wrong please try again"
            return redirect(url_for('erreur'))

        # FETCH MY PROFILE
        data_myprofile = data_prof(session['id'])
        notification = notifications(data_myprofile['username'])
        count_vue_notif = notification_count(data_myprofile['username'])
        # FETCH ALL PROFILES
        try :
            cursor.execute("SELECT * FROM profiles WHERE id != %s",
                        [session['id']])
            data_profiles = cursor.fetchall()
        except:
            msg = "something went wrong please try again"
            return redirect(url_for('erreur'))
        hashtags = []
         
        data_myprofile['hashtag'] = data_myprofile['hashtag'].split("#")
        for j in data_myprofile['hashtag']:
                j = j.lower()
                j = j.replace("+", "")
                if j.strip() not in hashtags:
                    hashtags.append(j)
        while ("" in hashtags):
            hashtags.remove("")
        
        input_hashtag = ''
        for hashtag in hashtags:
            input_hashtag += hashtag + ','

         
        if request.method == 'POST':
           
            username = request.form['username']
            
            #profile_pic 
            profilepicc = request.files["profilepic"]
            picturename = ""
            save_new = True
            if profilepicc:
                try:
                    profilepicc = Image.open(profilepicc)
                    profilepicc = profilepicc.resize((400,400))

                except:
                    save_new = False
                    isvalid = False
                    picturename = data_myprofile["profile_pic"]
                    msg = "invalid format image profile"
                if save_new == True:
                    pictursave = str(uuid.uuid4()) + '.png'
                    picturename = "../static/image/" + pictursave
                    profilepicc.save(os.path.join("static/image", pictursave))
            else :
                picturename = data_myprofile["profile_pic"]

                
            


            # USERNAME
            for username_profile in data_profiles:
                if username_profile['username'] == username and not data_myprofile['username'] == username:
                    username = data_myprofile['username']
                    msg = 'username exist'
            #  LASTNAME / FIRSTNAME
            firstname = request.form['firstname']
            lastname = request.form['lastname']
 
            if not re.match(r'[A-Za-z]+', firstname) or len(firstname) < 2 or len(firstname) > 20:
                msg = 'Incorrect firstname'
            if not re.match(r'[A-Za-z]+', lastname) or len(lastname) < 2 or len(lastname) > 20:
                msg = 'Incorrect Lastname'
            

           
            email = request.form['email']
            datebirth = request.form['datebirth']
            


            #  AGE :
            if not re.match("([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))", datebirth):
                    msg = 'Invalid date '
                    isvalid = False
            else:
                if datebirth != '':
                    datebirth = request.form['datebirth'].split("-")
                    age = calculateAge(date(int(datebirth[0]), int(datebirth[1]), int(datebirth[2])))
                
            age = ''
            if age :
                if age < 16 or age > 120:
                    msg = 'Age must be more than years 16 old'
                else:
                    age = data_myprofile['age']
            else:
                age = data_myprofile['age']


            #  GENDER :
            gender = request.form['gender']
         
            if gender != 'male' and gender != 'female':
                gender = data_myprofile['gender']
               


            # PREFERENCE:
            preference = request.form['preference']
            if not preference == 'Bisexual' and preference == 'Heterosexual' and preference == 'Homosexual':
                preference = data_myprofile['preference']


            #bio

            bio = request.form['bio']
            if bio == '':
                bio = data_myprofile['bio']

            #location
            latitude = request.form['lat']
            longitude = request.form["long"]

            if  (longitude != '' and latitude != '' ) and (longitude != 'None' and latitude != 'None')  :
                check_city = get_city(latitude, longitude)
                if check_city == 'None':
                    msg = 'Invalid Location'
                    latitude = data_myprofile['lat']
                    longitude = data_myprofile['lon']

           
            hashtags = request.form['hashtag']
            #validation
            valid = True
            if not re.match(r'[A-Za-z]+', username) or len(username) < 2 or len(username) > 10:
                msg = 'Incorrect username'
                valid = False
            elif not re.match("^[a-zA-Z]+$", firstname) or len(firstname) < 2 or len(firstname) > 10:
                msg = 'Name must be at least 3 characters contain only characters and numbers!'
                valid = False
            elif not re.match("^[a-zA-Z]+$", lastname) or len(lastname) < 2 or len(lastname) > 10:
                msg = 'Surname must be at least 3 characters contain only characters and numbers!'
                valid = False
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email) or len(email) > 50:
                msg = 'Invalid email address!'
                valid = False
       
            elif not re.match(r'[A-Za-z]+', bio) or len(bio) < 2 or len(bio) > 250:
                msg = 'Incorrect bio'
                valid = False
            elif not hashtags == '':

                hashtag = '#+' + (hashtags.replace(",", "+#+")) + '+'
                if not re.match("^[A-Za-z0-9\_\,]*$", hashtags) or (len(hashtags) < 2 or len(hashtags) > 15):
                    msg = 'Invalid hashtags'
                    valid = False
            
            #img1 :
            img1 = request.files["img1"]
            img1name = ""
            save_new_img1 = True
            if img1:
                try:
                    img1 = Image.open(img1)
                    img1 = img1.resize((400,400))
                except:
                    save_new_img1 = False
                    isvalid = False
                    img1name = data_myprofile["img1"]
                    msg = "Invalid format image 1"
                if save_new_img1 == True:
                    os.remove(data_myprofile['img1'][3:])
                    img1save = str(uuid.uuid4())+'.png'
                    img1name = "../static/image/"+img1save
                    img1.save(os.path.join("static/image",img1save))
            else:
                img1name = data_myprofile["img1"]
            

             #img2 :
            img2 = request.files["img2"]
            img2name = ""
            save_new_img2 = True
            if img2:
                try:
                    img2 = Image.open(img2)
                    img2 = img2.resize((400,400))
                except:
                    save_new_img2 = False
                    isvalid = False
                    img2name = data_myprofile["img2"]
                    msg = "Invalid format image 2"
                if save_new_img2 == True:
                    os.remove(data_myprofile['img2'][3:])
                    img2save = str(uuid.uuid4())+'.png'
                    img2name = "../static/image/"+img2save
                    img2.save(os.path.join("static/image",img2save))
            else:
                img2name = data_myprofile["img2"]


             #img3 :
            img3 = request.files["img3"]
            img3name = ""
            save_new_img3 = True
            if img3:
                try:
                    img3 = Image.open(img3)
                    img3 = img3.resize((400,400))
                except:
                    save_new_img3 = False
                    isvalid = False
                    img3name = data_myprofile["img3"]
                    msg = "Invalid format image 3"
                if save_new_img3 == True:
                    os.remove(data_myprofile['img3'][3:])
                    img3save = str(uuid.uuid4())+'.png'
                    img3name = "../static/image/"+img3save
                    img3.save(os.path.join("static/image",img3save))
            else:
                img3name = data_myprofile["img3"]



             #img4 :
            img4 = request.files["img4"]
            img4name = ""
            save_new_img4 = True
            if img4:
                try:
                    img4 = Image.open(img4)
                    img4 = img4.resize((400,400))
                except:
                    save_new_img4 = False
                    isvalid = False
                    img4name = data_myprofile["img4"]
                    msg = "Invalid format image 4"
                if save_new_img4 == True:
                    os.remove(data_myprofile['img4'][3:])
                    img4save = str(uuid.uuid4())+'.png'
                    img4name = "../static/image/"+img4save
                    img4.save(os.path.join("static/image",img4save))
            else:
                img4name = data_myprofile["img4"]




                
                             
            if valid == True:
               
                hashtag = '#+' + (hashtags.replace(",", "+#+")) + '+'
              
                try :
                    cursor.execute('UPDATE accounts SET firstname = %s, lastname = %s , username = %s , email = %s WHERE id = %s ', [
                                firstname, lastname, username, email, session['id']])
                    cursor.execute("UPDATE profiles SET username = %s, gender = %s, preference = %s, bio = %s, age = %s, hashtag = %s, lat = %s, lon = %s, profile_pic = %s, img1 = %s, img2 = %s, img3 = %s, img4 = %s WHERE id = %s", [
                                username, gender, preference, bio, age, hashtag, latitude, longitude, picturename, img1name, img2name, img3name, img4name, session['id']])
                    mysql.connection.commit()
                except:
                    msg = "something went wrong please try again"
                    return redirect(url_for('erreur'))
                







            
                    
            if 'old_password' in request.form and 'password' in request.form and 'confrim_password' in request.form:
                pattern = "^.*(?=.{8,})(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%^&+=]).*$"

                old_password = request.form['old_password']
                password = request.form['password']
                confirm_password = request.form['confrim_password']

                if not old_password == '':
                    if not re.findall(pattern, password):
                        msg = "Password must be contain a number and an uppercase letter ."
                    elif (len(password) < 8) or len(password) > 50:
                        msg = "Password must be at least 8 characters long"
                    else:
                        try :
                            cursor.execute('SELECT password from accounts where id = %s',
                                            [session['id']])
                            mypassword = cursor.fetchone()
                        except:
                            msg = "something went wrong please try again"
                            return redirect(url_for('erreur'))
                        
                        if check_password_hash(mypassword['password'], old_password) and password == confirm_password:
                            password = generate_password_hash(password)
                             
                            try :
                                cursor.execute("UPDATE accounts SET password = %s WHERE id = %s",
                                        [password, session['id']])
                                mysql.connection.commit()
                            except:
                                msg = "something went wrong please try again"
                                return redirect(url_for('erreur'))

                            msg = "Password has been changed"
                        else:
                            msg = 'Wrong password !'
                    
           

            return redirect(url_for('edit_profile', msg=msg))


                    


        me = data_myprofile
    else:
        return redirect(url_for('login'))
    return render_template('edit_profile.html', msg=msg, data_myprofile=data_myprofile, data_myaccount=data_myaccount, input_hashtag=input_hashtag, blocks=blocks, notification=notification, me=me, count_vue_notif=count_vue_notif, blocked_user=blocked_user)


# --------------------------------------------------------------------------------------------------
# -------------------------------------#ERROR PAGE---------------------------------------------------
# --------------------------------------------------------------------------------------------------


@app.route('/erreur')
def erreur():
    return render_template('erreur.html')



if __name__ == '__main__':
    socketio.run(app, debug=True)
