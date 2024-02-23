{{/*
Kubernetes Service resource
*/}}
{{- define "helm-library.service" -}}
apiVersion: v1
kind: Service
metadata:
  name: {{ include "helm-library.fullname" . }}
  labels:
    {{- include "helm-library.labels" . | nindent 4 }}
spec:
  type: {{ .Values.service.type }}
  {{- with .Values.service.ports }}
  ports:
    {{- toYaml . | nindent 4 }}
  {{- end }}
  selector:
    {{- include "helm-library.selectorLabels" . | nindent 4 }}
{{- end }}


{{/*
Kubernetes Service resource - for canary deploys
*/}}
{{- define "helm-library.service-canary" -}}
apiVersion: v1
kind: Service
metadata:
  name: {{ include "helm-library.fullname" . }}-canary
  labels:
    {{- include "helm-library.labels" . | nindent 4 }}
spec:
  type: {{ .Values.service.type }}
  {{- with .Values.service.ports }}
  ports:
    {{- toYaml . | nindent 4 }}
  {{- end }}
  selector:
    {{- include "helm-library.selectorLabels" . | nindent 4 }}
{{- end }}

{{/*
Kubernetes Service resource - for blue-green deploys
*/}}
{{- define "helm-library.service-preview" -}}
apiVersion: v1
kind: Service
metadata:
  name: {{ include "helm-library.fullname" . }}-preview
  labels:
    {{- include "helm-library.labels" . | nindent 4 }}
spec:
  type: {{ .Values.service.type }}
  {{- with .Values.service.ports }}
  ports:
    {{- toYaml . | nindent 4 }}
  {{- end }}
  selector:
    {{- include "helm-library.selectorLabels" . | nindent 4 }}
{{- end }}
