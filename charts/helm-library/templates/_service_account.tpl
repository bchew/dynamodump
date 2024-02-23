{{/*
Kubernetes ServiceAccount resource
*/}}
{{- define "helm-library.service-account" -}}
{{- if .Values.serviceAccount.create -}}
apiVersion: v1
kind: ServiceAccount
metadata:
  name: {{ include "helm-library.serviceAccountName" . }}
  labels:
{{ include "helm-library.labels" . | nindent 4 }}
  {{- with .Values.serviceAccount.annotations }}
  annotations:
    {{- toYaml . | nindent 4 }}
  {{- end -}}
{{- end -}}
{{- end -}}
