from flask import Flask, jsonify,request, render_template, Markup, redirect, url_for
from flask_sqlalchemy import SQLAlchemy


import re
import decodehex2
import definitions
import sys
import os
import Gen2secondgen as Gen2
import Gen2functions
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://aucgczltspqzuw:bb6151174de15689b394ac16680b84ac62b7d507fc51553d3f78117fca3782d2@ec2-54-235-177-183.compute-1.amazonaws.com:5432/d7upsnkmd5nlv1'
#os.environ.get['DATABASE_URL']
db = SQLAlchemy(app)
from models import User
@app.route('/add/')
def webhook():
    name = "ram"
    email = "ram@ram.com"
    u = User(id = 5, nickname = name, email = email)
    print("user created", u)
    db.session.add(u)
    db.session.commit()
    return "user created"

@app.route('/fetch/<username>')
def  fetch(username):
    results=[]
    for user in db.session.query(User).filter_by(nickname='ram'):
        results.append(user)
    return results[0].email


@app.route('/delete/')
def delete():
    u = User.query.get(i)
    db.session.delete(u)
    db.session.commit()
    return "user deleted"

# simple decoder
@app.route('/validatehex', methods=['GET','POST'])
def validatehex():
    ret_data =  str(request.args.get('hexcode')).strip()
    print(ret_data)
    hexaPattern = re.findall(r'([A-F0-9])', ret_data,re.M|re.I)
    statuscheck='not valid'
    message = 'Enter a valid beacon hex message'
    if len(ret_data) > 0:
        if len(hexaPattern)==len(ret_data):

            message='This is a valid hexidecimal message.'
            if len(ret_data) in [15,30,23,63]:
                statuscheck = 'valid'
            else:
                message += '  However, length '+str(len(ret_data)) + ' is not a valid message.  Valid message should be 15,23,30 or 63.'
        else:
            statuscheck='not valid'
            message='Invalid Hexidecimal code.  (A-F-0-9)'


    return jsonify(echostatus=statuscheck, message=message)




@app.route("/",methods=['GET','POST'])
@app.route("/index")
def index():
    if request.method == 'POST':
        hexcode = str(request.form['hexcode'])
        return redirect(url_for('decoded',hexcode=hexcode))
    return render_template('child.html', title='Home', user='')




@app.route("/decoded/<hexcode>")
def decoded(hexcode):
    geocoord=(0,0)
    locationcheck=False
    if len(hexcode) == 63 or len(hexcode) == 51 or len(hexcode) == 75 or len(hexcode) == 23:
        beacon = Gen2.SecondGen(hexcode)
    else:
        beacon = decodehex2.BeaconHex(hexcode)
    beacon.processHex(hexcode)
    print(beacon.has_loc())
    decoded = beacon.tablebin
    if beacon.has_loc():

        geocoord = (float(beacon.location[0]),float(beacon.location[1]))
        locationcheck=True

    return render_template('output.html', hexcode=hexcode, decoded=decoded, locationcheck=locationcheck,geocoord=geocoord)


if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0', port=5555)
