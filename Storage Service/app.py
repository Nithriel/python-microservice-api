import connexion
from connexion import NoContent
import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from bug_report import BugReport
from player_report import PlayerReport
import logging
import logging.config
import yaml
import json
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread
import os

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yaml"
    log_conf_file = "/config/log_conf.yaml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yaml"
    log_conf_file = "log_conf.yaml"

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

DB_ENGINE = create_engine('mysql+pymysql://{}:{}@{}:{}/{}'.format(
    app_config['datastore']['user'], app_config['datastore']['password'], app_config['datastore']['hostname'], app_config['datastore']['port'], app_config['datastore']['db']))
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

logger.info('Connecting to DB {}:{} with user {}'.format(app_config['datastore']['hostname'], app_config['datastore']['port'], app_config['datastore']['user']))

def process_messages():
    """ Process event messages """
    client = KafkaClient(hosts=HOSTNAME)
    topic = client.topics[TOPIC]

    # Create a consume on a consumer group, that only reads new messages
    # (uncommitted messages) when the service re-starts (i.e., it doesn't
    # read all the old messages from the history in the message queue).
    consumer = topic.get_simple_consumer(consumer_group='event_group',
                                         reset_offset_on_start=False,
                                         auto_offset_reset=OffsetType.LATEST)
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)
        payload = msg["payload"]
        if msg["type"] == "bug": # Change this to your event type
            add_bug_report(payload)
        elif msg["type"] == "player": # Change this to your event type
            add_player_report(payload)
        # Commit the new message as being read
        consumer.commit_offsets()

def add_bug_report(body):
    """ Receives a bug report """
    session = DB_SESSION()

    br = BugReport(body.get('title'),
                       body.get('description'),
                       body.get('location'),
                       body.get('type'),
                       body.get('date'))

    session.add(br)

    session.commit()
    session.close()

    logger.debug('Stored event add_bug_report request with a unique id of {} - {} - {}'.format(body['title'], body['description'], body['location']))
    return NoContent, 201

def get_bug_reports(timestamp):
    """ Gets new bug reports after the timestamp """
    session = DB_SESSION()
    
    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
    report_list = session.query(BugReport).filter(BugReport.date_created >= timestamp_datetime)
    
    results_list = []
    
    for report in report_list:
        results_list.append(report.to_dict())
        
    session.close()
    
    logger.info('Query for bug reports Info after {} returns {} results'.format(timestamp, len(results_list)))
    
    return results_list, 200


def add_player_report(body):
    """ Receives a player report """
    session = DB_SESSION()

    pr = PlayerReport(body.get('player_name'),
                       body.get('description'),
                       body.get('location'),
                       body.get('type'),
                       body.get('date'))

    session.add(pr)

    session.commit()
    session.close()

    logger.debug('Stored event add_player_report request with a unique id of {} - {} - {}'.format(body['player_name'], body['description'], body['location']))
    return NoContent, 201

def get_player_reports(timestamp):
    """ Gets new player reports after the timestamp """
    session = DB_SESSION()
    
    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
    report_list = session.query(PlayerReport).filter(PlayerReport.date_created >= timestamp_datetime)
    
    results_list = []
    
    for report in report_list:
        results_list.append(report.to_dict())
        
    session.close()
    
    logger.info('Query for bug reports Info after {} returns {} results'.format(timestamp, len(results_list)))
    
    return results_list, 200

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", base_path='/', strict_validation=True, validate_responses=True)    

if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8090)
