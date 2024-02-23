{{- define "helm-library.externalsecret" -}}
{{- if .Values.enableESO }}
{{- if .Values.multipleExternalSecrets }}
{{- range $secrets := .Values.externalsecret }}
---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  {{- with .annotations }}
  annotations:
    {{- toYaml . | nindent 4 }}
  {{- end }}
  name: {{ .name }}
  labels:
    {{- include "helm-library.labels" $ | nindent 4 }}
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: {{ printf "%s-aws-secrets-manager-%s" .Values.environment (coalesce .Values.externalsecret.region .Values.region) }}
    kind: ClusterSecretStore
  {{- with .dataFrom }}
  dataFrom:
  {{- range $secret := . }}
  - extract:
      key: {{ $secret }}
  {{- end }}
  {{- end }}
  {{- with .data }}
  data:
  {{- range $secret := . }}
    {{- if (hasKey $secret "name") }}
  - remoteRef:
      key: {{ $secret.key }}
      property: {{ $secret.property }}
    secretKey: {{ $secret.name }}
    {{- end }}
    {{- if (hasKey $secret "remoteRef") }}
  - remoteRef:
      key: {{ $secret.remoteRef.key }}
      property: {{ $secret.remoteRef.property }}
    secretKey: {{ $secret.secretKey }}
    {{- end }}
  {{- end }}
  {{- end }}
  target:
    name: {{ .name }}
{{- end }}

{{ else }}
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  {{- with .Values.externalsecret.annotations }}
  annotations:
    {{- toYaml . | nindent 4 }}
  {{- end }}
  name: {{ .Values.externalsecret.name }}
  labels:
    {{- include "helm-library.labels" $ | nindent 4 }}
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: {{ printf "%s-aws-secrets-manager-%s" .Values.environment (coalesce .Values.externalsecret.region .Values.region) }}
    kind: ClusterSecretStore
  {{- with .Values.externalsecret.dataFrom }}
  dataFrom:
  {{- range $secret := . }}
  - extract:
      key: {{ $secret }}
  {{- end }}
  {{- end }}
  {{- with .Values.externalsecret.data }}
  data:
  {{- range $secret := . }}
    {{- if (hasKey $secret "name") }}
  - remoteRef:
      key: {{ $secret.key }}
      property: {{ $secret.property }}
    secretKey: {{ $secret.name }}
    {{- end }}
    {{- if (hasKey $secret "remoteRef") }}
  - remoteRef:
      key: {{ $secret.remoteRef.key }}
      property: {{ $secret.remoteRef.property }}
    secretKey: {{ $secret.secretKey }}
    {{- end }}
  {{- end }}
  {{- end }}
  target:
    name: {{ .Values.externalsecret.name }}
  {{- end }}

{{ else }}
{{- if .Values.multipleExternalSecrets }}
{{- range $secrets := .Values.externalsecret }}
---
apiVersion: kubernetes-client.io/v1
kind: ExternalSecret
metadata:
  {{- with .annotations }}
  annotations:
    {{- toYaml . | nindent 4 }}
  {{- end }}
  name: {{ .name }}
  labels:
    {{- include "helm-library.labels" $ | nindent 4 }}
secretDescriptor:
  backendType: secretsManager
  region: {{ .region | default $.Values.region | default "us-west-2" | quote }}
  {{- with .dataFrom }}
  dataFrom:
    {{- toYaml . | nindent 4 }}
  {{- end }}
  {{- with .data }}
  data:
    {{- toYaml . | nindent 4 }}
  {{- end }}
{{- end }}

{{ else }}
apiVersion: kubernetes-client.io/v1
kind: ExternalSecret
metadata:
  {{- with .Values.externalsecret.annotations }}
  annotations:
    {{- toYaml . | nindent 4 }}
  {{- end }}
  name: {{ .Values.externalsecret.name }}
  labels:
    {{- include "helm-library.labels" . | nindent 4 }}
secretDescriptor:
  backendType: secretsManager
  region: {{ .Values.externalsecret.region | default .Values.region | default "us-west-2" | quote }}
  {{- with .Values.externalsecret.dataFrom }}
  dataFrom:
    {{- toYaml . | nindent 4 }}
  {{- end }}
  {{- with .Values.externalsecret.data }}
  data:
    {{- toYaml . | nindent 4 }}
  {{- end }}
{{- end }}
{{- end }}
{{- end }}