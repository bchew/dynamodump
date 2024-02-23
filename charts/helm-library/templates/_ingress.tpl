{{/*
Kubernetes Ingress resource
*/}}
{{- define "helm-library.ingress" -}}
{{- if .Values.ingress.enabled -}}
{{- $environment := .Values.environment -}}
{{- $region := .Values.region -}}
{{- $svcPort := .Values.service.port -}}
{{- $fullName := include "helm-library.fullname" . -}}
{{- $abbrRegions := (dict "us-west-2" "usw2" "us-east-2" "use2" "eu-central-1" "euc1" "ap-northeast-1" "apne1") -}}

apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{ $fullName }}
  labels:
    {{- include "helm-library.labels" . | nindent 4 }}
  {{- with .Values.ingress.annotations }}
  annotations:
    {{- if (hasKey $.Values "externaldns") }}
    external-dns.alpha.kubernetes.io/hostname: {{ $.Values.externaldns.hostname | quote }}
    external-dns.alpha.kubernetes.io/set-identifier: {{ $.Values.externaldns.setIdentifier | quote }}
    {{- else  }}
    {{- if $.Values.ingress.dnsUseShortRecords | default false }}
    external-dns.alpha.kubernetes.io/hostname: {{ ( printf "%s-%s-w-eks-%s.gopro-platform.com" $environment $fullName (get $abbrRegions $region) ) | quote }}
    {{- else }}
    external-dns.alpha.kubernetes.io/hostname: {{ ( printf "%s-%s-weighted-eks-%s.gopro-platform.com" $environment $fullName $region ) | quote }}
    {{- end }}
    external-dns.alpha.kubernetes.io/set-identifier: "{{ $environment }}-{{ $region }}"
    {{- end }}
    {{- toYaml . | nindent 4 }}
  {{- end }}
spec:
  {{- if .Values.ingress.tls }}
  tls:
  {{- range .Values.ingress.tls }}
    - hosts:
      {{- range .hosts }}
        - {{ . | quote }}
      {{- end }}
      secretName: {{ .secretName }}
  {{- end }}
  {{- end }}
  {{- if .Values.ingress.ingressClassName }}
  ingressClassName: {{ .Values.ingress.ingressClassName }}
  {{- end }}
  rules:
    {{- include "helm-library.ingress-rules" . | indent 4 }}
{{- end }}
{{- end }}


{{/*
Ingress rules
*/}}
{{- define "helm-library.ingress-rules" -}}
{{- $top := . }}
{{- $fullName := include "helm-library.fullname" $top -}}
{{- range $rule := .Values.ingress.rules }}
{{- if $rule.host }}
- host: {{ $rule.host }}
  http:
{{- else -}}
- http:
{{ end }}
    paths:
    {{- if $top.Values.ingress.globalPaths -}}
    {{- range $globalPath := $top.Values.ingress.globalPaths -}}
    {{ $pathSpec := dict "path" $globalPath.path "pathType" $globalPath.pathType "backendService" (coalesce $globalPath.backendService $fullName) "backendServicePort" (coalesce $globalPath.backendServicePort $top.Values.service.port) "top" $top }}
    {{- include "helm-library.ingress-paths" $pathSpec | nindent 4 -}}
    {{- end -}}
    {{- end -}}
    {{ if $rule.routes }}
    {{- range $route := $rule.routes -}}
    {{ $pathSpec := dict "path" $route.path "pathType" $route.pathType "backendService" (coalesce $route.backendService $fullName) "backendServicePort" (coalesce $route.backendServicePort $top.Values.service.port) "top" $top }}
    {{- include "helm-library.ingress-paths" $pathSpec | nindent 4 -}}
    {{ end -}}
    {{- else -}}
    {{ $pathSpec := dict "path" $rule.path "pathType" $rule.pathType "top" $top }}
    {{- include "helm-library.ingress-paths" $pathSpec | nindent 4 -}}
    {{- end -}}
{{- end -}}
{{- end -}}


{{/*
Ingress paths
*/}}
{{- define "helm-library.ingress-paths" -}}
{{- if .path -}}
- path: {{ .path }}
  pathType: {{ default "ImplementationSpecific" .pathType }}
  backend:
    service:
      name: {{ .backendService }}
      port:
        number: {{ coalesce .backendServicePort .top.Values.service.port }}
{{- end -}}
{{- end -}}
