from flask import Flask, render_template
from typing import Any
app = Flask(__name__)

radiateurs : list[dict[str,Any]] = [
    {"id": 1, "nom": "Salle", "x": "70", "y": "200", "width": "30", "height": "10", "temp": 19.0},
    {"id": 2, "nom": "Salon", "x": "325", "y": "50", "width": "30", "height": "10", "temp": 20.0},
    {"id": 3, "nom": "Salle cuisine", "x": "200", "y": "390", "width": "30", "height": "10", "temp": 21.0},
    {"id": 4, "nom": "Cuisine", "x": "240", "y": "410", "width": "10", "height": "30", "temp": 22.0},
    {"id": 5, "nom": "Entree", "x": "315", "y": "500", "width": "10", "height": "30", "temp": 23.0},
    {"id": 6, "nom": "Salle de bain", "x": "540", "y": "325", "width": "10", "height": "30", "temp": 24.0},
    {"id": 7, "nom": "Chambre", "x": "500", "y": "50", "width": "30", "height": "10", "temp": 24.0},
]



@app.route('/')

def accueil():
    return render_template('index.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/rezdechausse')
def rezdechausse():
    _radiateurs = radiateurs.copy()

    # fetch command temp from other service
    _radiateurs[0].update(
        state="conf",
        schedule = [
            ("07:00", "conf"),
            ("23:00", "eco")
        ]
    )

    return render_template('RezDeChausse.html', radiateurs=_radiateurs)

@app.route('/radiateur/<radiateur_id>/set-temperature', methods=["POST"])
def set_temperature(radiateur_id: int):
    # set radiateur temparature with other service

    return "ok"


if __name__ == '__main__':
    app.run(host='192.168.1.33',
            ssl_context=('../LocalRsaKey/domoserv+2.pem', '../LocalRsaKey/domoserv+2-key.pem'), 
            port=8443)
