---
slug: /configuration
title: Configuration
---

## Environment variables

You can configure the app at runtime using various environment variables:

- `EMISTREAM_SERVER__HOST` -
  host to run the app on
  (default: `0.0.0.0`)
- `EMISTREAM_SERVER__PORT` -
  port to run the app on
  (default: `10000`)
- `EMISTREAM_SERVER__CONCURRENCY` -
  number of concurrent requests to handle
  (default: empty, which means no limit)
- `EMISTREAM_SERVER__BACKLOG` -
  number of requests to queue
  (default: `2048`)
- `EMISTREAM_SERVER__KEEPALIVE` -
  number of seconds to keep connections alive
  (default: `5`)
- `EMISTREAM_STREAM__TIMEOUT` -
  number of seconds to wait for a connection
  (default: `60`)
- `EMISTREAM_STREAM__FORMAT` -
  format to stream in
  (default: `ogg`)
- `EMISTREAM_FUSION__HOST` -
  host to connect to
  (default: `localhost`)
- `EMISTREAM_FUSION__PORT` -
  port to connect to
  (default: `9000`)
- `EMISTREAM_EMIRECORDER__HOST` -
  host to connect to
  (default: `localhost`)
- `EMISTREAM_EMIRECORDER__PORT` -
  port to connect to
  (default: `31000`)
