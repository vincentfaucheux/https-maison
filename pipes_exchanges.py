from pathlib import Path
import sys
import time
import threading
import yaml
import struct


#
# Callback data received
#
def on_data():
    global ep
    global bDataReceived
    global buf_reply
    global reply_length
    data = ep.read()
    if( len(buf_reply) < 5 ):
        buf_reply += data
        if( len(buf_reply) >= 5 ):
            reply_length = buf_reply[3] << 8 | buf_reply[4]
            if( len(buf_reply) - 5 >= reply_length ):
                # tout reçu
                bDataReceived = True
    else:
        buf_reply += data
        if( len(buf_reply) - 5 >= reply_length ):
            # tout reçu
            bDataReceived = True

#
#pipes initialization
#
def init_pipes():
    global ep
    global bWriteCreated
    global bDataReceived
    global buf_reply
    global reply_length
    ep = None
    bWriteCreated = False
    bDataReceived = False
    buf_reply = bytearray()
    reply_length = 0

    print("Initialisation des tubes d'échange...")
    #
    # Charger le fichier de configuration
    config_path = Path(__file__).resolve().parent / "configuration.yaml"
    if( config_path.exists() == False ):
        print("Fichier de configuration introuvable")
        sys.exit( -1 )

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    print(config)

    #
    #charger la librairie interprocess
    #
    if "interprocess_client_lib" not in config:
        print("Clé interprocess_client_lib introuvable dans le fichier de configuration")
        sys.exit( -1 )
    sys.path.append(config["interprocess_client_lib"])  # Chemin vers le module compilé
    from pipecom import EndPointCom
                
    #
    # Créer l'EndPointCom
    #
    if (("app2serv_pipe_name" not in config) or
        ("serv2app_pipe_name" not in config) or
        ("interprocess_pipes_lib" not in config)):
        print("Clé(s) manquante(s) dans le fichier de configuration")
        sys.exit( -1 )

    ep = EndPointCom(
        config["interprocess_pipes_lib"],
        config["app2serv_pipe_name"],
        config["serv2app_pipe_name"]
    )

    if( ep != None ):
        #
        # Attendre la création du pipe write
        #
        while not bWriteCreated:
            if(ep.is_write_created() == True):
                bWriteCreated = True
                print("WRITE pipe créé")
        time.sleep(0.1)

#
# End pipes
#
def end_pipes():
    global ep
    if ep != None:
        del ep
        
#
# sznd request on pipe and wait for respons
#
def send_request_on_pipe(cmd, floors, items, str_data):
    global ep
    global bDataReceived
    global buf_reply
    buf_reply = bytearray()
    if ep != None:
        # les données à envoyer
        data_bytes = str_data.encode('utf-8')
        # longueur des données
        length = len(data_bytes)
        # construire le buffer à envoyer
        # > : big-endian, B : unsigned char (1 byte), H : unsigned short (2 bytes)
        buffer = struct.pack(">B B B H", cmd, floors, items, length) + data_bytes
        # response buffer vide au départ
        #
        # Envoyer des données
        #
        ep.write( buffer)

        #
        # Attendre la réception des données
        #
        while not bDataReceived:
            if( ep.is_data_received() == True ):
                while not bDataReceived:
                    on_data()
                    time.sleep(0.01)
            time.sleep(0.01)
        bDataReceived = False
        print("Cmd " + str( struct.unpack_from( ">B", buf_reply, 0)))
        print("Floors " + str( struct.unpack_from( ">B", buf_reply, 1)))
        print("Items " + str( struct.unpack_from( ">B", buf_reply, 2)))
        print("Argument size " + str( struct.unpack_from( ">H", buf_reply, 3)))
    return buf_reply[5:5+reply_length].decode('utf-8')
