from flask import Flask, render_template, request
from typing import Any

app = Flask(__name__)

RADIATEUR_CONFIGS : dict[int, dict[str,Any]] = {
    1: { "nom": "Salle", "x": "70", "y": "200", "width": "30", "height": "10"},
    2: { "nom": "Salon", "x": "325", "y": "50", "width": "30", "height": "10"},
    3: { "nom": "Salle cuisine", "x": "200", "y": "390", "width": "30", "height": "10"},
    4: { "nom": "Cuisine", "x": "240", "y": "410", "width": "10", "height": "30"},
    5: { "nom": "Entree", "x": "315", "y": "500", "width": "10", "height": "30"},
    6: { "nom": "Salle de bain", "x": "540", "y": "325", "width": "10", "height": "30"},
    7: { "nom": "Chambre", "x": "500", "y": "50", "width": "30", "height": "10"},
}

RADIATEUR_STATES = {
    1: 1,  # 0=off, 1=conf, 2=eco, 3=hors gel
    2: 1,
    3: 1,
    4: 1,
    5: 1,
    6: 1,
    7: 1,
}


@app.route('/')

def accueil():
    return render_template('index.html')


@app.route('/rezdechausse')
def rezdechausse():

    # build the list for HTML
    resp_list = []
    for id, radiateur_data in RADIATEUR_CONFIGS.items():
        radiateur_data = radiateur_data.copy()
        radiateur_data['id'] = id
        radiateur_data['state'] = RADIATEUR_STATES[id]
        radiateur_data['schedule'] = [
            ("07:00", "conf"),
            ("23:00", "eco")
        ]
        resp_list.append(radiateur_data)

    return render_template('RezDeChausse.html', radiateurs=resp_list)


@app.route('/radiateur/<radiateur_id>/set-NewState', methods=["POST"])
def set_new_state(radiateur_id: str):
    # get the parameter
    new_state = request.json.get("state")

    # save the new state to the RadiateurState list
    RADIATEUR_STATES[int(radiateur_id)] = new_state

    return {"status": "success", "state": new_state}, 200


if __name__ == '__main__':
    app.run(host='192.168.1.33',
            ssl_context=('../LocalRsaKey/domoserv+2.pem', '../LocalRsaKey/domoserv+2-key.pem'), 
            port=8443)
