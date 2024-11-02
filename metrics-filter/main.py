"""
A reversed proxy server for filtering prometheus exporter metrics.
"""

import argparse
import configparser
import sys
from urllib.parse import urljoin
import requests
from flask import Flask, request, make_response

# Read the command line arguments and read the configuration files

parser = argparse.ArgumentParser(description='Metrics Fliter')
parser.add_argument(
    '-c',
    '--configuration',
    default='sample.conf',
    help='The configuration file you want to use to launch the metric filter.'
)

args = parser.parse_args()
configuration = args.configuration
config = configparser.ConfigParser()
config.read(configuration)

if 'Settings' not in config:
    print('Invalid configuration file.')
    sys.exit(0)

# Initialize the global constants

TARGET = config['Settings'].get('target', None)
PORT = config['Settings'].get('port', None)

if TARGET is None:
    print("Target is not set.")
    sys.exit(0)

if PORT is None or not PORT.isnumeric():
    print("Port is not set. Using default port 8000.")
    PORT = 8000

with open('./whitelist.txt', 'r', encoding='utf-8') as f:
    WHITELIST=f.read().splitlines()

# Initialize the Flask app

app = Flask(__name__)

def fetch(url):
    """
    Fetching data from target and filtering the metrics from the data.
    """
    raw_metrics = requests.get(url, timeout=(3, 5)).text.splitlines()
    filtered_metrics = []

    for metric in raw_metrics:
        for pattern in WHITELIST:
            if pattern in metric:
                filtered_metrics.append(metric)
                break

    return "\n".join(filtered_metrics)

@app.route('/')
def fetch_root_route():
    """
    This route is for '/'.
    """
    print('Accessing to "/".')
    response = make_response(fetch(TARGET))
    response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return response

@app.route('/<path:path>')
def fetch_route(path):
    """
    This route is for all other URLs.
    """
    print(f'Accessing to "{path}".')
    response = make_response(fetch(urljoin(TARGET, request.full_path)))
    response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(PORT))

# author: theoyu314159, K Rin
