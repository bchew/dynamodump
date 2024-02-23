{{/*
Kubernetes Argo Roullout resource
*/}}
{{- define "helm-library.rollout" -}}
{{- $env := ( coalesce .Values.environment "qa" ) -}}
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: {{ include "helm-library.fullname" . }}
  labels:
  {{- with .Values.labels }}
    {{- toYaml . | nindent 4 }}
  {{- end }}
    {{- include "helm-library.labels" . | nindent 4 }}
    {{- include "helm-library.ddLabels" . | indent 4 }}
spec:
  revisionHistoryLimit: {{ .Values.revisionHistoryLimit | default 5 }}
  selector:
    matchLabels:
      {{- include "helm-library.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
      {{- with .Values.selectorLabels }}
        {{- toYaml . | nindent 8 }}
      {{- end }}
        {{- include "helm-library.selectorLabels" . | nindent 8 }}
        {{- include "helm-library.ddLabels" . | indent 8 }}
    spec:
    {{- with .Values.imagePullSecrets }}
      imagePullSecrets:
        {{- toYaml . | nindent 8 }}
    {{- end }}
      serviceAccountName: {{ include "helm-library.serviceAccountName" . }}
      {{- with .Values.podSecurityContext }}
      securityContext:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.podTopologySpreadConstraints }}
      topologySpreadConstraints:
        {{- toYaml . | nindent 6 }}
      {{- end }}
      containers:
        - name: {{ .Chart.Name }}
          {{- if .Values.container }}
          {{- with .Values.container.command }}
          command:
          {{- range . }}
            - {{ . | quote }}
          {{- end }}
          {{- end }}
          {{- with .Values.container.args }}
          args:
          {{- range . }}
            - {{ . | quote }}
          {{- end }}
          {{- end }}
          {{- end }}
          {{- with .Values.securityContext }}
          securityContext:
            {{- toYaml . | nindent 12 }}
          {{- end }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          imagePullPolicy: {{ .Values.image.pullPolicy | default "IfNotPresent" }}
          env:
          {{- range $key, $value := .Values.rollout.env }}
            - name: {{ $key }}
              value: {{ $value | quote }}
          {{- end }}
          {{- if (or .Values.datadogUnifiedTagging (eq $env "qa")) }}
            - name: DD_ENV
              valueFrom:
                fieldRef:
                  fieldPath: metadata.labels['tags.datadoghq.com/env']
            - name: DD_SERVICE
              valueFrom:
                fieldRef:
                  fieldPath: metadata.labels['tags.datadoghq.com/service']
            - name: BUILD_VERSION
              valueFrom:
                fieldRef:
                  fieldPath: metadata.labels['tags.datadoghq.com/version']
            - name: DD_VERSION
              valueFrom:
                fieldRef:
                  fieldPath: metadata.labels['tags.datadoghq.com/version']
          {{- end }}
          {{- with .Values.rollout.envFrom }}
            {{- toYaml . | nindent 12 }}
          {{- end }}
          {{- with .Values.rollout.ports }}
          ports:
            {{- toYaml . | nindent 12 }}
          {{- end }}
          {{- with .Values.livenessProbe }}
          livenessProbe:
            {{- toYaml . | nindent 12 }}
          {{- end }}
          {{- with .Values.readinessProbe }}
          readinessProbe:
            {{- toYaml . | nindent 12 }}
          {{- end }}
          {{- with .Values.rollout.lifecycle }}
          lifecycle:
            {{- toYaml . | nindent 12 }}
          {{- end }}
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
          {{- with .Values.rollout.volumeMounts }}
          volumeMounts:
            {{- toYaml . | nindent 12 }}
          {{- end }}
      terminationGracePeriodSeconds: {{ .Values.terminationGracePeriodSeconds | default 30 }}
      {{- with .Values.rollout.volumes }}
      volumes:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.nodeSelector }}
      nodeSelector:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.affinity }}
      affinity:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.tolerations }}
      tolerations:
        {{- toYaml . | nindent 8 }}
      {{- end }}
  strategy:
    # For a normal rolling update, simply specify the canary strategy without steps defined.
    # The maxSurge and maxUnavailable fields can be specified. If omitted, defaults to 25% and 0
    # respectively.
    {{- with .Values.rollout.strategy }}
      {{- toYaml . | nindent 4 }}
    {{- end }}
{{- end }}
