# python -m venv env -->pta nhi kyu kikha check krege 

from flask import Flask,render_template,redirect,url_for,flash,request, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField,IntegerField,SelectField,SubmitField
from wtforms.validators import DataRequired, Email, EqualTo ,optional
from flask_mysqldb import MySQL
import json

createGuestQuary = """create table if not exists guest_register (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                                                              firstName TEXT, 
                                                              lastName TEXT,
                                                              username TEXT,
                                                              email TEXT,
                                                              address TEXT,
                                                              guests INT)"""

 
insertIntoTable= """ INSERT INTO guest_register (firstName,lastName,username,email,address,guests)
                                       VALUES ('{}','{}','{}','{}','{}','{}')"""
username_email_exits="""  SELECT CASE 
                       WHEN EXISTS (
                                   SELECT 1 
                                   FROM guest_register 
                                    WHERE username = '{}' OR email = '{}'
                                    ) THEN 'Exist'
                            ELSE 'NotExist'
                        END AS result"""
readPropertyQuary=" select JSON_ARRAYAGG(json_object('srcImg',srcImg,'title',title,'description',description,'price',price)) from propertydata;"


app = Flask(__name__)



app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'kakukaku'
app.config['MYSQL_DB'] = 'hotel_app'
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['WTF_CSRF_ENABLED'] = True
 
mysql = MySQL(app)



class RegisterForm(FlaskForm):
     firstName=StringField("First name",validators=[DataRequired()])
     lastName=StringField("Last name",validators=[DataRequired()])
     Username=StringField("Username",validators=[DataRequired()])
     email=StringField("email",validators=[DataRequired()])
     address=StringField("Address",validators=[optional()])
     numberOfGuest=SelectField("number of guest",choices=[1,2,3,4,5,6,7,8],validators=[DataRequired()])
     submit= SubmitField("submit")
     error_fileds=""

class statusRegis():
     status = False
     errorMsg = ""
     successMsg=" you booking has been register , when booking will be confirmed we will update you"
     



def sqlfunction(action,read):
     if read==True:
         
         cur = mysql.connection.cursor()

         cur.execute(action)

         mysql.connection.commit()  

         data= cur.fetchall()
         cur.close()
         return data

                
         
   
     else:
        cur = mysql.connection.cursor()

        cur.execute(action)

        mysql.connection.commit()
    
        cur.close()




@app.route('/')
def home():

    return render_template('home.html')



@app.route('/info',methods=['GET','POST'])
def info():
    sqlfunction(createGuestQuary,False)
   
   
    form = RegisterForm()
    
    
    if form.validate_on_submit():
        print("form get valided")
        fname=form.firstName.data
        lname=form.lastName.data
        username=form.Username.data
        email=form.email.data
        add =form.address.data
        noOfGuest = form.numberOfGuest.data

        data= sqlfunction(username_email_exits.format(username,email),True)

        print(data[0][0])

        if data[0][0]=='Exist':
            print("email or username exist")
            statusRegis.status=False
            statusRegis.errorMsg = "this  email or username already taken"
            return redirect(url_for('statusOfRegis'))
        else:
            sqlfunction(insertIntoTable.format(fname,lname,username,email,add,noOfGuest),False)
            statusRegis.status=True
            statusRegis.successMsg=" congratulations {} {} {} number of guest has been booked for given hotel on the username of {} and {} email is registered ".format(fname,lname,noOfGuest,username,email)
            return redirect(url_for('statusOfRegis'))
    
    else:
    # Check each field for errors and print them or handle accordingly
     for field_name,error_messages in form.errors.items():
        for message in error_messages:
         flash(f"Error in {field_name}: {message}", 'error')
            
    

    return render_template('info.html' ,form=form)



@app.route('/booking')
def booking():
    return render_template('bookings.html')


@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/statusOfReg')
def statusOfRegis():
    return render_template('statusRegis.html',statusRegis=statusRegis)

@app.route('/dataProperties',methods=['GET'])
def addProperties():
     data = sqlfunction(readPropertyQuary,True)
    #  print("mee",data[0][0][0])
    #  columns = [column[0] for column in cursor.description] 
     return data[0][0]


@app.route('/seletedHotel',methods=['GET','POST'])
def seletedHotel():
      data = request.get_json()
      print(data)
      return jsonify({'status': 'success', 'data_received': data})

if __name__ == '__main__':
    app.run(debug=True)

