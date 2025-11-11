import json
import threading
import paho.mqtt.client as mqtt
from app import create_app
from app.extension import db
from app.models.donnees_medicales import DonneesMedicale

app = create_app()

def on_connect(client, userdata, flags, rc):
    print("Connecté au broker MQTT avec code", rc)
    client.subscribe("s3dpa/donnees")

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        with app.app_context():
            for item in data:
                donnee = DonneesMedicale(
                    patient_id=item["patient_id"],
                    capteur_id=item["capteur_id"],
                    valeur_mesuree=item["valeur_mesuree"]
                )
                db.session.add(donnee)
            db.session.commit()
            print("Données insérées :", data)
    except Exception as e:
        print("Erreur MQTT :", e)

def start_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("broker.hivemq.com", 1883, 60)
    client.loop_forever()
