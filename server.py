from flask import Flask, render_template, request
from flask import jsonify
from typing import Any
from data2json import write_json2file, read_string2fulljson, read_string2partialjson, write_json2string
from pipes_exchanges import init_pipes, end_pipes, send_request_on_pipe
from pathlib import Path
import yaml
import sys
import threading
import time
import mylog

app = Flask(__name__)

HEATER_CONFIGS = {
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
                "Nom": "Radiateur Chambre", 
                "Groupe": "Chambre",
                "X": "500", 
                "Y": "50", 
                "Width": "30", 
                "Height": "10"
            },
        },
        "Etage_1": {
            "Radiateur_10": { 
                "Nom": "Radiateur Martin", 
                "Groupe": "Chambres étage", 
                "X": "400", 
                "Y": "50", 
                "Width": "30", 
                "Height": "10"
            },
            "Radiateur_11": { 
                "Nom": "Radiateur Justin", 
                "Groupe": "Chambres étage",
                "X": "400", 
                "Y": "540", 
                "Width": "30", 
                "Height": "10"
            },
            "Radiateur_12": { 
                "Nom": "Radiateur Charlie", 
                "Groupe": "Chambres étage",
                "X": "150", 
                "Y": "540", 
                "Width": "30", 
                "Height": "10"
            }
        }
    }
}

GROUP_CONFIGS = {
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
            }
        },
        "Etage_1": {
            "Piece_10": {  
                "X":"280",
                "Y":"350",
                "Nom": "Chambres étage"
            }
        }
    }
}


HEATERS_DATA_INIT = {
    "Maison": {
        "Etage_0": {
            "Mode": {
                "Radiateur_1": 1,  # 0=RADIATEUR_STATESoff, 1=conf, 2=eco, 3=hors gel
                "Radiateur_2": 1,
                "Radiateur_3": 1,
                "Radiateur_4": 1,
                "Radiateur_5": 1,
                "Radiateur_6": 1,
            },
            "Force": {
                "Radiateur_1": { "Heure": 0, "Minute": 0, "Mode": 1 }, 
                "Radiateur_2": { "Heure": 0, "Minute": 0, "Mode": 1 }, 
                "Radiateur_3": { "Heure": 0, "Minute": 0, "Mode": 1 }, 
                "Radiateur_4": { "Heure": 0, "Minute": 0, "Mode": 1 }, 
                "Radiateur_5": { "Heure": 0, "Minute": 0, "Mode": 1 }, 
                "Radiateur_6": { "Heure": 0, "Minute": 0, "Mode": 1 }, 
            },
            "Schedule": {
                "Radiateur_1": {
                    "Lundi": [],
                    "Mardi": [],
                    "Mercredi": [],
                    "Jeudi": [],  
                    "Vendredi": [],
                    "Samedi": [],
                    "Dimanche": []   
                },
                "Radiateur_2": {
                    "Lundi": [],
                    "Mardi": [],
                    "Mercredi": [],
                    "Jeudi": [],  
                    "Vendredi": [],
                    "Samedi": [],
                    "Dimanche": []   
                },
                "Radiateur_3": {
                    "Lundi": [],
                    "Mardi": [],
                    "Mercredi": [],
                    "Jeudi": [],  
                    "Vendredi": [],
                    "Samedi": [],
                    "Dimanche": []   
                },
                "Radiateur_4": {
                    "Lundi": [],
                    "Mardi": [],
                    "Mercredi": [],
                    "Jeudi": [],  
                    "Vendredi": [],
                    "Samedi": [],
                    "Dimanche": []   
                },
                "Radiateur_5": {
                    "Lundi": [],
                    "Mardi": [],
                    "Mercredi": [],
                    "Jeudi": [],  
                    "Vendredi": [],
                    "Samedi": [],
                    "Dimanche": []   
                },
                "Radiateur_6": {
                    "Lundi": [],
                    "Mardi": [],
                    "Mercredi": [],
                    "Jeudi": [],  
                    "Vendredi": [],
                    "Samedi": [],
                    "Dimanche": []   
                },
            }
        },
        "Etage_1": {
            "Mode": {
                "Radiateur_10": 1,  # 0=RADIATEUR_STATESoff, 1=conf, 2=eco, 3=hors gel
                "Radiateur_11": 1,
                "Radiateur_12": 1
            },
            "Force": {
                "Radiateur_10": { "Heure": 0, "Minute": 0, "Mode": 1 }, 
                "Radiateur_11": { "Heure": 0, "Minute": 0, "Mode": 1 }, 
                "Radiateur_12": { "Heure": 0, "Minute": 0, "Mode": 1 } 
            },
            "Schedule": {
                "Radiateur_10": {
                    "Lundi": [],
                    "Mardi": [],
                    "Mercredi": [],
                    "Jeudi": [],  
                    "Vendredi": [],
                    "Samedi": [],
                    "Dimanche": []   
                },
                "Radiateur_11": {
                    "Lundi": [],
                    "Mardi": [],
                    "Mercredi": [],
                    "Jeudi": [],  
                    "Vendredi": [],
                    "Samedi": [],
                    "Dimanche": []   
                },
                "Radiateur_12": {
                    "Lundi": [],
                    "Mardi": [],
                    "Mercredi": [],
                    "Jeudi": [],  
                    "Vendredi": [],
                    "Samedi": [],
                    "Dimanche": []   
                }
            }
        }
    }
}

HEATERS_DATA = {
}

html_list_groundfloor = { "Heaters": [], "Groups": [] }
html_list_firstfloor = { "Heaters": [], "Groups": [] }

lock = threading.Lock()
end_pipes_exchanges = False
serv2main_dictionary = {}
serv2main_msg = ""
serv2main_trigger = False
config = None

def init_html_list_groundfloor_groups():
    global html_list_groundfloor
    html_list_groundfloor = { "Heaters": [], "Groups": [] }
    for id, piece_data in GROUP_CONFIGS["Maison"]["Etage_0"].items():
        piece_data = piece_data.copy()
        piece_data['Id'] = id
        html_list_groundfloor["Groups"].append(piece_data)

def init_html_list_firstfloor_groups():
    global html_list_firstfloor
    html_list_firstfloor = { "Heaters": [], "Groups": [] }
    for id, piece_data in GROUP_CONFIGS["Maison"]["Etage_1"].items():
        piece_data = piece_data.copy()
        piece_data['Id'] = id
        html_list_firstfloor["Groups"].append(piece_data)

def update_main_app( floor, action, heaters):
    global serv2main_dictionary
    global HEATERS_DATA
    global serv2main_trigger
    global lock
    global serv2main_msg
    values = {}
    for heater in heaters: 
        values[heater] = HEATERS_DATA["Maison"][floor][action][heater]
    path = [ "Maison", floor, action ]
    for key in reversed(path):
        values = { key: values }
    serv2main_dictionary = values
    with lock:
        retcode, msg = write_json2string(serv2main_dictionary)
        if retcode != 0:
            print( msg)
            return
        serv2main_msg = msg
        serv2main_trigger = True

def updage_groundfloor_heaters():
    global HEATERS_DATA
    global html_list_groundfloor
    html_list_groundfloor ["Heaters"].clear()
    # build the list for HTML
    for id, radiateur_data in HEATER_CONFIGS["Maison"]["Etage_0"].items():
        radiateur_data = radiateur_data.copy()
        radiateur_data['Id'] = id
        radiateur_data['Mode'] = HEATERS_DATA["Maison"]["Etage_0"]['Mode'][id]
        radiateur_data['Force'] = HEATERS_DATA["Maison"]["Etage_0"]['Force'][id]
        # Example schedule
        radiateur_data['Schedule'] = HEATERS_DATA["Maison"]["Etage_0"]['Schedule'][id]
        html_list_groundfloor["Heaters"].append(radiateur_data)

def update_firstfloor_heaters():
    global HEATERS_DATA
    global html_list_firstfloor
    html_list_firstfloor ["Heaters"].clear()
    # build the list for HTML
    for id, radiateur_data in HEATER_CONFIGS["Maison"]["Etage_1"].items():
        radiateur_data = radiateur_data.copy()
        radiateur_data['Id'] = id
        radiateur_data['Mode'] = HEATERS_DATA["Maison"]["Etage_1"]['Mode'][id]
        radiateur_data['Force'] = HEATERS_DATA["Maison"]["Etage_1"]['Force'][id]
        # Example schedule
        radiateur_data['Schedule'] = HEATERS_DATA["Maison"]["Etage_1"]['Schedule'][id]
        html_list_firstfloor["Heaters"].append(radiateur_data)

def pipe_exchanges():
    global HEATERS_DATA
    global serv2main_msg
    global serv2main_trigger
    global lock
    # échange initial, etats, force et schedule, pour tous les heaters
    with lock:
        respons =send_request_on_pipe( 1, 255, 255, "")
    print("response ", respons)
    retcode, serv2main_msg = read_string2fulljson(respons, HEATERS_DATA)
    if retcode != 0:
        print( serv2main_msg)
        #print("JSON invalide, reinitialisation des donnees")
        #HEATERS_DATA = HEATERS_DATA_INIT.copy()
    print("keys HEATERS_DATA ", HEATERS_DATA.keys())
    print("keys HEATERS_DATA['Maison'] ", HEATERS_DATA["Maison"].keys())
    updage_groundfloor_heaters()
    update_firstfloor_heaters()

    time.sleep( 1)

    while end_pipes_exchanges == False:
        if serv2main_trigger == True:
            serv2main_trigger = False
            respons = send_request_on_pipe( 2, 255, 255, serv2main_msg)
            print("response ", respons)
        else:
            # échanges périodiques, etats et force, pour tous les heaters
            with lock:
                respons =send_request_on_pipe( 1, 255, 3, "")
            print("response ", respons)
            retcode, msg = read_string2partialjson(respons, HEATERS_DATA)
            if retcode != 0:
                print( msg)
            print("keys HEATERS_DATA ", HEATERS_DATA.keys())
            print("keys HEATERS_DATA['Maison'] ", HEATERS_DATA["Maison"].keys())
            updage_groundfloor_heaters()
            update_firstfloor_heaters()

        time.sleep( 20)

@app.route('/')
def accueil():
    global HEATERS_DATA
    # read the data from file
    # retcode, msg = read_file2json(HEATERS_DATA)
    #if retcode != 0:
    #    if retcode == -2:
    #        print("JSON invalide, reinitialisation des donnees")
    #    HEATERS_DATA = HEATERS_DATA_INIT.copy()
    # print("keys HEATERS_DATA ", HEATERS_DATA.keys())
    # print("keys HEATERS_DATA['Maison'] ", HEATERS_DATA["Maison"].keys())

    return render_template('index.html')


@app.route('/groundfloor')
def groundfloor():
#    global HEATERS_DATA
    global html_list_groundfloor
    # # build the list for HTML
    # for id, radiateur_data in HEATER_CONFIGS["Maison"]["Etage_0"].items():
    #     radiateur_data = radiateur_data.copy()
    #     radiateur_data['Id'] = id
    #     radiateur_data['Mode'] = HEATERS_DATA['Mode'][id]
    #     radiateur_data['Force'] = HEATERS_DATA['Force'][id]
    #     # Example schedule
    #     radiateur_data['Schedule'] = HEATERS_DATA['Schedule'][id]
    #     html_list_groundfloor["Heaters"].append(radiateur_data)

    # for id, piece_data in GROUP_CONFIGS["Maison"]["Etage_0"].items():
    #     piece_data = piece_data.copy()
    #     piece_data['Id'] = id
    #     html_list_groundfloor["Groups"].append(piece_data)

    return render_template('GroundFloor.html', heaters=html_list_groundfloor["Heaters"], groups=html_list_groundfloor["Groups"])


@app.route('/firstfloor')
def firstfloor():
    return render_template('FirstFloor.html', heaters=html_list_firstfloor["Heaters"], groups=html_list_firstfloor["Groups"])


@app.route('/refresh_groundfloor_data')
def refresh_groundfloor_data():
    return jsonify(html_list_groundfloor)


@app.route('/refresh_firstfloor_data')
def refresh_firstfloor_data():
    return jsonify(html_list_firstfloor)


@app.route('/groundfloor/heater/<heater_id>/set-NewheaterState', methods=["POST"])
def set_new_groundfloor_heaterstate(heater_id: str):
    global HEATERS_DATA
    # get the parameter
    force_mode = request.json.get("forcemode")
    force_heure = request.json.get("forceheure")
    force_minute = request.json.get("forceminute")

    #initiate list of heaters to update in main app
    heaters = []

    # save the new state to the HeaterState list
    HEATERS_DATA["Maison"]["Etage_0"]["Force"][heater_id] = { 
        "Heure": force_heure,
        "Minute": force_minute,
        "Mode": force_mode
    }

    #add the heater to the list of heaters to update in main app
    heaters.append(heater_id)

    #request send to main app
    update_main_app( "Etage_0", "Force", heaters)

    # write to file
    write_json2file(HEATERS_DATA)

    #logger info
    mylog.info_log("heater: " + heater_id + " state set")

    return {"status": "success", "mode": force_mode}, 200


@app.route('/firstfloor/heater/<heater_id>/set-NewheaterState', methods=["POST"])
def set_new_heaterstate(heater_id: str):
    global HEATERS_DATA
    # get the parameter
    force_mode = request.json.get("forcemode")
    force_heure = request.json.get("forceheure")
    force_minute = request.json.get("forceminute")

    #initiate list of heaters to update in main app
    heaters = []

    # save the new state to the HeaterState list
    HEATERS_DATA["Maison"]["Etage_1"]["Force"][heater_id] = { 
        "Heure": force_heure,
        "Minute": force_minute,
        "Mode": force_mode
    }

    #add the heater to the list of heaters to update in main app
    heaters.append(heater_id)

    #request send to main app
    update_main_app( "Etage_1", "Force", heaters)

    # write to file
    write_json2file(HEATERS_DATA)

    #logger info
    mylog.info_log("heater: " + heater_id + " state set")

    return {"status": "success", "mode": force_mode}, 200


@app.route('/groundfloor/group/<group_id>/set-NewGroupState', methods=["POST"])
def set_new_groundfloor_group_state(group_id: str):
    global HEATERS_DATA
    # get the parameter
    force_mode = request.json.get("forcemode")
    force_heure = request.json.get("forceheure")
    force_minute = request.json.get("forceminute")

    #initiate list of heaters to update in main app
    heaters = []

    # update all heaters in the piece
    GroupName = GROUP_CONFIGS["Maison"]["Etage_0"][group_id]["Nom"]
    for id, radiateur_data in HEATER_CONFIGS["Maison"]["Etage_0"].items():
        if radiateur_data["Groupe"] == GroupName:
            HEATERS_DATA["Maison"]["Etage_0"]["Force"][id] = { 
                "Heure": force_heure,
                "Minute": force_minute,
                "Mode": force_mode
            }

            #add the heater to the list of heaters to update in main app
            heaters.append(id)

    #request send to main app
    update_main_app( "Etage_0", "Force", heaters)

    # write to file
    write_json2file(HEATERS_DATA)

    #logger info
    mylog.info_log("group: " + GroupName + " state set")

    return {"status": "success", "mode": force_mode}, 200


@app.route('/firstfloor/group/<group_id>/set-NewGroupState', methods=["POST"])
def set_new_firstfloor_group_state(group_id: str):
    global HEATERS_DATA
    # get the parameter
    force_mode = request.json.get("forcemode")
    force_heure = request.json.get("forceheure")
    force_minute = request.json.get("forceminute")

    #initiate list of heaters to update in main app
    heaters = []

    # update all heaters in the piece
    GroupName = GROUP_CONFIGS["Maison"]["Etage_1"][group_id]["Nom"]
    for id, radiateur_data in HEATER_CONFIGS["Maison"]["Etage_1"].items():
        if radiateur_data["Groupe"] == GroupName:
            HEATERS_DATA["Maison"]["Etage_1"]["Force"][id] = { 
                "Heure": force_heure,
                "Minute": force_minute,
                "Mode": force_mode
            }

            #add the heater to the list of heaters to update in main app
            heaters.append(id)

    #request send to main app
    update_main_app( "Etage_1", "Force", heaters)

    # write to file
    write_json2file(HEATERS_DATA)

    #logger info
    mylog.info_log("group: " + GroupName + " state set")

    return {"status": "success", "mode": force_mode}, 200


@app.route('/groundfloor/heater/<heater_id>/set-NewHeaterConfig', methods=["POST"])
def set_new_groundfloor_heater_config(heater_id: str):
    global HEATERS_DATA
    # get the parameter
    RadSchedule = request.json.get("DayConfigs")

    #initiate list of heaters to update in main app
    heaters = []

    # save the new state to the HeaterState list
    HEATERS_DATA["Maison"]["Etage_0"]["Schedule"][heater_id] = RadSchedule

    #add the heater to the list of heaters to update in main app
    heaters.append(heater_id)

    #request send to main app
    update_main_app( "Etage_0", "Schedule", heaters)

    # write to file
    write_json2file(HEATERS_DATA)

    #logger info
    mylog.info_log("heater: " + heater_id + " config set")

    return {"status": "success", "state": "1"}, 200


@app.route('/firstfloor/heater/<heater_id>/set-NewHeaterConfig', methods=["POST"])
def set_new_firstfloor_heater_config(heater_id: str):
    global HEATERS_DATA
    # get the parameter
    RadSchedule = request.json.get("DayConfigs")

    #initiate list of heaters to update in main app
    heaters = []

    # save the new state to the HeaterState list
    HEATERS_DATA["Maison"]["Etage_1"]["Schedule"][heater_id] = RadSchedule

    #add the heater to the list of heaters to update in main app
    heaters.append(heater_id)

    #request send to main app
    update_main_app( "Etage_1", "Schedule", heaters)

    # write to file
    write_json2file(HEATERS_DATA)

    #logger info
    mylog.info_log("heater: " + heater_id + " config set")

    return {"status": "success", "state": "1"}, 200


@app.route('/groundfloor/group/<group_id>/set-NewGroupConfig', methods=["POST"])
def set_new_groundfloor_group_config(group_id: str):
    global HEATERS_DATA
    # get the parameter
    GroupSchedule = request.json.get("DayConfigs")

    #initiate list of heaters to update in main app
    heaters = []

    # update all heaters in the group
    GroupName = GROUP_CONFIGS["Maison"]["Etage_0"][group_id]["Nom"]
    for id, heater_data in HEATER_CONFIGS["Maison"]["Etage_0"].items():
        if heater_data["Groupe"] == GroupName:
            HEATERS_DATA["Maison"]["Etage_0"]["Schedule"][id] = GroupSchedule

            #add the heater to the list of heaters to update in main app
            heaters.append(id)

    #request send to main app
    update_main_app( "Etage_0", "Schedule", heaters)

    # write to file
    write_json2file(HEATERS_DATA)

    #logger info
    mylog.info_log("group: " + GroupName + " config set")

    return {"status": "success", "state": "1"}, 200


@app.route('/firstfloor/group/<group_id>/set-NewGroupConfig', methods=["POST"])
def set_new_firstfloor_group_config(group_id: str):
    global HEATERS_DATA
    # get the parameter
    GroupSchedule = request.json.get("DayConfigs")

    #initiate list of heaters to update in main app
    heaters = []

    # update all heaters in the group
    GroupName = GROUP_CONFIGS["Maison"]["Etage_1"][group_id]["Nom"]
    for id, radiateur_data in HEATER_CONFIGS["Maison"]["Etage_1"].items():
        if radiateur_data["Groupe"] == GroupName:
            HEATERS_DATA["Maison"]["Etage_1"]["Schedule"][id] = GroupSchedule

            #add the heater to the list of heaters to update in main app
            heaters.append(id)

    #request send to main app
    update_main_app( "Etage_1", "Schedule", heaters)

    # write to file
    write_json2file(HEATERS_DATA)

    #logger info
    mylog.info_log("group: " + GroupName + " config set")

    return {"status": "success", "state": "1"}, 200


if __name__ == '__main__':
    #
    # Charger le fichier de configuration
    print("Load configuration...")
    config_path = Path(__file__).resolve().parent / "configuration.yaml"
    if( config_path.exists() == False ):
        print("Fichier de configuration introuvable")
        sys.exit( -1 )

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    print(config)

    # Initialiser le logging
    if "log_path" not in config:
        print("Clé log_path introuvable dans le fichier de configuration")
        sys.exit( -1 )
    mylog.start_log( config["log_path"])
    mylog.info_log("Serveur started")

    # initialisation des tubes d'échange
    init_pipes( config)
    time.sleep( 2)

    #
    # initialisation de la liste pour HTML
    #
    init_html_list_groundfloor_groups()
    init_html_list_firstfloor_groups()

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

    # Fermer le logging
    mylog.info_log("Serveur stopped")
    mylog.close_log()

