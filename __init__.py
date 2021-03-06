from flask import Flask, flash,jsonify,request, render_template, Markup, redirect, url_for,make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from sgbform import SGB, SGB_g008
from fgbform import FirstGenForm,FirstGenStd,FirstGenRLS, FirstGenELTDT
from longfirstgenmsg import encodelongFGB
from decodefunctions import is_number
import re
import os
import sys
import decodehex2
import definitions
import requests
UPLOAD_FOLDER = ''
ALLOWED_EXTENSIONS = set(['txt'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.secret_key = 'my secret'
try:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
except:
    print('no database')
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://aucgczltspqzuw:bb6151174de15689b394ac16680b84ac62b7d507fc51553d3f78117fca3782d2@ec2-54-235-177-183.compute-1.amazonaws.com:5432/d7upsnkmd5nlv1'
#os.environ.get['DATABASE_URL']
db = SQLAlchemy(app)
from models import User, Types



COUNTRIES=[]
country=open('countries2.csv')
for line in country.readlines():
    COUNTRIES.append(line)
##for key in definitions.countrydic:
##    COUNTRIES.append('{} ({})'.format(definitions.countrydic[key], key))
COUNTRIES.sort()








@app.route('/add/')
def webhook():
    name = 'peter4'
    email = "peter4@ram.com"
    u = User( nickname = name, email = email)
    print("user created", u)
    db.session.add(u)
    db.session.commit()
    return "user created"

@app.route('/fetch/<ident>')
def  fetch(ident):
    results=[]
    for e in db.session.query(Types).filter_by(id=ident):
        results.append(e)
    return str(results[0].name)


@app.route('/delete/')
def delete():
    u = User.query.get(i)
    db.session.delete(u)
    db.session.commit()
    return "user deleted"





@app.route('/processhex', methods=['GET'])
def processhex():
    protocol=str(request.args.get('protocol'))
    t = definitions.protocolspecific[protocol](request.args,protocol)
    retdata = t.getresult()
    beacon_gen = t.getgen()
    return jsonify(beacon_gen=beacon_gen,binary=retdata['binary'],hexcode=retdata['hexcode'],echostatus=retdata['status'], messages=retdata['message'], flderrors=retdata['flderrors'])


@app.route('/filterlist', methods=['GET'])
def filterlist():
    protocol=str(request.args.get('a'))
    beacontype=str(request.args.get('b'))
    print('protocol: '+protocol+' and beacon: '+beacontype)
    selectdic={"---select protocol---":"0"}
    for l in definitions.pselect[protocol][beacontype]:
        selectdic[l[0]]=l[1]
    statuscheck='valid'
    return jsonify(returndata=selectdic,echostatus=statuscheck)


@app.route('/longSGB', methods=['GET','POST'])
def longSGB():
    hexcodeUIN = str(request.args.get('hex_code'))
    error = None

    rotatefld=str(request.args.get('rotatingfield'))
    print(rotatefld,hexcodeUIN)
    forms={'0000': SGB_g008(request.form)}
    form = forms[rotatefld]
    if request.method == 'POST' and form.validate():

        hexcodelong = request.form['homingdevice'] + request.form['selftest'] + request.form['beacontype'] + request.form['testprotocol']
        #hexcodelong = encodelongFGB(hexcodeUIN, lat, latdir, long, longdir, suppdata)
        print(form.encodelong(hexcodeUIN))
        return redirect(url_for('decoded', hexcode=form.encodelong(hexcodeUIN)))

    return render_template('encodelongSGBentryform.html', hexcode=hexcodeUIN, ptype=rotatefld, form=form, error=error)

@app.route('/longfirstgen', methods=['GET','POST'])
def longfirstgen():
    hexcodeUIN = str(request.args.get('hex_code'))
    error = None
    beacon = decodehex2.BeaconFGB(hexcodeUIN)
    ptype = beacon.loctype()
    if ptype == 'National User':
        return redirect(url_for('decoded', hexcode=hexcodeUIN + '0' * 15))

    if beacon.protocolflag()=='User':
        ptype = 'User'

    forms={'User': FirstGenForm(request.form),'Standard Location':FirstGenStd(request.form), 'National Location':FirstGenStd(request.form),'RLS Location':FirstGenRLS(request.form),'ELT-DT Location':FirstGenELTDT(request.form)}
    form = forms[ptype]

    if request.method == 'POST' and form.validate():

        lat = request.form['latitude']
        latdir=request.form['northsouth']
        long = request.form['longitude']
        longdir =request.form['eastwest']
        if ptype == 'User':
            suppdata = request.form['encodepos']

        elif ptype in ['Standard Location', 'National Location']:
            suppdata='1101'+request.form['encodepos'] + request.form['auxdevice']
        elif ptype == 'RLS Location' :
            suppdata = request.form['encodepos'] + \
                       request.form['auxdevice'] + \
                       request.form['rlmtypeone'] + \
                       request.form['rlmtypetwo'] + \
                       request.form['feedbacktype1'] + \
                       request.form['feedbacktype2'] + \
                       request.form['rlsprovider']
        elif ptype == 'ELT-DT Location':
            suppdata = request.form['meansactivation'] + request.form['encodedaltitude']
            if form.data.get('freshness')==True:
                suppdata = suppdata + '11'
            else:
                suppdata = suppdata + '00'

        hexcodelong = encodelongFGB(hexcodeUIN, lat, latdir, long, longdir, suppdata)
        print('hex', hexcodelong)
        return redirect(url_for('decoded', hexcode=hexcodelong))

    return render_template('encodelongfirstentryform.html', hexcode=hexcodeUIN, ptype=ptype, form=form, error=error)

@app.route('/long',methods=['GET'])
def long():

    hexcode=str(request.args.get('hex_code'))
    return redirect(url_for('decoded', hexcode=hexcode))




@app.route('/validatehex', methods=['GET'])
def validatehex():
    ret_data =  str(request.args.get('hexcode')).strip()

    hexaPattern = re.findall(r'([A-F0-9])', ret_data,re.M|re.I)
    statuscheck='not valid'
    message = 'Enter a valid beacon hex message'
    if len(ret_data) > 0:
        if len(hexaPattern)==len(ret_data):
            message='Valid hexidecimal message.'
            if len(ret_data) in [15,30,36,23,51,63]:
                statuscheck = 'valid'
            else:
                message = 'Bad length '+str(len(ret_data)) +  '  Valid lengths: 15 hex, 23 hex, 30, 36,51 or 63 hex'
        else:
            statuscheck='not valid'
            message='Invalid Hexidecimal code  (A-F-0-9)'
    return jsonify(echostatus=statuscheck, message=message)


@app.route("/",methods=['GET','POST'])
@app.route("/index")
def index():
    if request.method == 'POST':
        print('post')
        hexcode = str(request.form['hexcode']).strip()
        return redirect(url_for('decoded',hexcode=hexcode))
    return render_template('indx.html', title='Home', user='')


@app.route("/decode",methods=['GET','POST'])
def decode():
    if request.method == 'POST':
        hexcode = str(request.form['hexcode']).strip()
        return redirect(url_for('decoded',hexcode=hexcode))
    return render_template('decodehex.html', title='Home', user='')


@app.route("/autocomplete",methods=['GET'])
def autocomplete():
    search = request.args.get('q')
    results= [k for k in COUNTRIES if k.upper().startswith(search.upper())]
    return jsonify(matching_results=results)

@app.route("/encodehex")
def encodehex():
    countries=[]
    for key in definitions.countrydic:
        countries.append('{} ({})'.format(definitions.countrydic[key], key))
    countries.sort()
    return render_template("encodehexunique.html", countries=countries)

@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/decodedjson/<hexcode>")
def decodedjson(hexcode):
    # perform independent basic validation of hex code for length and specifications. Basic check
    # that hex code can be decoded.
    # if pass test, then make the beacon object
    beacon = decodehex2.Beacon(hexcode)
    # decode , FGB , SGB and if there is any error, describe errors (eg : BCH errors)
    # if message is valid, then complete the dictionary of all relevant keys.
    if beacon.type=='uin':
        if beacon.gentype=='first':
            tmp = 'FGB unique identifier'
        elif beacon.gentype=='second':
            tmp = 'SGB unique identifier'
    else:
        tmp='long message'
    if beacon.has_loc() and is_number(beacon.location[0]) and is_number(beacon.location[1]):
        geocoord = (float(beacon.location[0]),float(beacon.location[1]))
    else:
        geocoord = (0,0)
    beacondecode= {'type': tmp, 'loc': geocoord}
    return jsonify(beacondecode)




@app.route("/decoded/<hexcode>")
def decoded(hexcode):
    # send POST request to jotforms for logging
    ipaddress=str(request.remote_addr)
    #print(request.remote_addr)

    geocoord = (0, 0)
    locationcheck = False
    beacon = decodehex2.Beacon(hexcode)
    error=''
    if len(beacon.errors)>0 :
        error = ', '.join(beacon.errors)


    
    print(beacon.type=='uin')
    if beacon.type=='uin':
        if beacon.gentype=='first':
            tmp = 'encodelongfirst.html'
            # redirect with the hexcode, beacon type - different inputs depending on type of first gen
        elif beacon.gentype=='second':
            tmp = 'encodelongsecond.html'
        elif beacon.gentype=='secondtruncated':
            tmp = 'output.html'


    else:
        print('default output.html')
        #print(beacon.bchstring)
        tmp='output.html'

    if beacon.has_loc() and is_number(beacon.location[0]) and is_number(beacon.location[1]):
        geocoord = (float(beacon.location[0]),float(beacon.location[1]))
        print(geocoord)
        locationcheck=True

    return render_template(tmp, hexcode=hexcode.upper(), decoded=beacon.tablebin, locationcheck=locationcheck,geocoord=geocoord, genmsg=beacon.genmsg)

@app.route("/bch/<hexcode>")
def download_bch(hexcode):
    beacon = decodehex2.Beacon(hexcode)
    bchout=beacon.bchstring
    response = make_response(bchout)
    cd = 'attachment; filename=mybch.txt'
    response.headers['Content-Disposition'] = cd
    response.mimetype = 'text/csv'
    return response

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route('/batch', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            text = open(filename, 'r+')
            content = text.read()
            text.close()
            hexlist=['004D24053C05B00E2932550000000000007FFFC171EA1D91901ABC06772DC50','A5BD01349FC3E0FA5BD01349FC3E0F']
            return render_template('content.html', text=content,results=hexlist)

    return redirect(url_for('decode'))

if __name__ == "__main__":
    app.secret_key = 'my secret'
    app.run(debug=True,host='0.0.0.0', port=5555)
