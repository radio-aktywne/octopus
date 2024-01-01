---
slug: /configuration
title: Configuration
---

## Environment variables

You can configure the app at runtime using various environment variables:

- `EMISTREAM__SERVER__HOST` -
  host to run the server on
  (default: `0.0.0.0`)
- `EMISTREAM__SERVER__PORT` -
  port to run the server on
  (default: `10000`)
- `EMISTREAM__STREAM_HOST` -
  host to listen on for connections
  (default: `0.0.0.0`)
- `EMISTREAM__STREAM__PORT` -
  port to listen on for connections
  (default: `10000`)
- `EMISTREAM__STREAM__TIMEOUT` -
  time after which a stream will be stopped if no connections are made
  (default: `PT1M`)
- `EMISTREAM__STREAM__WINDOW` -
  time window to search for event instances around the current time
  (default: `PT1H`)
- `EMISTREAM__FUSION__HOST` -
  host to connect to
  (default: `localhost`)
- `EMISTREAM__FUSION__PORT` -
  port to connect to
  (default: `9000`)
- `EMISTREAM__EMIRECORDER__HOST` -
  host to connect to
  (default: `localhost`)
- `EMISTREAM__EMIRECORDER__PORT` -
  port to connect to
  (default: `31000`)
- `EMISTREAM__EMISHOWS__HOST` -
  host to connect to
  (default: `localhost`)
- `EMISTREAM__EMISHOWS__PORT` -
  port to connect to
  (default: `35000`)
