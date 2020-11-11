import connexion
from connexion import NoContent
import datetime
from flask_cors import CORS, cross_origin

import logging
import logging.config
import yaml
from apscheduler.schedulers.background import BackgroundScheduler
import json
import requests


with open('app_conf.yaml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yaml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config) 

logger = logging.getLogger('basicLogger')

def get_stats():
    """ Receives a bug report """
    logger.info('GET request stats has been initiated')
    try:
        with open(app_config['datastore']['filename'], 'r') as f:
            data_stats_read = f.read()
            
            # converted to object
            data_stats = json.loads(data_stats_read)
            
            show_stats = {
                "num_player_reports": data_stats["num_player_reports"],
                "num_bug_reports": data_stats["num_bug_reports"],
                "total_reports": data_stats["total_reports"],
                "last_updated": data_stats["last_updated"]
            }
            
            logger.debug('Get stats with num_player_reports: {}, num_bug_reports: {}, total_reports: {}'.format(
                show_stats['num_player_reports'],
                show_stats['num_bug_reports'],
                show_stats['total_reports']
            ))
            
            logger.info('GET request stats has been completed')
            
            return show_stats, 200
            
    except FileNotFoundError:
        error_message = 'Statistics do not exist with status code 404'
        logger.error(error_message)
        
        return {"message": error_message}, 404

def populate_stats(): 
    """ Periodically update stats """
    
    logger.info('Periodic processing for stats has been initiated')
    
    stats_info = ''
    try:
        with open(app_config['datastore']['filename'], 'r') as f:
            data_read = f.read()
            stats_info = json.loads(data_read)
            
    except FileNotFoundError:
        with open(app_config['datastore']['filename'], 'w') as f:
            json_template = {
                "num_player_reports": 0,
                "num_bug_reports": 0,
                "total_reports": 0,
                "last_updated": "2000-01-01T00:00:00Z"
            }
            f.write(json.dumps(json_template, indent=4))
        
        with open(app_config['datastore']['filename'], 'r') as f:
            data_read = f.read()
            
            stats_info = json.loads(data_read)
            
    timestamp = {
        "timestamp": stats_info['last_updated']
    }

    get_bug_reports = requests.get('{}/reports/player'.format(app_config['eventstore']['url']), params=timestamp)
    
    get_player_reports = requests.get('{}/reports/bugs'.format(app_config['eventstore']['url']), params=timestamp)
    
    # logs for bug reports list
    if (get_bug_reports.status_code != 200):
        logger.error('Could not receive events GET bug reports list with status code {}'.format(
            get_bug_reports.status_code))
        
    else:
        logger.info('{} events received from bug reports GET request with status code {}'.format(
        len(get_bug_reports.json()),
        get_bug_reports.status_code))  
        
        stats_info["num_player_reports"] = stats_info["num_player_reports"] + len(get_bug_reports.json())
    
    # logs for player reports list
    if (get_player_reports.status_code != 200):
        logger.error('Could not receive events GET request player reports list with status code {}'.format(
            get_player_reports.status_code
        ))
    else:
        logger.info('{} events received from player reports GET request with status code {}'.format(
        len(get_player_reports.json()),
        get_player_reports.status_code))
        
        stats_info["num_bug_reports"] = stats_info["num_bug_reports"] + len(get_player_reports.json())
        
    # Updating data.json file
    stats_info["total_reports"] = stats_info["num_player_reports"] + stats_info["num_bug_reports"]
    stats_info["last_updated"] = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
    
    with open(app_config['datastore']['filename'], 'w') as f:
        f.write(json.dumps(stats_info, indent=4))
        
    logger.debug("Data store updated with num_player_reports: {}, num_bug_reports: {}, total_reports: {}".format(
        stats_info["num_player_reports"],
        stats_info["num_bug_reports"],
        stats_info["total_reports"]
    ))
    
    logger.info('Period processing for stats has ended')

def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats, 'interval', seconds=app_config['scheduler']['period_sec'])
    sched.start()

app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yaml", base_path='/', strict_validation=True, validate_responses=True)    

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100, use_reloader=False)
