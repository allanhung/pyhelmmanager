{{- define "grafana-agent-eventhandler.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "grafana-agent-eventhandler.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- if contains $name .Release.Name -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
{{- end -}}

{{- define "grafana-agent-eventhandler.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "grafana-agent-eventhandler.image" -}}
{{- $tag := (coalesce .Values.image.tag .Chart.AppVersion) | toString -}}
{{- if .Values.image.registry -}}
{{- printf "%s/%s:%s" .Values.image.registry .Values.image.repository $tag -}}
{{- else -}}
{{- printf "%s:%s" .Values.image.repository $tag -}}
{{- end -}}
{{- end -}}

{{- define "grafana-agent-eventhandler.matchLabels" -}}
app: {{ template "grafana-agent-eventhandler.name" . }}
release: {{ .Release.Name }}
version: {{ .Chart.AppVersion }}
{{- end -}}

{{- define "grafana-agent-eventhandler.metaLabels" -}}
chart: {{ template "grafana-agent-eventhandler.chart" . }}
{{- end -}}

{{- define "grafana-agent-eventhandler.labels" -}}
{{ include "grafana-agent-eventhandler.metaLabels" . }}
{{ include "grafana-agent-eventhandler.matchLabels" . }}
{{- end -}}

{/* Allow KubeVersion to be overridden. */}}
{{- define "grafana-agent-eventhandler.ingress.kubeVersion" -}}
  {{- default .Capabilities.KubeVersion.Version .Values.kubeVersionOverride -}}
{{- end -}}

{{/* Get Ingress API Version */}}
{{- define "grafana-agent-eventhandler.ingress.apiVersion" -}}
  {{- if and (.Capabilities.APIVersions.Has "networking.k8s.io/v1") (semverCompare ">= 1.19.x" (include "grafana-agent-eventhandler.ingress.kubeVersion" .)) -}}
      {{- print "networking.k8s.io/v1" -}}
  {{- else if .Capabilities.APIVersions.Has "networking.k8s.io/v1beta1" -}}
    {{- print "networking.k8s.io/v1beta1" -}}
  {{- else -}}
    {{- print "extensions/v1beta1" -}}
  {{- end -}}
{{- end -}}

{{/* Check Ingress stability */}}
{{- define "grafana-agent-eventhandler.ingress.isStable" -}}
  {{- eq (include "grafana-agent-eventhandler.ingress.apiVersion" .) "networking.k8s.io/v1" -}}
{{- end -}}

{{/* Check Ingress supports pathType */}}
{{/* pathType was added to networking.k8s.io/v1beta1 in Kubernetes 1.18 */}}
{{- define "grafana-agent-eventhandler.ingress.supportsPathType" -}}
  {{- or (eq (include "grafana-agent-eventhandler.ingress.isStable" .) "true") (and (eq (include "grafana-agent-eventhandler.ingress.apiVersion" .) "networking.k8s.io/v1beta1") (semverCompare ">= 1.18.x" (include "grafana-agent-eventhandler.ingress.kubeVersion" .))) -}}
{{- end -}}
