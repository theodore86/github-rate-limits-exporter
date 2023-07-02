{{/* vim: set filetype=mustache: */}}

{{/*
Expand the name of the chart.
*/}}
{{- define "github-rate-limits-exporter.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars and convert string to lowercase because some Kubernetes name fields are limited by complying to DNS naming spec.
If release name contains chart name it will be used as a full name.
*/}}
{{- define "github-rate-limits-exporter.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | lower | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name -}}
{{- .Release.Name | trunc 63 | lower | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | lower | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "github-rate-limits-exporter.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- /*
Standard labels are frequently used in metadata.
*/ -}}
{{- define "github-rate-limits-exporter.labels" -}}
app.kubernetes.io/name: {{ template "github-rate-limits-exporter.fullname" . }}
helm.sh/chart: {{ template "github-rate-limits-exporter.chart" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/version: {{ default .Chart.Version .Chart.AppVersion | quote }}
{{- end }}

{{- /*
Standar labels for workload selector filtering.
*/ -}}
{{- define "github-rate-limits-exporter.selectorLabels" -}}
app.kubernetes.io/name: {{ template "github-rate-limits-exporter.fullname" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- /*
Checksum annotations for configmaps and secrets.
*/ -}}
{{- define "github-rate-limits-exporter.annotations.checksum" -}}
{{- if .Values.grafana.enabled -}}
checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
{{- end }}
checksum/secret: {{ include (print $.Template.BasePath "/secret.yaml") . | sha256sum }}
{{- end }}
