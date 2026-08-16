{{/*
Expand the name of the chart.
*/}}
{{- define "investment-platform.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited.
If release name contains the chart name it will be used as a full name.
*/}}
{{- define "investment-platform.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart label — used in the helm.sh/chart annotation.
*/}}
{{- define "investment-platform.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels applied to every resource.
*/}}
{{- define "investment-platform.labels" -}}
helm.sh/chart: {{ include "investment-platform.chart" . }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/part-of: investment-platform
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}

{{/*
Selector labels for a given component.
Usage: {{ include "investment-platform.selectorLabels" (dict "component" "backend" "context" .) }}
*/}}
{{- define "investment-platform.selectorLabels" -}}
app.kubernetes.io/name: {{ .component }}
app.kubernetes.io/instance: {{ .context.Release.Name }}
{{- end }}

{{/*
Full set of labels for a given component (common + selector).
*/}}
{{- define "investment-platform.componentLabels" -}}
{{ include "investment-platform.labels" .context }}
{{ include "investment-platform.selectorLabels" . }}
app.kubernetes.io/component: {{ .component }}
{{- end }}

{{/*
Service account name helper.
*/}}
{{- define "investment-platform.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "investment-platform.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Database host — uses the Bitnami sub-chart service name by default.
When postgresql.enabled is false, host comes from externalDatabase.host.
*/}}
{{- define "investment-platform.databaseHost" -}}
{{- if .Values.postgresql.enabled }}
{{- printf "%s-postgresql" .Release.Name }}
{{- else }}
{{- .Values.externalDatabase.host }}
{{- end }}
{{- end }}

{{/*
Database port.
*/}}
{{- define "investment-platform.databasePort" -}}
{{- if .Values.postgresql.enabled }}
{{- .Values.postgresql.primary.service.ports.postgresql | default 5432 }}
{{- else }}
{{- .Values.externalDatabase.port | default 5432 }}
{{- end }}
{{- end }}

{{/*
Database name.
*/}}
{{- define "investment-platform.databaseName" -}}
{{- if .Values.postgresql.enabled }}
{{- .Values.postgresql.auth.database }}
{{- else }}
{{- .Values.externalDatabase.database }}
{{- end }}
{{- end }}

{{/*
Database user.
*/}}
{{- define "investment-platform.databaseUser" -}}
{{- if .Values.postgresql.enabled }}
{{- .Values.postgresql.auth.username }}
{{- else }}
{{- .Values.externalDatabase.username }}
{{- end }}
{{- end }}

{{/*
Construct the async DATABASE_URL for the Python backend.
*/}}
{{- define "investment-platform.databaseUrl" -}}
{{- printf "postgresql+asyncpg://%s@%s:%v/%s"
    (include "investment-platform.databaseUser" .)
    (include "investment-platform.databaseHost" .)
    (include "investment-platform.databasePort" .)
    (include "investment-platform.databaseName" .)
}}
{{- end }}

{{/*
Construct the sync DATABASE_URL for n8n (uses plain postgres:// scheme).
*/}}
{{- define "investment-platform.n8nDatabaseUrl" -}}
{{- printf "postgresql://%s@%s:%v/%s"
    (include "investment-platform.databaseUser" .)
    (include "investment-platform.databaseHost" .)
    (include "investment-platform.databasePort" .)
    (include "investment-platform.n8nDatabaseName" .)
}}
{{- end }}

{{/*
n8n database name (separate from the backend DB).
*/}}
{{- define "investment-platform.n8nDatabaseName" -}}
{{- .Values.n8n.database.name | default "n8n" }}
{{- end }}

{{/*
Backend service URL used by n8n (Kubernetes DNS).
In split-app mode, uses global.backendServiceHost to reach the separate backend app.
*/}}
{{- define "investment-platform.backendServiceUrl" -}}
{{- printf "http://%s:%v" .Values.global.backendServiceHost (.Values.backend.service.port | default 8000) }}
{{- end }}

{{/*
Image helper — builds the full image reference.
Usage: {{ include "investment-platform.image" .Values.backend.image }}
*/}}
{{- define "investment-platform.image" -}}
{{- if .digest }}
{{- printf "%s/%s@%s" .registry .repository .digest }}
{{- else }}
{{- printf "%s/%s:%s" .registry .repository (.tag | default "latest") }}
{{- end }}
{{- end }}
