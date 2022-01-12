#!/usr/bin/env python

from jinja2 import Template
import collections
import shlex, subprocess
import yaml
import jq
import json
import os
import re
import sys
import pyhelmmanager
from copy import deepcopy
import datetime

pipelineTemplate = 'pipeline.json.j2'

def getTemplateDir():
    return os.path.join(os.path.dirname(pyhelmmanager.__file__), "helm_templates")

def render_template(template_str, template_dict, output_file):
    output_str = Template(template_str).render(template_dict) if template_dict else template_str
    # to save the results
    if output_file:
        with open(output_file, "w") as f:
            f.write(output_str+'\n')
    else:
        return output_str

def read_template(filename):
    with open(os.path.join(getTemplateDir(), filename), 'r') as f:
        return '\n'.join(f.read().splitlines())

def convertUnicodeToString(data):
    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(convertUnicodeToString, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convertUnicodeToString, data))
    else:
        return data

def runCommand(cmd):
    args = shlex.split(cmd)
    return subprocess.check_output(args, stderr=subprocess.STDOUT)
    
def pyjq(inputs, rule):
    return jq.compile(rule).input(inputs).all()

def loadconfig(projectName):
    configFile = os.path.join(os.getcwd(), "config_%s.yaml" % projectName)
    if not os.path.exists(configFile):
      print("Config file '%s' not exists!" % configFile)
      sys.exit(1)
    with open(configFile, "r") as yamlfile:
        config = yaml.load(yamlfile, Loader=yaml.FullLoader)
        config["projectName"] = projectName
        return config

def saveconfig(data, filename):
    with open(filename, "w") as yamlfile:
        yaml.dump(data, yamlfile)

def getAppList(gatewayEndpoint, cookieheader=None):
    cmd = "helm application list --gate-endpoint %s" % gatewayEndpoint
    if cookieheader:
        cmd += " --default-headers Cookie=%s" % cookieheader
    apps = json.loads(runCommand(cmd))
    return pyjq(apps, ".[].name")

def getAppExecutionCount(appName, gatewayEndpoint, cookieheader=None):
    cmd = "curl -s %s/applications/%s/executions/search" % (gatewayEndpoin, appName)
    if cookieheader:
        cmd += " -H 'cookie: %s'" % cookieheader
    execution = json.loads(runCommand(cmd))
    return len(executionCount)

def appExists(appName, gatewayEndpoint, cookieheader=None, appList=None):
    if not appList:
        appList = getAppList(gatewayEndpoint, cookieheader)
    return (appName in appList)

def createApplication(appName, ownerEmail, cloudProvider, gatewayEndpoint, cookieheader=None):
    cmd = "helm application save --application-name %s --owner-email %s --cloud-providers %s --gate-endpoint %s" % (appName, ownerEmail, cloudProvider, gatewayEndpoint)
    if cookieheader:
        cmd += " --default-headers Cookie=%s" % cookieheader
    runCommand(cmd)

def getPipeline(appName, env, gatewayEndpoint, cookieheader=None):
    cmd = "helm pipeline get --application %s --name %s --gate-endpoint %s" % (appName, ("iac-%s" % env), gatewayEndpoint)
    if cookieheader:
        cmd += " --default-headers Cookie=%s" % cookieheader
    return json.loads(runCommand(cmd))

def getPipelineList(appName, gatewayEndpoint, cookieheader=None):
    cmd = "helm pipeline list --application %s --gate-endpoint %s" % (appName, gatewayEndpoint)
    if cookieheader:
        cmd += " --default-headers Cookie=%s" % cookieheader
    pipelines = json.loads(runCommand(cmd))
    return pyjq(pipelines, ".[].name")

def getPipelineTriggerStatus(appName, gatewayEndpoint, cookieheader=None):
    result = {}
    cmd = "helm pipeline list --application %s --gate-endpoint %s" % (appName, gatewayEndpoint)
    if cookieheader:
        cmd += " --default-headers Cookie=%s" % cookieheader
    pipelines = json.loads(runCommand(cmd))
    pipelineNameList = pyjq(pipelines, ".[].name")
    triggerEnableList = pyjq(pipelines, ".[].triggers[0].enabled")
    for i, pipeline in enumerate(pipelineNameList):
        result.update({pipeline: {"triggerEnabled": triggerEnableList[i]}})
    return result

def getPipelineExecutionStatus(appName, gatewayEndpoint, cookieheader=None):
    result = {}
    cmd = "curl -s %s/applications/%s/executions/search?reverse=true&statuses=RUNNING,SUCCEEDED" % (gatewayEndpoint, appName)
    if cookieheader:
        cmd += " --default-headers Cookie=%s" % cookieheader
    executionList =  json.loads(runCommand(cmd))
    for execution in executionList:
        endtime = datetime.datetime.fromtimestamp(execution['endTime']/1000)
        result.update({execution['name']: endtime.strftime('%Y-%m-%d %H:%M:%S')})
    return result

def getPipelineStatus(appName, gatewayEndpoint, cookieheader=None):
    result = {}
    cmd = "curl -s %s/applications/%s/pipelines?limit=1&statuses=RUNNING,SUCCEEDED" % (gatewayEndpoint, appName)
    if cookieheader:
        cmd += " -H 'cookie: %s'" % cookieheader
    statusList =  json.loads(runCommand(cmd))
    for status in statusList:
        endtime = datetime.datetime.fromtimestamp(status['endTime']/1000)
        result.update({status['name']: {"lastExecutiontime": endtime.strftime('%Y-%m-%d %H:%M:%S')}})
    return result

def pipelineExists(appName, env, gatewayEndpoint, cookieheader=None, appList=None):
    if not appList:
        appList = getAppList(gatewayEndpoint, cookieheader)
    if appName not in appList:
        return False
    pipelineList = getPipelineList(appName, gatewayEndpoint, cookieheader)
    return (("iac-%s" % env) in pipelineList)

def createPipeline(pipelineFile, gatewayEndpoint, cookieheader=None):
    cmd = "helm pipeline save --file %s --gate-endpoint %s" % (pipelineFile, gatewayEndpoint)
    if cookieheader:
        cmd += " --default-headers Cookie=%s" % cookieheader
    runCommand(cmd)

def deletePipeline(applicationName, pipelineName, gatewayEndpoint, cookieheader=None):
    cmd = "helm pipeline delete -a %s -n %s --gate-endpoint %s" % (applicationName, pipelineName, gatewayEndpoint)
    if cookieheader:
        cmd += " --default-headers Cookie=%s" % cookieheader
    runCommand(cmd)

def generate_pipeline_setting(appName, env, config):
    context = deepcopy(config.get('default', {}))
    context.update(config.get('environment', {}).get(env, {}))
    context.update(config.get('application', {}).get(appName, {}))
    context.update(config.get('application', {}).get(("%s.%s" % (appName, env)), {}))
    context['appName']=appName
    context['env']=env
    if 'gitRepo' not in context.keys():
        context['gitRepo'] = appName
    return context
