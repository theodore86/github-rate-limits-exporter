# Github Rate Limit Prometheus Exporter Helm Chart

This helm chart helps to install and configure the exporter on Kubernetes clusters.

The helm chart itself is a simplified version of a generated helm chart for 'any' service.

Values which can be configured can be viewed [here](values.yaml)

## Get Repo Charts

```sh
helm pull oci://registry-1.docker.io/theodore86/github-rate-limits-exporter [FLAGS]
```

## Install Chart

```sh
helm upgrade --install \
  [RELEASE NAME] grl-exporter/github-rate-limits-prometheus-exporter \
    [FLAGS]
```

## Uninstall Chart

```sh
helm uninstall [RELEASE NAME]
```

## Application specific configuration

GitHub PAT:

```yaml
github:
  accountName: theodore86
  authType: pat
  token: 34ghhj$2rfg # Github personal access token
```

GitHub App:

```yaml
github:
  accountName: theodore86
  authType: app
  appID: "123456" # GitHub applicaiton ID
  installationID: "12345678" # GitHub App installation ID
  mountPath: /secret # name of a secret which stores key.pem
  privateKey: | # private key (could be base64 encoded) will be mounted
    -----BEGIN RSA PRIVATE KEY-----
    MIIEogIBAAKCAQEAuLYmbXnFr2bSA8VG8kS8LemXdHif4JE1fNZTF2R9sKED43yE
    ...
    ...
    ...
    GB89a7noqLX9w1sXhzmRPuROO4YsKv4H0Bfaq6mZSP+Bc+LT9Pg=
    -----END RSA PRIVATE KEY-----
```

## Example Values file

```yaml
github:
  accountName: theodore86
  authType: pat
  token: 3fgh%65hghhhj

image:
  # Overrides the image tag whose default is the chart version.
  tag: "v0.7.1"
```
