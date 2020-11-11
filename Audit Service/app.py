import connexion
from connexion import NoContent
import datetime
from flask_cors import CORS, cross_origin

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging
import logging.config
import yaml
import json
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread


with open('app_conf.yaml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yaml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config) 

logger = logging.getLogger('basicLogger')

HOSTNAME = "{}:{}".format(app_config["events"]["hostname"], app_config["events"]["port"])
TOPIC = app_config["events"]["topic"]

def get_bug_reports(index):
    """ Get Bug Reports in History """
    hostname = "{}:{}".format(app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[app_config["events"]["topic"]]
    
    # Here we reset the offset on start so that we retrieve
    # messages at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to
    # 100ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(consumer_group='event_group', reset_offset_on_start=True, consumer_timeout_ms=100)
    
    logger.info("Retrieving Bug Reports at index {}".format(index))
    count = 0
    for msg in consumer:
        msg_str = msg.value.decode("utf-8")
        msg = json.loads(msg_str)
        
        payload = msg["payload"]
        
        # Find the event at the index you want and
        # return code 200
        # i.e., return event, 200
        if msg["type"] == "bug":
            if count == index:
                return payload, 200
            
            count += 1
    logger.error("Could not find Bug Reports at index {}".format(index))
    return { "message": "Not Found" }, 404
            
def get_player_reports(index):
    """ Get Player Reports in History """
    hostname = "{}:{}".format(app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[app_config["events"]["topic"]]
    
    # Here we reset the offset on start so that we retrieve
    # messages at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to
    # 100ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(consumer_group='event_group', reset_offset_on_start=True, consumer_timeout_ms=100)
    
    logger.info("Retrieving Player Reports at index {}".format(index))
    count = 0
    for msg in consumer:
        msg_str = msg.value.decode("utf-8")
        msg = json.loads(msg_str)
        
        payload = msg["payload"]

        
        # Find the event at the index you want and
        # return code 200
        # i.e., return event, 200
        if msg["type"] == "player":
            if count == index:
                return payload, 200
            
            count += 1
    logger.error("Could not find Player Reports at index {}".format(index))
    return { "message": "Not Found" }, 404

app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yaml", base_path='/', strict_validation=True, validate_responses=True)    

if __name__ == "__main__":
    app.run(port=8110)
