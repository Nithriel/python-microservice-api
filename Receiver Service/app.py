import connexion 
from connexion import NoContent
import json
import os
from os import path
import yaml
import logging
import logging.config
import requests

with open('app_conf.yaml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yaml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config) 

logger = logging.getLogger('basicLogger')

def add_bug_report(body):
    logger.info('Received event add_bug_report request with a unique id of {} - {} - {}'.format(body['title'], body['description'], body['location']))
    bug = requests.post(app_config['report_bug']['url'], json=body)
    logger.info('Returned event add_bug_report response (Id: {} - {} - {}) with status {}'.format(body['title'], body['description'], body['location'], bug.status_code))
    return NoContent, bug.status_code

def add_player_report(body):
    logger.info('Received event add_player_report request with a unique id of {} - {} - {}'.format(body['player_name'], body['description'], body['location']))
    player = requests.post(app_config['report_player']['url'], json=body)
    logger.info('Returned event add_player_report response (Id: {} - {} - {}) with status {}'.format(body['player_name'], body['description'], body['location'], player.status_code))
    return NoContent, player.status_code

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", base_path='/', strict_validation=True, validate_responses=True)    

if __name__ == "__main__":    
    app.run(port=8080)
