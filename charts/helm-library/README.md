A collection of helm templates

- [Usage](#usage)
  - [external-secret](#external-secret)
  - [rollout](#rollout)
    - [topologySpreadConstraints](#topologyspreadconstraints)
    - [Container lifecycle hooks](#container-lifecycle-hooks)
  - [HPA](#hpa)
  - [Datadog Unified Tagging](#datadog-unified-tagging)

# Usage
Add the helm-library chart to your Chart.yaml dependencies
```
dependencies:
  - name: helm-library
    version: "${VERSION}"
    repository: "https://helm.artifactory-infra.gopro-platform.com/artifactory/helm"
    condition: namespaces
```

## external-secret
Include an externalsecrets.yaml file in your chart's template folder with the following line:
```
{{ include "helm-library.externalsecret" . }}
```

Example values.yaml:

To read a single secret:
```
externalsecret:
name: svc-awards-externalsecret
annotations:
  argocd.argoproj.io/sync-wave: "-1"
dataFrom:
  - qa-awards-rdsreadwrite
  - qa-awards-secret
region: us-west-2
```

To read multiple secrets within a single object:

NOTE: Secret keys should be unique.  Any naming conflicts will use the last defined.
```
externalsecret:
name: svc-awards-externalsecret
annotations:
  argocd.argoproj.io/sync-wave: "-1"
dataFrom:
  - qa-awards-rdsreadwrite
  - qa-awards-secret
region: us-west-2
```

To create multiple externalsecrets objects:
```
multipleExternalSecrets: true
externalsecret:
- name: svc-awards-rdsreadwrite
  annotations:
    argocd.argoproj.io/sync-wave: "-1"
  dataFrom:
    - qa-awards-rdsreadwrite
  region: us-west-2
- name: svc-awards-secret
  annotations:
    argocd.argoproj.io/sync-wave: "-1"
  dataFrom:
    - qa-awards-secret
  region: us-west-2
```

## rollout
Include a rollout.yaml file in your chart's template folder with the following line:
```
{{ include "helm-library.rollout" . }}
```

### topologySpreadConstraints
Configure pod topology spread constraints included in thhe Pod API field, `spec.topologySpreadConstraints`.  Additional details available by running:
```
$ kubectl explain Pod.spec.topologySpreadConstraints
```

Example:

Multiple constraints.  Kubernetes will try to satify both constraints when scheduling a pod. `ScheduleAnyway` ensures that a pod will be scheduled even if there are conflicts.
```
podTopologySpreadConstraints:
- maxSkew: 1
  topologyKey: topology.kubernetes.io/zone
  whenUnsatisfiable: ScheduleAnyway
  labelSelector:
    matchLabels:
      app: media-service-rails
- maxSkew: 1
  topologyKey: kubernetes.io/hostname
  whenUnsatisfiable: ScheduleAnyway
  labelSelector:
    matchLabels:
      app: media-service-rails
```
### Container lifecycle hooks
Define postStop/preStop hooks in the rollouts object.  Use with `terminationGracePeriodSeconds`

Example:
```
rollout:
  lifecycle:
    preStop:
      exec:
        # SIGTERM triggers a quick exit; gracefully terminate instead
        command: ['kube/sidekiq_quiet']
```

## HPA
Scale-up and scale-down policies can be overridden. Default values will populate if no overrides are provided.

Example overrides for scale-down values:
```
downStabilizationWindowSeconds: 350
downPercent: 90
downPercentPeriodSeconds: 20
```

Policy type for scale-down can also be overridden to use TypePod. Defaults to TypePercent. Using both is also valid.

Example:
```
downPoliciesTypePercent: false
downPoliciesTypePod: true
downPods: 7
downPodsPeriodSeconds: 75
```

The use of external metrics from Datadog can be achieved in TWO MUTUALLY EXCLUSIVE ways:
### Autoscale with simple external metric without DatadogMetric
Ref: https://docs.datadoghq.com/containers/guide/cluster_agent_autoscaling_metrics/?tab=helm#autoscaling-without-datadogmetric-queries

Here we can use a single metric from Datadog to scale our Rollout. The averageValue mentioned refers to the value of the given metric divided by the number of pods.

```
autoscaling:
  min: 2
  max: 5
  extenabled: true
  extmetric: aws.sqs.approximate_number_of_messages_visible
  matchLabels:
    queuename: prod-svc-usage
  averageValue: 300
```


### Autoscale with DatadogMetric queries
Ref: https://docs.datadoghq.com/containers/guide/cluster_agent_autoscaling_metrics/?tab=helm#autoscaling-with-datadogmetric-queries

Here we can use an assortment of queries and functions.
The Datadog query reference can be found here: https://docs.datadoghq.com/dashboards/functions/interpolation/#default-zero
```
autoscaling:
  ddmetricenabled: true
  ddmetric:
    type: AverageValue
    value: 666
    query: "clamp_min(default_zero(avg:aws.kafka.messages_in_per_sec{cluster_name:staging-mor-msk,topic:appstore}), 0.01)"
```



## Datadog Unified Tagging

- `datadogUnifiedTagging` (boolean) adds additional Datadog environment variables to the deployment. This will set the service name, environment, and deployment in Datadog.
- `datadogServiceName` (optional string) allows charts to override the Datadog service name. The service name defaults to the chart full name. This is useful if multiple services should use the same name in Datadog. Example: `media-service-rails` and `media-service-rails-ro` or the `media-service-sidekiq*` charts.


## MultiApp 

This functionality enables helm-library to render multiple tightly coupled charts  from one single file in the `/apps` directory.
Applications must have the same prefix similarly to the media suite:
- media-service-rails
- media-service-rails-ro
- media-service-sidekiq
- media-service-sidekiq-hp
- media-service-sidekiq-lp

Given this list of apps we can create a single values file:

```
multiapps:
- rails
- rails-ro
- sidekiq
- sidekiq-hp

regions:
- us-west-2
- eu-central-1

environment: qa


# valueOverrides are values that take precedence over any values defined in the chart which we want to install through the Argo Application
# requires the globalapps name to be the first child under the valueOverrides key; any child the globalapps key has must be valid for the chart being installed.
valueOverrides:
  # multiapp applies value overrides to all the generated apps
  # the only additional parameter is .multiapp which referrs to each of the values from the multiapp list
  globalapps:
    externaldns:
      hostname: '{{ .environment }}-media-service{{ .multiapp }}-{{ .region }}.gopro-platform.com'
      setIdentifier: media-service{{ .multiapp }}
    image:
      tag: 666
    environmentOverride: "{{ .environment }}"
    # Used in Datadog for log/metrics filtering override from env:staging
    selectorLabels:
      env: '{{ .environment | lower }}'
    rollout:
      env:
        APP_NAME: media-service{{ .multiapp }}
    ingress:
      dnsUseShortRecords: true
      rules:
        - host: '{{ .environment }}-media-service{{ .multiapp }}-{{ .region }}.gopro-platform.com'
    namespaces:
      namespaces:
        - name: media-service{{ .multiapp }}
    regcred:
      namespace: media-service{{ .multiapp }}
    datadogUnifiedTagging: true

  # specific app names control the specifc app in the regions and environment
  sidekiq:
    rollout:
      env:
        # if we have the same key under <<globalapps>> and under a specific app
        # we'll need to accumulate them ourselves here 
        APP_NAME: media-service{{ .multiapp }}
        APP_SPECIFIC_VAR: whiskey
    autoscaling:
      max: 4

  sidekiq-hp:
    rollout:
      env:
        APP_SPECIFIC_VAR: tango
    autoscaling:
      max: 2

  rails:
    rollout:
      env:
        APP_SPECIFIC_VAR: foxtrot
    autoscaling:
      max: 6
```

THe keys unde the `globalapps` key apply to all the rendered apps. Specific app overrides can be specified by using any of the suffixes initially specified in the `multiapps` list.

This file should be placed here `/apps/media-app-of-apps/qa-multiapp.yaml`

**Note**
If we have both the `globalapps` key and an app specific key defined (i.e. `sidekiq`) we need to accumulate the same key for ourselves like we did above wtih:

```  
sidekiq:
    rollout:
      env:
        # if we have the same key under <<globalapps>> and under a specific app
        # we'll need to accumulate them ourselves here 
        APP_NAME: media-service{{ .multiapp }}
        APP_SPECIFIC_VAR: whiskey
```

With this improvement we can have templating inside values files which can be powerful