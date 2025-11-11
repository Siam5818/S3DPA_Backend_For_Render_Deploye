# 
from app import create_app
from app.mqtt_client import start_mqtt
import threading

app = create_app()

if __name__ == "__main__":
    mqtt_thread = threading.Thread(target=start_mqtt)
    mqtt_thread.daemon = True
    mqtt_thread.start()

    app.run(debug=True)