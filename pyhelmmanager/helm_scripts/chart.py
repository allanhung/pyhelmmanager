#!/usr/bin/env python

"""
Generate helm chart by template
  create - create chart template
  patchrbacfile - patch kubernetes rbac file

Usage:
  pyhelmmanager chart create  (-p=<PROJECT>) [-k=<KIND>]
  pyhelmmanager chart patchrbacfile  (-p=<PROJECT>) (-f=<FILE>) 

Options:
  -h, --help                              Show this screen.
  -k=<KIND>, --kind=<KIND>                Kubernetes objects type [default deploy]
  -p=<PROJECT>, --project=<PROJECT>       Project Name
  -f=<PROJECT>, --file=<FILE>             RBAC File to patch
"""

from docopt import docopt
import os
import sys
import pyhelmmanager.helm_scripts.common as common
from tqdm import tqdm
import numpy
import yaml
import json
import pathlib
from shutil import copyfile
import jinja2

def create(args):
    print('create chart template in directory %s.' % args['--project'])
    if not args['--kind'] in ["deploy", "deployment", "ds", "daemonset"]:
        sys.exit('Does not support kind: %s' % args['--kind'])
    config = common.loadconfig(args['--project'])  
    config['kind']=args['--kind']
    chartTemplates = ["_helpers.tpl.j2", "Chart.yaml.j2", "configmap.yaml.j2", "values.yaml.j2", "service.yaml.j2", "service-udp.yaml.j2", "ingress.yaml.j2", "ingress_list.yaml.j2"]
    if args['--kind'] in ["deploy", "deployment"]:
        chartTemplates.append("deployment.yaml.j2")
    elif args['--kind'] in ["ds", "daemonset"]:
        chartTemplates.append("daemonset.yaml.j2")
    pathlib.Path(os.path.join(os.getcwd(), args['--project'], "templates")).mkdir(parents=True, exist_ok=True)
    for chartTemplate in tqdm(chartTemplates):
        if chartTemplate.endswith("values.yaml.j2"):
            chartFile = os.path.join(os.getcwd(), args['--project'], "values.yaml")
        elif chartTemplate[:-3] in ["Chart.yaml"]:
            chartFile = os.path.join(os.getcwd(), args['--project'], chartTemplate[:-3])
        else:
            chartFile = os.path.join(os.getcwd(), args['--project'], "templates", chartTemplate[:-3])
        common.render_template(common.read_template(chartTemplate), config, chartFile)
    print("Test:\n  helm template --namespace={project_name} {project_name} -f {project_name}/values.yaml {project_name}".format(project_name=args['--project']))
    print("Install:\n  helm upgrade --install {project_name} --namespace {project_name} --create-namespace -f {project_name}/values.yaml {project_name}".format(project_name=args['--project']))

def patchrbacfile(args):
    print('patch rbac file %s.' % args['--file'])
    metadata = {}
    outputFile = args['--file']
    metadata['labels']='{{- include "%s.labels" . | nindent 4 }}' % args['--project']
    metadata['name']='{{ include "%s.fullname" . }}' % args['--project']
    metadata['namespace']='{{ .Release.Namespace }}'
    if not os.path.exists(outputFile):
      print("File '%s' not exists!" % outputFile)
      sys.exit(1)
    file_extension = pathlib.Path(outputFile).suffix
    if file_extension == ".bak":
        outputFile = outputFile[:-4]
    else:
        copyfile(args['--file'], args['--file']+'.bak')
    with open(args['--file'], "r") as yamlFile:
        chartFiles = yaml.load_all(yamlFile, Loader=yaml.FullLoader)
        for i, chartFile in enumerate(chartFiles):
            chartFile['metadata']= metadata
            if "subjects" in chartFile.keys():
                chartFile["subjects"][0]["name"]='{{ include "%s.fullname" . }}' % args['--project']
                chartFile["subjects"][0]["namespace"]='{{ .Release.Namespace }}'
            if i == 0:
                with open(args['--file']+'.tmp', 'w') as outfile:
                    yaml.dump(chartFile, outfile)
            else:
                with open(args['--file']+'.tmp', 'a') as outfile:
                    outfile.write("---\n")
                    yaml.dump(chartFile, outfile, default_flow_style=False)
    with open(args['--file']+'.tmp', "rt") as fin:
        with open(outputFile, "wt") as fout:
            for line in fin:
                line = line.replace("'{{", "{{")
                line = line.replace("}}'", "}}")
                fout.write(line)
    os.remove(args['--file']+'.tmp')
