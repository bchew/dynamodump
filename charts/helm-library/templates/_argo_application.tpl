{{/*
ArgoCD Application resource.
*/}}
{{- define "helm-library.argo-application" -}}
{{- $env := .environment -}}
{{- $envValues := ( coalesce .top.Values.envValuesOverride .environment ) -}}
{{- $cluster := ternary "staging" .environment (hasPrefix "staging" .environment ) -}}
{{- $account := .top.Values.account | default "gopro-platform" }}
{{- $localsuffix := ternary (print "-" .multiapp) "" ( ne .multiapp nil) }}
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: {{ $env }}-{{ .top.Chart.Name }}{{ $localsuffix }}-{{ .region }}
  namespace: argocd
  {{- with .top.Values.argocd }}
  {{- with .annotations }}
  annotations:
    {{- toYaml . | nindent 4 }}
  {{- end }}
  {{- end }}
spec:
  project: default
  source:
    chart: {{ .top.Values.spec.source.chart }}
    repoURL: {{ .top.Values.spec.source.repoURL }}
    targetRevision: {{ .top.Values.spec.source.targetRevision }}

    helm:
      valueFiles:
      - values.yaml
      - "{{ $account }}/{{ .region }}/{{ $envValues }}.yaml"
      {{- with .top.Values.valueOverrides }}
      {{- $data := dict "environment" $env "region" $.region "values" $.top.Values.valueOverrides "Template" $.Template "multiapp" $localsuffix}}
      {{ include "helm-library.application-override-values" $data }}
      {{- end }}

  destination:
    {{- if hasPrefix "staging-" $env }}
    namespace: {{ printf "%s-%s" .top.Values.spec.destination.namespace ( trimPrefix "staging-" $env ) }}
    {{ else }}
    namespace: {{ .top.Values.spec.destination.namespace }}{{ $localsuffix }}
    {{- end }}
    {{- $data := dict "environment" $cluster "region" .region }}
    {{ include "helm-library.cluster-server" $data }}
  # Sync policy
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    {{- with .top.Values.spec.syncOptions }}
    syncOptions:
      {{- toYaml . | nindent 6 }}
    {{- end }}
  ignoreDifferences:
  - group: apps
    jsonPointers:
    - /spec/template/spec/containers/{{ .top.Values.spec.source.chart }}/image
    kind: Rollout
    name: {{ $env }}-{{ .top.Chart.Name }}-{{ .region }}
{{- end }}

{{/*
Create more than one ArgoCD Application resource by iterating through all the regions associated with an environment.
e.g create the same type of Application in qa clusters across all 4 regions
*/}}
{{- define "helm-library.argo-application-generator" -}}
  {{- $top := . -}}
  {{- if .Values.environments }}
    {{- range $envs := .Values.environments }}
      {{- range $region := $top.Values.regions }}
        {{ $data := dict "region" $region "environment" $envs "top" $top "Template" $.Template}}
---
        {{ include "helm-library.argo-application" $data }}
      {{- end }}
    {{- end }}
  {{ else if .Values.multiapps}}
    {{- range $multiapp := .Values.multiapps }}
      {{- range $region := $top.Values.regions }}
        {{ $data := dict "region" $region "environment" $.Values.environment "top" $top "Template" $.Template  "multiapp" $multiapp}}
---
        {{ include "helm-library.argo-application" $data }}
      {{- end }}
    {{- end }}  
  {{ else }}
    {{- range $region := .Values.regions }}
      {{ $data := dict "region" $region "environment" $.Values.environment "top" $top }}
---
      {{ include "helm-library.argo-application" $data }}
    {{- end }}
  {{- end }}
{{- end }}

{{/*
Define helm values used for overriding chart values for the chart installed through the ArgoCD Application.
*/}}
{{- define "helm-library.application-override-values" -}}
  {{- if (hasKey .values "staging-envxx" ) }}
    {{- with (get .values "staging-envxx" ) }}
      values: |
        {{- tpl (toYaml . | nindent 8) ( dict "region" $.region "environment" $.environment "Template" $.Template ) }}
    {{- end }}
  {{- end }}
  {{- if (hasKey .values .environment) }}
    {{- with (get .values .environment) }}
        {{- tpl (toYaml . | nindent 8) ( dict "region" $.region "environment" $.environment "Template" $.Template ) }}
    {{- end }}
  {{- end }}
  {{- if (hasKey .values "globalapps" ) }}
    {{- with (get .values "globalapps" ) }}
      values: |
        {{- tpl (toYaml . | nindent 8) ( dict "region" $.region "environment" $.environment "Template" $.Template "multiapp" $.multiapp ) }}
    {{- end }}
  {{- end }}
  {{- if (hasKey .values ( trimPrefix "-" .multiapp )) }}
    {{- with (get .values ( trimPrefix "-" .multiapp )) }}
        
        {{- tpl (toYaml . | nindent 8) ( dict "region" $.region "environment" $.environment "Template" $.Template "multiapp" $.multiapp ) }}
    {{- end }}
  {{- end }}
{{- end }}