{{/*
Common labels
*/}}
{{- define "helm-library.labels" -}}
helm.sh/chart: {{ include "helm-library.chart" . }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{ include "helm-library.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
{{- end -}}

{{/*
Datadog Unified Tagging labels
*/}}
{{- define "helm-library.ddLabels" -}}
{{- $env := ( coalesce .Values.environmentOverride .Values.environment "qa" ) -}}
{{- $fullName := include "helm-library.fullname" . -}}
{{- if (or .Values.datadogUnifiedTagging (eq $env "qa")) }}
tags.datadoghq.com/env: {{ $env }}
tags.datadoghq.com/service: {{ .Values.datadogServiceName | default $fullName | quote }}
tags.datadoghq.com/version: {{ .Values.image.tag | quote }}
{{- end }}
{{- end -}}


{{/*
Selector labels
*/}}
{{- define "helm-library.selectorLabels" -}}
{{- $env := ( coalesce .Values.environmentOverride .Values.environment "qa" ) -}}
{{- $fullName := include "helm-library.fullname" . -}}
app.kubernetes.io/name: {{ include "helm-library.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}
