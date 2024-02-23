{{- define "helm-library.ddmetric" -}}
{{- if .Values.autoscaling.ddmetricenabled }}
apiVersion: datadoghq.com/v1alpha1
kind: DatadogMetric
metadata:
  name: {{ include "helm-library.fullname" . }}-ddmetric
spec:
  query: {{ .Values.autoscaling.ddmetric.query}}
{{- end }}
{{- end }}