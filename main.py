import time
from flask import Flask, request, jsonify, Response, render_template
from flask_mqtt import Mqtt

app = Flask(__name__)

app.config['MQTT_BROKER_URL'] = 'broker.hivemq.com'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = ''  # Set this item when you need to verify username and password
app.config['MQTT_PASSWORD'] = ''  # Set this item when you need to verify username and password
app.config['MQTT_KEEPALIVE'] = 5  # Set KeepAlive time in seconds
app.config['MQTT_TLS_ENABLED'] = False  # If your server supports TLS, set it True
topic = 'flask/iot' # Topic name

mqtt_client = Mqtt(app)

@mqtt_client.on_connect()
def handle_connect(client, userdata, flags, rc):
   if rc == 0:
       print('Connected successfully')
       mqtt_client.subscribe(topic) # subscribe topic
   else:
       print('Bad connection. Code:', rc)

mensagem_mqtt = None

@mqtt_client.on_message()
def handle_mqtt_message(client, userdata, message):
    global mensagem_mqtt  # Use the global variable
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )
    print('Received message on topic: {topic} with payload: {payload}'.format(**data))
    mensagem_mqtt = data['payload']  # Store the payload in mensagem_mqtt

def get_new_message():
    global mensagem_mqtt
    while True:
        if mensagem_mqtt is not None:
            yield f"data: {mensagem_mqtt}\n\n"
            mensagem_mqtt = None  # Clear the message after sending it
        time.sleep(2)  # Adjust the delay between updates as needed

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stream')
def stream():
    # Return a response object with 'text/event-stream' mimetype
    return Response(get_new_message(), content_type='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True)
