# Pulsar Message Filter Function

## Overview

This Pulsar Function receives messages from an input topic, checks if each message contains a configurable string, and forwards matching messages to a different output topic. This is a simple example of content-based message routing.

## Installation

### Prerequisites

- Apache Pulsar cluster (local or cloud-based)
- [`pulsarctl`](https://github.com/streamnative/pulsarctl) or `pulsar-admin` CLI tool installed
- `pulsar-client` for testing on command line

- [Download complete Apache Pulsar binary](https://pulsar.apache.org/download/) to get the `pulsar-admin` and `pulsar-client` command line tools
- [Install `pulsarctl`](https://github.com/streamnative/pulsarctl?tab=readme-ov-file#install-pulsarctl) / [Download `pulsarctl`](https://github.com/streamnative/pulsarctl/releases)

### Cloud Pulsar deployment

For connecting to cloud deployments with `pulsar-client` and `pulsar-admin`, it's useful a custom `cloudenv_client.conf` file with this type of content

```properties
webServiceUrl=https://host_name
brokerServiceUrl=pulsar+ssl://host_name:6651
authPlugin=org.apache.pulsar.client.impl.auth.AuthenticationToken
authParams=token:<JWT_TOKEN>
```

You can use this file by setting `PULSAR_CLIENT_CONF` environment variable to point to this file. For example:

```shell
export PULSAR_CLIENT_CONF=$PWD/cloudenv_client.conf
```

For `pulsarctl`, the configuration is different, see `pulsarctl context set --help` and `pulsarctl context use --help` for more details or [read the docs](https://github.com/streamnative/pulsarctl/blob/master/docs/en/how-to-use-context.md).

### Local Pulsar standalone

Starting

```shell
docker run -d --name pulsar-standalone -e PULSAR_STANDALONE_USE_ZOOKEEPER=1 -p 8080:8080 -p 6650:6650 apachepulsar/pulsar:latest /pulsar/bin/pulsar standalone
```

Stopping

```shell
docker stop pulsar-standalone
```

Removing

```shell
docker rm pulsar-standalone
```

Logs

```shell
docker logs -f pulsar-standalone
```

### Installation steps

#### 1. Create the necessary topics with desired configuration

```shell
pulsarctl topics create persistent://public/default/input-topic 0
pulsarctl topics create persistent://public/default/filtered-output-topic 0
```

or with `pulsar-admin`

```shell
pulsar-admin topics create persistent://public/default/input-topic
pulsar-admin topics create persistent://public/default/filtered-output-topic
```

#### 2. Deploy the function

Deploy using the configuration file:

```shell
pulsarctl functions create --function-config-file message-filter-config.yaml
```

or with `pulsar-admin`

```shell
pulsar-admin functions create --function-config-file message-filter-config.yaml
```


## Testing

### 1. Start a consumer to see filtered messages

```shell
pulsar-client consume persistent://public/default/filtered-output-topic -s "test-sub" -n 0
```

### 2. Send test messages to the input topic

In a separate terminal, send messages:

```shell
# This message contains the filter string "magic" and should be forwarded
pulsar-client produce persistent://public/default/input-topic \
  -m "This is a test message containing a magic word"

# This message doesn't contain "magic" and should NOT be forwarded
pulsar-client produce persistent://public/default/input-topic \
  -m "Hello world"
```

### 3. Verify results

Only messages containing the filter string ("magic" by default) should appear in the consumer output.

## Customizing

### Change the filter string

To change the string that triggers message forwarding:

```shell
pulsarctl functions update \
  --tenant public \
  --namespace default \
  --name message-filter \
  --user-config '{"destinationTopic":"persistent://public/default/filtered-output-topic","filterString":"warning"}'
```

This updates the function to forward messages containing "warning" instead of "magic".

### Change the destination topic

If you want to route messages to a different output topic:

```shell
# First create the new topic
pulsarctl topics create persistent://public/default/new-output-topic 0

# Update the function configuration
pulsarctl functions update \
  --tenant public \
  --namespace default \
  --name message-filter \
  --user-config '{"destinationTopic":"persistent://public/default/new-output-topic","filterString":"magic"}'
```

## Monitoring and Management

### View function status

```shell
pulsarctl functions status \
  --tenant public \
  --namespace default \
  --name message-filter
```

### View function stats

```shell
pulsarctl functions stats \
  --tenant public \
  --namespace default \
  --name message-filter
```

This command shows metrics including:

- Number of messages processed
- Processing latency
- Custom metrics recorded by the function

### Restart the function

```shell
pulsarctl functions restart \
  --tenant public \
  --namespace default \
  --name message-filter
```

### Stop the function

```shell
pulsarctl functions stop \
  --tenant public \
  --namespace default \
  --name message-filter
```

### Delete the function

```shell
pulsarctl functions delete \
  --tenant public \
  --namespace default \
  --name message-filter
```

## Troubleshooting

### Function doesn't start

Check the function status:

```shell
pulsarctl functions status --tenant public --namespace default --name message-filter
```

Check the function logs (local standalone):

```shell
docker exec -it pulsar-standalone tail -n 500 -f logs/functions/public/default/message-filter/message-filter-0.log
```

For StreamNative Cloud, you can find the function logs in the Web UI.