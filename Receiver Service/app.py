import connexion 
from connexion import NoContent
import json
import os
from os import path
import yaml
import logging
import logging.config
import requests
import datetime
import json
from pykafka import KafkaClient

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())
    # External Logging Configuration
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
    logger = logging.getLogger('basicLogger')
    logger.info("App Conf File: %s" % app_conf_file)
    logger.info("Log Conf File: %s" % log_conf_file)


logger = logging.getLogger('basicLogger')
HOSTNAME = "{}:{}".format(app_config["events"]["hostname"], app_config["events"]["port"])
TOPIC = app_config["events"]["topic"]

def add_bug_report(body):
    logger.info('Received event add_bug_report request with a unique id of {} - {} - {}'.format(body['title'], body['description'], body['location']))

    # bug = requests.post(app_config['report_bug']['url'], json=body)
    client = KafkaClient(hosts=HOSTNAME)
    topic = client.topics[TOPIC]
    producer = topic.get_sync_producer()
    msg = { "type": "bug",
        "datetime":
                datetime.datetime.now().strftime(
                    "%Y-%m-%dT%H:%M:%S"),
           "payload": body}
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.info('Returned event add_bug_report response (Id: {} - {} - {}) with status {}'.format(body['title'], body['description'], body['location'], '201'))
    return NoContent, 201

def add_player_report(body):
    logger.info('Received event add_player_report request with a unique id of {} - {} - {}'.format(body['player_name'], body['description'], body['location']))

    # player = requests.post(app_config['report_player']['url'], json=body)
    client = KafkaClient(hosts=HOSTNAME)
    topic = client.topics[TOPIC]
    producer = topic.get_sync_producer()
    msg = { "type": "player",
        "datetime":
                datetime.datetime.now().strftime(
                    "%Y-%m-%dT%H:%M:%S"),
           "payload": body}
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.info('Returned event add_player_report response (Id: {} - {} - {}) with status {}'.format(body['player_name'], body['description'], body['location'], '201'))
    return NoContent, 201

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", base_path='/', strict_validation=True, validate_responses=True)    

if __name__ == "__main__":    
    app.run(port=8080)
