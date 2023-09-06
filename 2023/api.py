from flask import Flask, render_template, redirect, request, jsonify
from Model import *

app = Flask(__name__)
app = Flask(__name__, template_folder="templates")

@app.route('/')
def entrada():
    temps = persistencia.query(Temperaturator).all()
    qtd = len(temps)
    return render_template("index.html", count=qtd, temps=temps)

@app.route('/temperaturator/<id>')
def temperaturator(id):
    temp = persistencia.query(Temperaturator).filter_by(id=id).first()
    return render_template("temperaturator.html", temp=temp)

@app.route('/temperaturator/<id>/consume')
def consumetemperaturator(id):
    temp = persistencia.query(Temperaturator).filter_by(id=id).first()
    temperatura = temp.media()
    return jsonify(temperatura)

@app.route('/temperaturator/apagar/<id>', methods=['GET', 'POST'])
def deltemperaturator(id):
    temp = persistencia.query(Temperaturator).filter_by(id=id).first()
    persistencia.delete(temp)
    persistencia.commit()
    return redirect('/')

@app.route('/temperaturator/<id>/endpoint/add', methods=['GET', 'POST'])
def addtemperaturatorendpoint(id):
    url = request.form['url']
    temp = persistencia.query(Temperaturator).filter_by(id=id).first()
    e = EndPoint()
    e.url = url
    e.temperaturator = temp
    persistencia.add(e)
    persistencia.commit()
    return render_template("temperaturator.html", temp=temp)

@app.route('/temperaturator/add', methods=['GET', 'POST'])
def addtemperaturator():
    loc = request.form['local']
    desc = request.form['description']
    t = Temperaturator(local=loc, description=desc)
    persistencia.add(t)
    return redirect('/')

@app.route('/temperaturator/<id>/endpoint/del', methods=['GET', 'POST'])
def deltemperaturatorendpoint(id):
    edpid = request.form['endpointid']
    temp = persistencia.query(Temperaturator).filter_by(id=id).first()
    edp = persistencia.query(EndPoint).filter_by(id=edpid).first()
    persistencia.delete(edp)
    persistencia.commit()
    return render_template("temperaturator.html", temp=temp)

@app.route('/temperaturator/<id>/endpoint/<edpid>/chave/add', methods=['GET', 'POST'])
def addchaveendpoint(id,edpid):
    temp = persistencia.query(Temperaturator).filter_by(id=id).first()
    edp = persistencia.query(EndPoint).filter_by(id=edpid).first()
    chave = request.form['chave']
    edp.newChave(chave)
    persistencia.add_all(edp.chaves)
    persistencia.commit()
    return render_template("temperaturator.html", temp=temp)

if __name__ == "__main__":
    app.run()