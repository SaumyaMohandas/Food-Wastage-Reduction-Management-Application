from flask import Flask, render_template, request, redirect, url_for, session
import ibm_db
import re
app = Flask(__name__)
app.secret_key='a'
conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=ba99a9e6-d59e-4883-8fc0-d6a8c9f7a08f.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=31321;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA (1).crt;UID=plz69289;PWD=jYJ4fpRfDKFIWaxh",'','')
print(conn)
print('connected')

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def aboutus():
    return render_template('about.html')

@app.route('/login-register')
def contactus():
    return render_template('login-register.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

   



# @app.route('/contact')
# def contactus():
#     return render_template('contact.html')



@app.route('/login',methods=['GET','POST'])
def login():
    global userid
    msg=''
       
    if request.method == 'POST' :
            username = request.form['username']
            password = request.form['password']
            sql = "SELECT * FROM login_table WHERE username =? AND password=?"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt,1,username)
            ibm_db.bind_param(stmt,2,password)
            ibm_db.execute(stmt)
            account = ibm_db.fetch_assoc(stmt)
            print (account)
            if account:
                session['loggedin'] = True
                session['id'] = account['USERNAME']
                userid=  account['USERNAME']
                session['USERID'] = account['USERID']
                msg = 'Logged in successfully !'
                # msg = 'Logged in successfully !'
                return redirect(url_for("home"))
            else:
                msg='Incorrect username/password!'
                return render_template('login.html',msg=msg) 
                
           
    return render_template('login.html',msg=msg)           

    
@app.route('/register',methods=['GET','POST'])
def register():
    msg=''
    if request.method=='POST':
        name=request.form['name']
        username=request.form['username']
        email=request.form['email']
        password=request.form['password']
        role = request.form['role']
        sql="SELECT * FROM login_table WHERE username=? AND password=?"
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,username)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            msg='Account already exits!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg='name must contain only characters and numbers!'
        else:
            sql = "SELECT count(*) FROM login_table"
            stmt = ibm_db.prepare(conn,sql)
            ibm_db.execute(stmt)
            length = ibm_db.fetch_assoc(stmt)
            print(length)

            insert_sql = "INSERT INTO  login_table VALUES (?, ?, ?,?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            
            ibm_db.bind_param(prep_stmt, 1, name)
            ibm_db.bind_param(prep_stmt, 2, email)
            ibm_db.bind_param(prep_stmt, 3, username)
            ibm_db.bind_param(prep_stmt, 4, password)
            ibm_db.bind_param(prep_stmt, 5, length['1']+1)
            ibm_db.bind_param(prep_stmt, 6, role) 
            ibm_db.execute(prep_stmt)
            #msg='You Have Successfully registerd!'
            
            return render_template('login.html',msg=msg)

    return render_template('register.html',msg=msg)

@app.route('/home', methods=['POST', 'GET'])
def home():
    sql = "SELECT * FROM login_table WHERE USERID=" + str(session['USERID'])
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
    User = ibm_db.fetch_tuple(stmt)
    print(User)
    print('data fetched')
    if User[5] == 0:
        print('agent')
       
        return render_template("agent-page.html", user= User)
      

    elif User[5] == 1:
        print('admin')
        
        return render_template("admin.html", user= User)

   
    elif User[5] == 2:
       print('donor')
        
       return render_template('donor.html') 

@app.route('/donate',  methods=['POST', 'GET'])
def donate():
    sql = "SELECT * FROM login_table WHERE USERID=" + str(session['USERID'])
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
    User = ibm_db.fetch_tuple(stmt)
    print(User)
    if request.method=='POST':
       
        TYPE_OF_FOOD=request.form['food']
        DATE_OF_COOKING=request.form['date']
        TIME_OF_COOKING=request.form['time']
        QUANTITY=request.form['quantity']
        LOCATION=request.form['location']
        sql = "INSERT INTO  donation_table VALUES (?,?,?,?,?,?,?,?, NULL, NULL)"
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,User[2])
        ibm_db.bind_param(stmt,2,User[1])
        ibm_db.bind_param(stmt,3,TYPE_OF_FOOD)
        ibm_db.bind_param(stmt,4,DATE_OF_COOKING)
        ibm_db.bind_param(stmt,5,TIME_OF_COOKING)
        ibm_db.bind_param(stmt,6,QUANTITY)
        ibm_db.bind_param(stmt,7,LOCATION)
        ibm_db.bind_param(stmt,8,User[4])
        ibm_db.execute(stmt)
    return render_template('donate.html') 



@app.route('/data') 
def data1():
    sql1="SELECT * FROM donation_table"
    stmt1=ibm_db.prepare(conn, sql1)
    ibm_db.execute(stmt1)
    donation = ibm_db.fetch_tuple(stmt1)
    print(donation)
    user1=[]
    while donation!= False:
        user1.append(donation)
        donation = ibm_db.fetch_tuple(stmt1)
    print(user1)
    return render_template("data.html",responses= user1)

 
@app.route('/Notifications') 
def Notifications():
    sql = "SELECT * FROM login_table WHERE USERID=" + str(session['USERID'])
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
    User = ibm_db.fetch_tuple(stmt)
    print(User)
    if User[5] == 0:
        sql1="SELECT * FROM donation_table"
        stmt1=ibm_db.prepare(conn, sql1)
        ibm_db.execute(stmt1)
        donation = ibm_db.fetch_tuple(stmt1)
        print(donation)
        user1=[]
        while donation!= False:
            user1.append(donation)
            donation = ibm_db.fetch_tuple(stmt1)
        print(user1)
        return render_template("data.html",responses= user1, user=User)

@app.route('/Donations',  methods=['POST', 'GET']) 
def Donations():
    print('admin')
    sql = "SELECT * FROM login_table WHERE USERID=" + str(session['USERID'])
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
    User = ibm_db.fetch_tuple(stmt)
    print(User)
    if User[5] == 1:
        sql = "SELECT * FROM LOGIN_TABLE WHERE ROLE=0" 
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.execute(stmt)
        assign = ibm_db.fetch_tuple(stmt)
        print(assign)
        list=[]
        while assign!= False:
            list.append(assign)
            assign = ibm_db.fetch_tuple(stmt)
        print(list)

        sql1="SELECT * FROM donation_table"
        stmt1=ibm_db.prepare(conn, sql1)
        ibm_db.execute(stmt1)
        donation = ibm_db.fetch_tuple(stmt1)
        print(donation)
        user1=[]
        while donation!= False:
            user1.append(donation)
            donation = ibm_db.fetch_tuple(stmt1)
        print(user1)
        return render_template("data_admin.html",user1= list, user=User, rows=user1)

@app.route('/delete_info/<string:USERID>', methods = ['POST'])
def delete_info(USERID):
    # current_user = session["USERID"]
    sql= "DELETE FROM DONATION_TABLE WHERE USERID=?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, USERID)
    ibm_db.execute(stmt)
    print('item deleted')
    return redirect(url_for('Donations'))

@app.route('/update_info/<string:USERID>', methods = ['POST'])
def update_info(USERID):
    if request.method == "POST":

        AGENT_NAME = request.form.get('agent')
        # current_user = session["USERID"]
        update_sql ="UPDATE DONATION_TABLE SET AGENT_NAME =? WHERE USERID =  " + str(USERID)
        stmt = ibm_db.prepare(conn, update_sql)
        ibm_db.bind_param(stmt, 1, AGENT_NAME)
        ibm_db.execute(stmt)
        print('item passing')
        return redirect(url_for('Donations'))    


@app.route('/update_agent/<string:USERID>', methods = ['POST'])
def update_agent(USERID):
    if request.method == "POST":

        DONATION_STATUS = request.form.get('update')
        # current_user = session["USERID"]
        update_sql ="UPDATE DONATION_TABLE SET DONATION_STATUS =? WHERE USERID =  " + str(USERID)
        stmt = ibm_db.prepare(conn, update_sql)
        ibm_db.bind_param(stmt, 1, DONATION_STATUS)
        ibm_db.execute(stmt)
        print('updated')
        return redirect(url_for('Notifications')) 


@app.route('/logout')
def logout():
    return render_template('index.html') 
    
if __name__=='__main__':
    app.run(host='0.0.0.0',debug=True)

    

