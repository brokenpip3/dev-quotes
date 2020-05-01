#!/usr/bin/env python
"""
DevQuotes: FIXME
"""

from flask import Flask, render_template, send_from_directory
import requests
import json
import platform
import psutil
import os
from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
from flask_prometheus_metrics import register_metrics

api_url = 'https://programming-quotes-api.herokuapp.com/quotes/random/lang/en'

def get_quotes(api_url):
    """
    get_quotes get api random quote and return into dictionary
    """
    response = requests.get(api_url)
    if response.status_code == 200:
       text = json.loads(response.text)
       return text

def get_system_info():

    osinfo = dict()

    def loadavg():
      """
      Load average
      """
      load1, load5, load15 = os.getloadavg()
      return load1


    def memory():
      """
      Memory information
      """
      with open("/proc/meminfo", "r") as f:
          lines = f.readlines()
      mem1 = (lines[0].strip())
      mem2 = (lines[1].strip())
      return (mem1 + " " + mem2)

    def uptime():
      """
      Uptime
      """
      uptime = None
      with open("/proc/uptime", "r") as f:
          uptime = f.read().split(" ")[0].strip()
      uptime = int(float(uptime))
      uptime_hours = uptime // 3600
      uptime_minutes = (uptime % 3600) // 60
      return(str(uptime_hours) + ":" + str(uptime_minutes) + " hours")

    def getip():
      """
      Ip information
      """
      ifaces = psutil.net_if_addrs()
      ips = dict()
      for k, v in ifaces.items():
          ips[k] = v[0].address
      return ips

    osinfo["Hostname"] = platform.node()
    osinfo["System"] = platform.system()
    osinfo["Architecture"] = platform.architecture()[0]
    osinfo["Machine"] = platform.machine()
    osinfo["Load Average"] = loadavg()
    osinfo["Memory"] = memory()
    osinfo["Uptime"] = uptime()
    osinfo["IP"] = getip()

    return osinfo

def create_app():
    """
    create_app
    """

    app = Flask(__name__, static_url_path='/static')

    @app.route('/', methods=['GET'])
    def home():
        return render_template('index.html', page_title="Dev Quotes", quotes=get_quotes(api_url))

    @app.route('/pod', methods=['GET'])
    def podinfo():
        return render_template('podinfo.html', page_title="Dev Quotes - Container info", os_info=get_system_info() )

    @app.route('/about', methods=['GET'])
    def about():
        return render_template('about.html', page_title="Dev Quotes - About")
    
    @app.route('/healthz', methods=['GET'])
    def health():
        """
        Fake liveness probe
        """
        return 'OK'
    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'),
                          'favicon.ico',mimetype='image/vnd.microsoft.icon')
    return app

app=create_app()
register_metrics(app, app_version="v0.2", app_config="dev")
dispatcher = DispatcherMiddleware(app.wsgi_app, {"/metrics": make_wsgi_app()})

if __name__ == "__main__":
    run_simple(
        "0.0.0.0",
        8080,
        application=dispatcher
    )
