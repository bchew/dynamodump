{{- define "helm-library.hpa" -}}
{{- if .Values.autoscaling.enabled }}
apiVersion: {{ ternary "autoscaling/v2" "autoscaling/v2beta2" (semverCompare ">=1.23.0-0" .Capabilities.KubeVersion.Version) }}
kind: HorizontalPodAutoscaler
metadata:
  name: {{ include "helm-library.fullname" . }}
spec:
  maxReplicas: {{ .Values.autoscaling.max }}
  minReplicas: {{ .Values.autoscaling.min }}
  behavior:
    scaleDown:
      stabilizationWindowSeconds: {{ .Values.autoscaling.downStabilizationWindowSeconds | default 300 }}
      policies:
      {{- if .Values.autoscaling.downPoliciesTypePercent | default true }}
      - type: Percent
        value: {{ .Values.autoscaling.downPercent | default 100 }}
        periodSeconds: {{ .Values.autoscaling.downPercentPeriodSeconds | default 15 }}
      {{- end }}
      {{- if .Values.autoscaling.downPoliciesTypePod | default false }}
      - type: Pods
        value: {{ .Values.autoscaling.downPods | default 5 }}
        periodSeconds: {{ .Values.autoscaling.downPodsPeriodSeconds | default 60 }}
      {{- end }}
    scaleUp:
      stabilizationWindowSeconds: {{ .Values.autoscaling.upStabilizationWindowSeconds | default 0 }}
      policies:
      - type: Percent
        value: {{ .Values.autoscaling.upPercent | default 80 }}
        periodSeconds: {{ .Values.autoscaling.upPercentPeriodSeconds | default 15 }}
      - type: Pods
        value: {{ .Values.autoscaling.upPods | default 4 }}
        periodSeconds: {{ .Values.autoscaling.upPodsPeriodSeconds | default 15 }}
      selectPolicy: Max
  scaleTargetRef:
    apiVersion: argoproj.io/v1alpha1
    kind: Rollout
    name: {{ include "helm-library.fullname" . }}
  metrics:
  {{- if .Values.autoscaling.extenabled }}
  - type: External
    external:
      metric: 
        name: {{ .Values.autoscaling.extmetric }}
        selector:
          matchLabels: 
            {{- range $key, $value := .Values.autoscaling.matchLabels }}
            {{ $key  }}: {{ $value }}
            {{- end  }}
      target:
        type: AverageValue
        averageValue: {{ .Values.autoscaling.averageValue}}
  {{- else if .Values.autoscaling.ddmetricenabled | default false }}
  - type: External
    external:
      metric: 
        name: 'datadogmetric@{{ .Release.Namespace }}:{{ include "helm-library.fullname" . }}-ddmetric'
      target:
        type: {{ .Values.autoscaling.ddmetric.type| default "AverageValue"}}
        {{- if eq .Values.autoscaling.ddmetric.type "AverageValue"}}
        averageValue: {{ .Values.autoscaling.ddmetric.value}}
        {{- else if eq .Values.autoscaling.ddmetric.type "Value" }}
        value: {{ .Values.autoscaling.ddmetric.value}}
        {{- end}}
  {{- else }}
  {{- if .Values.autoscaling.targetMemory }}
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: {{ .Values.autoscaling.targetMemory }}
  {{- end }}
  {{- if .Values.autoscaling.targetCPU }}
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: {{ .Values.autoscaling.targetCPU }}
  {{- end }}
  {{- end }}
{{- end }}
{{- end }}
