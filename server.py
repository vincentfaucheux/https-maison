from flask import Flask, render_template, request
from typing import Any

app = Flask(__name__)

RADIATEUR_CONFIGS : dict[int, dict[str,Any]] = {
    1: { "nom": "Radiateur Salle", 
         "groupe": "Pièces a vivre", 
         "x": "70", 
         "y": "200", 
         "width": "30", 
         "height": "10"
        },
    2: { "nom": "Radiateur Salon", 
         "groupe": "Pièces a vivre",
         "x": "325", 
         "y": "50", 
         "width": "30", 
         "height": "10"
        },
    3: { "nom": "Radiateur Salle mur cuisine", 
         "groupe": "Pièces a vivre",
         "x": "200", 
         "y": "390", 
         "width": "30", 
         "height": "10"
        },
    4: { "nom": "Radiateur Cuisine", 
         "groupe": "Pièces a vivre",
         "x": "240", 
         "y": "410", 
         "width": "10", 
         "height": "30"
        },
    5: { "nom": "Radiateur Entree", 
         "groupe": "Pièces a vivre",
         "x": "315", 
         "y": "500", 
         "width": "10", 
         "height": "30"
        },
    6: { "nom": "Radiateur Salle de bain", 
         "groupe": "Salle de bain",
         "x": "540", 
         "y": "325", 
         "width": "10", 
         "height": "30"
        },
    7: { "nom": "Radiateur Chambre", 
         "groupe": "Chambre",
         "x": "500", 
         "y": "50", 
         "width": "30", 
         "height": "10"
        },
}

PIECE_CONFIGS = {
    1: {  "x":"150",
          "y":"300",
          "nom": "Pièces a vivre"
        },
    2:  {
          "x":"130",
          "y":"475",
          "nom": "Cuisine"
        },
    3:  {
          "x":"430",
          "y":"200",
          "nom": "Chambre"
        },
    4:  {
          "x":"430",
          "y":"335",
          "nom": "Salle de bain"
        }
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

RADIATEUR_TIME_FORCE = {
    1: { "heure": 0, "minute": 0 }, 
    2: { "heure": 0, "minute": 0 }, 
    3: { "heure": 0, "minute": 0 }, 
    4: { "heure": 0, "minute": 0 }, 
    5: { "heure": 0, "minute": 0 }, 
    6: { "heure": 0, "minute": 0 }, 
    7: { "heure": 0, "minute": 0 }, 
}

RADIATEUR_SCHEDULE = {
    1: {
        "Lundi": [
        { "heure": 7, "minute": 0, "mode": 1},
        { "heure": 23, "minute": 0, "mode": 2}
        ],
        "Mardi": [
        ],
        "Mercredi": [
        ],
        "Jeudi": [
        ],  
        "Vendredi": [
        ],
        "Samedi": [
        ],
        "Dimanche": [
        ]   
    },
    2: {
        "Lundi": [
        { "heure": 7, "minute": 0, "mode": 1},
        { "heure": 23, "minute": 0, "mode": 2}
        ],
        "Mardi": [
        ],
        "Mercredi": [
        ],
        "Jeudi": [
        ],  
        "Vendredi": [
        ],
        "Samedi": [
        ],
        "Dimanche": [
        ]   
    },
    3: {
        "Lundi": [
        { "heure": 7, "minute": 0, "mode": 1},
        { "heure": 23, "minute": 0, "mode": 2}
        ],
        "Mardi": [
        ],
        "Mercredi": [
        ],
        "Jeudi": [
        ],  
        "Vendredi": [
        ],
        "Samedi": [
        ],
        "Dimanche": [
        ]   
    },
    4: {
        "Lundi": [
        { "heure": 7, "minute": 0, "mode": 1},
        { "heure": 23, "minute": 0, "mode": 2}
        ],
        "Mardi": [
        ],
        "Mercredi": [
        ],
        "Jeudi": [
        ],  
        "Vendredi": [
        ],
        "Samedi": [
        ],
        "Dimanche": [
        ]   
    },
    5: {
        "Lundi": [
        { "heure": 7, "minute": 0, "mode": 1},
        { "heure": 23, "minute": 0, "mode": 2}
        ],
        "Mardi": [
        ],
        "Mercredi": [
        ],
        "Jeudi": [
        ],  
        "Vendredi": [
        ],
        "Samedi": [
        ],
        "Dimanche": [
        ]   
    },
    6: {
        "Lundi": [
        { "heure": 7, "minute": 0, "mode": 1},
        { "heure": 23, "minute": 0, "mode": 2}
        ],
        "Mardi": [
        ],
        "Mercredi": [
        ],
        "Jeudi": [
        ],  
        "Vendredi": [
        ],
        "Samedi": [
        ],
        "Dimanche": [
        ]   
    },
    7: {
        "Lundi": [
        { "heure": 7, "minute": 0, "mode": 1},
        { "heure": 23, "minute": 0, "mode": 2}
        ],
        "Mardi": [
        ],
        "Mercredi": [
        ],
        "Jeudi": [
        ],  
        "Vendredi": [
        ],
        "Samedi": [
        ],
        "Dimanche": [
        ]   
    },
}


@app.route('/')

def accueil():
    return render_template('index.html')


@app.route('/rezdechausse')
def rezdechausse():

    # build the list for HTML
    html_list = { "radiateurs": [], "pieces": [] }
    for id, radiateur_data in RADIATEUR_CONFIGS.items():
        radiateur_data = radiateur_data.copy()
        radiateur_data['id'] = id
        radiateur_data['state'] = RADIATEUR_STATES[id]
        radiateur_data['timeforce'] = RADIATEUR_TIME_FORCE[id]
        # Example schedule
        radiateur_data['schedule'] = RADIATEUR_SCHEDULE[id]
        html_list["radiateurs"].append(radiateur_data)

    for id, piece_data in PIECE_CONFIGS.items():
        piece_data = piece_data.copy()
        piece_data['id'] = id
        html_list["pieces"].append(piece_data)

    return render_template('RezDeChausse.html', radiateurs=html_list["radiateurs"], pieces=html_list["pieces"])


@app.route('/radiateur/<radiateur_id>/set-NewRadiateurState', methods=["POST"])
def set_new_radiateurstate(radiateur_id: str):
    # get the parameter
    new_state = request.json.get("state")
    force_heure = request.json.get("forceheure")
    force_minute = request.json.get("forceminute")

    # save the new state to the RadiateurState list
    RADIATEUR_STATES[int(radiateur_id)] = new_state
    RADIATEUR_TIME_FORCE[int(radiateur_id)] = { 
        "heure": force_heure,
        "minute": force_minute
    }
    return {"status": "success", "state": new_state}, 200


@app.route('/piece/<piece_id>/set-NewGroupeState', methods=["POST"])
def set_new_piece_state(piece_id: str):
    # get the parameter
    new_state = request.json.get("state")
    force_heure = request.json.get("forceheure")
    force_minute = request.json.get("forceminute")

    # update all radiateurs in the piece
    NomPiece = PIECE_CONFIGS[int(piece_id)]["nom"]
    for id, radiateur_data in RADIATEUR_CONFIGS.items():
        if radiateur_data["groupe"] == NomPiece:
            RADIATEUR_STATES[id] = new_state
            RADIATEUR_TIME_FORCE[id] = { 
                "heure": force_heure,
                "minute": force_minute
            }
    return {"status": "success", "state": new_state}, 200


if __name__ == '__main__':
    app.run(host='192.168.1.33',
            ssl_context=('../LocalRsaKey/domoserv+2.pem', '../LocalRsaKey/domoserv+2-key.pem'), 
            port=8443)
