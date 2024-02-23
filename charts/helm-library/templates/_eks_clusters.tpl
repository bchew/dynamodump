{{/*
Use the appropriate Kubernetes cluster server address for the given env, region combination.
For us-west-2 region, as this is where the ArgoCD servers are installed, the value should be https://kubernetes.default.svc
For other regions, this is basically a list of the EKS cluster API endpoints.
*/}}
{{- define "helm-library.cluster-server" -}}
{{- if eq .region "us-west-2" -}}
server: https://kubernetes.default.svc

{{- else if eq .region "us-east-2" -}}
{{- if eq .environment "qa" -}}
server: https://96A51B51D67771190C9039E8CC585CED.gr7.us-east-2.eks.amazonaws.com
{{- else if eq .environment "staging" -}}
server: https://DEECE8AE6463806576ECA8AC7C410F65.gr7.us-east-2.eks.amazonaws.com
{{- else if eq .environment "prod" -}}
server: https://DE8FD45983979FFCAEA062922BDAFFE8.yl4.us-east-2.eks.amazonaws.com
{{- else if eq .environment "infra" -}}
server: https://ABA1C584E3A40135DB5DC1B7CE23146A.yl4.us-east-2.eks.amazonaws.com
{{- end }}

{{- else if eq .region "eu-central-1" -}}
{{- if eq .environment "qa" -}}
server: https://FE37DBF3FEC421366686EB619062AC1C.gr7.eu-central-1.eks.amazonaws.com
{{- else if eq .environment "staging" -}}
server: https://D927BC5023BC35832FEA0155501F4142.gr7.eu-central-1.eks.amazonaws.com
{{- else if eq .environment "prod" -}}
server: https://B30A456E22C6164D614FBBE1C31DC4AE.sk1.eu-central-1.eks.amazonaws.com
{{- else if eq .environment "infra" -}}
server: https://2292D21913F06A2C9B1AA77EAB05A1EF.yl4.eu-central-1.eks.amazonaws.com
{{- end }}

{{- else if eq .region "ap-northeast-1" -}}
{{- if eq .environment "qa" -}}
server: https://6BFA4E779C1BABC907CB057754F0E941.gr7.ap-northeast-1.eks.amazonaws.com
{{- else if eq .environment "staging" -}}
server: https://85CCC131BEEB446CFA2B14512E550381.gr7.ap-northeast-1.eks.amazonaws.com
{{- else if eq .environment "prod" -}}
server: https://210DAFE07B334F754AEBA581D8D71CF0.sk1.ap-northeast-1.eks.amazonaws.com
{{- else if eq .environment "infra" -}}
server: https://861A276599944E6FC68C567CD16523C3.yl4.ap-northeast-1.eks.amazonaws.com
{{- end }}
{{- end }}
{{- end }}
