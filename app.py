#!/usr/bin/env python
"""
DevQuotes: FIXME
"""

from flask import Flask, render_template
import requests
import json
import platform
import psutil
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
      with open("/proc/loadavg", "r") as f:
        return(f.read().strip())


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
      return(ips)

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

    @app.route('/')
    def home():
        return render_template('index.html', page_title="Dev Quotes", quotes=get_quotes(api_url))

    @app.route('/pod')
    def podinfo():
        return render_template('podinfo.html', page_title="Dev Quotes - Container info", os_info=get_system_info() )

    @app.route('/about')
    def about():
        return render_template('about.html', page_title="Dev Quotes - About", os_info=get_system_info() )
    
    @app.route('/healthz', methods=['GET'])
    def health():
        """
        Fake liveness probe
        """
        return 'OK'

    return app

app=create_app()
register_metrics(app, app_version="v0.1", app_config="dev")
dispatcher = DispatcherMiddleware(app.wsgi_app, {"/metrics": make_wsgi_app()})

if __name__ == "__main__":
    run_simple(
        "0.0.0.0",
        8080,
        application=dispatcher
    )
