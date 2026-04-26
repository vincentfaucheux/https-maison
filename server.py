from flask import Flask, render_template, request
from typing import Any
from data2json import write_json2file, read_string2fulljson, read_string2partialjson
from pipes_exchanges import init_pipes, end_pipes, send_request_on_pipe
import threading
import time

app = Flask(__name__)

RADIATEUR_CONFIGS = {
    "Maison": {
        "Etage_0": {
            "Radiateur_1": { 
                "Nom": "Radiateur Salle", 
                "Groupe": "Pièces a vivre", 
                "X": "70", 
                "Y": "200", 
                "Width": "30", 
                "Height": "10"
            },
            "Radiateur_2": { 
                "Nom": "Radiateur Salon", 
                "Groupe": "Pièces a vivre",
                "X": "325", 
                "Y": "50", 
                "Width": "30", 
                "Height": "10"
            },
            "Radiateur_3": { 
                "Nom": "Radiateur Salle mur cuisine", 
                "Groupe": "Pièces a vivre",
                "X": "200", 
                "Y": "390", 
                "Width": "30", 
                "Height": "10"
            },
            "Radiateur_4": { 
                "Nom": "Radiateur Cuisine", 
                "Groupe": "Pièces a vivre",
                "X": "240", 
                "Y": "410", 
                "Width": "10", 
                "Height": "30"
            },
            "Radiateur_5": { 
                "Nom": "Radiateur Entree", 
                "Groupe": "Pièces a vivre",
                "X": "315", 
                "Y": "500", 
                "Width": "10", 
                "Height": "30"
            },
            "Radiateur_6": { 
                "Nom": "Radiateur Salle de bain", 
                "Groupe": "Salle de bain",
                "X": "540", 
                "Y": "325", 
                "Width": "10", 
                "Height": "30"
            },
            "Radiateur_7": { 
                "Nom": "Radiateur Chambre", 
                "Groupe": "Chambre",
                "X": "500", 
                "Y": "50", 
                "Width": "30", 
                "Height": "10"
            },
        }
    }
}

PIECE_CONFIGS = {
    "Maison": {
        "Etage_0": {
            "Piece_1": {  
                "X":"150",
                "Y":"300",
                "Nom": "Pièces a vivre"
            },
            "Piece_2":  {
                "X":"130",
                "Y":"475",
                "Nom": "Cuisine"
            },
            "Piece_3":  {
                "X":"430",
                "Y":"200",
                "Nom": "Chambre"
            },
            "Piece_4":  {
                "X":"430",
                "Y":"335",
                "Nom": "Salle de bain"
            }
        }
    }
}

RADIATEURS_DATA_INIT = {
    "Maison": {
        "Etage_0": {
            "Mode": {
                "Radiateur_1": 1,  # 0=RADIATEUR_STATESoff, 1=conf, 2=eco, 3=hors gel
                "Radiateur_2": 1,
                "Radiateur_3": 1,
                "Radiateur_4": 1,
                "Radiateur_5": 1,
                "Radiateur_6": 1,
                "Radiateur_7": 1,
            },
            "Force": {
                "Radiateur_1": { "Heure": 0, "Minute": 0 }, 
                "Radiateur_2": { "Heure": 0, "Minute": 0 }, 
                "Radiateur_3": { "Heure": 0, "Minute": 0 }, 
                "Radiateur_4": { "Heure": 0, "Minute": 0 }, 
                "Radiateur_5": { "Heure": 0, "Minute": 0 }, 
                "Radiateur_6": { "Heure": 0, "Minute": 0 }, 
                "Radiateur_7": { "Heure": 0, "Minute": 0 }, 
            },
            "Schedule": {
                "Radiateur_1": {
                    "Lundi": [
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
                "Radiateur_2": {
                    "Lundi": [
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
                "Radiateur_3": {
                    "Lundi": [
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
                "Radiateur_4": {
                    "Lundi": [
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
                "Radiateur_5": {
                    "Lundi": [
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
                "Radiateur_6": {
                    "Lundi": [
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
                "Radiateur_7": {
                    "Lundi": [
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
        }
    }
}

RADIATEURS_DATA = {
}

html_list_groundfloor = { "Radiateurs": [], "Pieces": [] }

lock = threading.Lock()
end_pipes_exchanges = False

def init_html_list_groundfloor_pieces():
    global html_list_groundfloor
    html_list_groundfloor = { "Radiateurs": [], "Pieces": [] }
    for id, piece_data in PIECE_CONFIGS["Maison"]["Etage_0"].items():
        piece_data = piece_data.copy()
        piece_data['Id'] = id
        html_list_groundfloor["Pieces"].append(piece_data)

def updage_groundfloor_radiateurs():
    global RADIATEURS_DATA
    global html_list_groundfloor
    html_list_groundfloor ["Radiateurs"].clear()
    # build the list for HTML
    for id, radiateur_data in RADIATEUR_CONFIGS["Maison"]["Etage_0"].items():
        radiateur_data = radiateur_data.copy()
        radiateur_data['Id'] = id
        radiateur_data['Mode'] = RADIATEURS_DATA["Maison"]["Etage_0"]['Mode'][id]
        radiateur_data['Force'] = RADIATEURS_DATA["Maison"]["Etage_0"]['Force'][id]
        # Example schedule
        radiateur_data['Schedule'] = RADIATEURS_DATA["Maison"]["Etage_0"]['Schedule'][id]
        html_list_groundfloor["Radiateurs"].append(radiateur_data)

def pipe_exchanges():
    global RADIATEURS_DATA
    # échange initial, etats, force et schedule, pour tous les radiateurs
    with lock:
        respons =send_request_on_pipe( 1, 255, 255, "")
    print("response ", respons)
    retcode, msg = read_string2fulljson(respons, RADIATEURS_DATA)
    if retcode != 0:
        print( msg)
        #print("JSON invalide, reinitialisation des donnees")
        #RADIATEURS_DATA = RADIATEURS_DATA_INIT.copy()
    print("keys RADIATEURS_DATA ", RADIATEURS_DATA.keys())
    print("keys RADIATEURS_DATA['Maison'] ", RADIATEURS_DATA["Maison"].keys())
    updage_groundfloor_radiateurs()

    time.sleep( 1)

    while end_pipes_exchanges == False:
        # échanges périodiques, etats et force, pour tous les radiateurs
        with lock:
            respons =send_request_on_pipe( 1, 255, 3, "")
        print("response ", respons)
        retcode, msg = read_string2partialjson(respons, RADIATEURS_DATA)
        if retcode != 0:
            print( msg)
        print("keys RADIATEURS_DATA ", RADIATEURS_DATA.keys())
        print("keys RADIATEURS_DATA['Maison'] ", RADIATEURS_DATA["Maison"].keys())
        updage_groundfloor_radiateurs()
        time.sleep( 20)

@app.route('/')
def accueil():
    global RADIATEURS_DATA
    # read the data from file
    # retcode, msg = read_file2json(RADIATEURS_DATA)
    #if retcode != 0:
    #    if retcode == -2:
    #        print("JSON invalide, reinitialisation des donnees")
    #    RADIATEURS_DATA = RADIATEURS_DATA_INIT.copy()
    print("keys RADIATEURS_DATA ", RADIATEURS_DATA.keys())
    print("keys RADIATEURS_DATA['Maison'] ", RADIATEURS_DATA["Maison"].keys())

    return render_template('index.html')


@app.route('/rezdechausse')
def rezdechausse():
#    global RADIATEURS_DATA
    global html_list_groundfloor
    # # build the list for HTML
    # for id, radiateur_data in RADIATEUR_CONFIGS["Maison"]["Etage_0"].items():
    #     radiateur_data = radiateur_data.copy()
    #     radiateur_data['Id'] = id
    #     radiateur_data['Mode'] = RADIATEURS_DATA['Mode'][id]
    #     radiateur_data['Force'] = RADIATEURS_DATA['Force'][id]
    #     # Example schedule
    #     radiateur_data['Schedule'] = RADIATEURS_DATA['Schedule'][id]
    #     html_list_groundfloor["Radiateurs"].append(radiateur_data)

    # for id, piece_data in PIECE_CONFIGS["Maison"]["Etage_0"].items():
    #     piece_data = piece_data.copy()
    #     piece_data['Id'] = id
    #     html_list_groundfloor["Pieces"].append(piece_data)

    return render_template('RezDeChausse.html', radiateurs=html_list_groundfloor["Radiateurs"], pieces=html_list_groundfloor["Pieces"])


@app.route('/radiateur/<radiateur_id>/set-NewRadiateurState', methods=["POST"])
def set_new_radiateurstate(radiateur_id: str):
    global RADIATEURS_DATA
    # get the parameter
    new_state = request.json.get("state")
    force_heure = request.json.get("forceheure")
    force_minute = request.json.get("forceminute")

    # save the new state to the RadiateurState list
    RADIATEURS_DATA["Maison"]["Etage_0"]["Mode"][radiateur_id] = new_state
    RADIATEURS_DATA["Maison"]["Etage_0"]["Force"][radiateur_id] = { 
        "Heure": force_heure,
        "Minute": force_minute
    }

    # write to file
    write_json2file(RADIATEURS_DATA)

    return {"status": "success", "state": new_state}, 200


@app.route('/piece/<piece_id>/set-NewGroupeState', methods=["POST"])
def set_new_piece_state(piece_id: str):
    global RADIATEURS_DATA
    # get the parameter
    new_state = request.json.get("state")
    force_heure = request.json.get("forceheure")
    force_minute = request.json.get("forceminute")

    # update all radiateurs in the piece
    NomPiece = PIECE_CONFIGS[piece_id]["Nom"]
    for id, radiateur_data in RADIATEUR_CONFIGS.items():
        if radiateur_data["Groupe"] == NomPiece:
            RADIATEURS_DATA["Maison"]["Etage_0"]["Mode"][id] = new_state
            RADIATEURS_DATA["Maison"]["Etage_0"]["Force"][id] = { 
                "Heure": force_heure,
                "Minute": force_minute
            }

    # write to file
    write_json2file(RADIATEURS_DATA)

    return {"status": "success", "state": new_state}, 200


@app.route('/radiateur/<radiateur_id>/set-NewRadiateurConfig', methods=["POST"])
def set_new_radiateurconfig(radiateur_id: str):
    global RADIATEURS_DATA
    # get the parameter
    RadSchedule = request.json.get("DayConfigs")

    # save the new state to the RadiateurState list
    RADIATEURS_DATA["Maison"]["Etage_0"]["Schedule"][radiateur_id] = RadSchedule

    # write to file
    write_json2file(RADIATEURS_DATA)

    return {"status": "success", "state": "1"}, 200


@app.route('/piece/<piece_id>/set-NewGroupeConfig', methods=["POST"])
def set_new_piececonfig(piece_id: str):
    global RADIATEURS_DATA
    # get the parameter
    PieceSchedule = request.json.get("DayConfigs")

    # update all radiateurs in the piece
    NomPiece = PIECE_CONFIGS[piece_id]["Nom"]
    for id, radiateur_data in RADIATEUR_CONFIGS.items():
        if radiateur_data["Groupe"] == NomPiece:
            RADIATEURS_DATA["Maison"]["Etage_0"]["Schedule"][id] = PieceSchedule

    # write to file
    write_json2file(RADIATEURS_DATA)

    return {"status": "success", "state": "1"}, 200


if __name__ == '__main__':
    # initialisation des tubes d'échange
    init_pipes()
    time.sleep( 2)

    #
    # initialisation de la liste pour HTML
    #
    init_html_list_groundfloor_pieces()

    # start the thread for pipe exchanges
    t = threading.Thread(target=pipe_exchanges)
    t.daemon = True
    t.start()
    time.sleep( 2)

    #
    # boucle avant arrêt du serveurl
    #
    # bQuit = False
    # while( bQuit == False ):
    #     str_input = input("Appuyer sur Q pour quitter ")
    #     if(( str_input == "Q" ) or ( str_input == "q" )):
    #         bQuit = True

    app.run(host='192.168.1.34',
            ssl_context=(
                '/home/vincent-pi4/zigbee/server/LocalRsaKey/domoserv+2.pem', 
                '/home/vincent-pi4/zigbee/server/LocalRsaKey/domoserv+2-key.pem'), 
            port=8443, debug=False)

    #
    # Tout fermer   
    #
    end_pipes_exchanges = True
    t.join()
    end_pipes()


# en java script pour dedemander les nouvelles données
#-------------------------------------------------------
#setInterval(() => {
#    fetch("/data")
#        .then(r => r.json())
#        .then(data => {
#            document.body.innerText = JSON.stringify(data);
#        });
#}, 2000);