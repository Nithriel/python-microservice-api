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


with open('app_conf.yaml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yaml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config) 

logger = logging.getLogger('basicLogger')

DB_ENGINE = create_engine('mysql+pymysql://{}:{}@{}:{}/{}'.format(
    app_config['datastore']['user'], app_config['datastore']['password'], app_config['datastore']['hostname'], app_config['datastore']['port'], app_config['datastore']['db']))
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

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
    app.run(port=8090)
