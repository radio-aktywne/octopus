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
- `EMISTREAM__STREAM__HOST` -
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
- `EMISTREAM__FUSION__SRT__HOST` -
  host of the SRT stream of the fusion service
  (default: `localhost`)
- `EMISTREAM__FUSION__SRT__PORT` -
  port of the SRT stream of the fusion service
  (default: `9000`)
- `EMISTREAM__EMIRECORDER__HTTP__SCHEME` -
  scheme of the HTTP API of the emirecorder service
  (default: `http`)
- `EMISTREAM__EMIRECORDER__HTTP__HOST` -
  host of the HTTP API of the emirecorder service
  (default: `localhost`)
- `EMISTREAM__EMIRECORDER__HTTP__PORT` -
  port of the HTTP API of the emirecorder service
  (default: `31000`)
- `EMISTREAM__EMIRECORDER__HTTP__PATH` -
  path of the HTTP API of the emirecorder service
  (default: ``)
- `EMISTREAM__EMIRECORDER__SRT__HOST` -
  host of the SRT stream of the emirecorder service
  (default: `localhost`)
- `EMISTREAM__EMIRECORDER__SRT__PORT` -
  port of the SRT stream of the emirecorder service
  (default: `31000`)
- `EMISTREAM__EMISHOWS__HTTP__SCHEME` -
  scheme of the HTTP API of the emishows service
  (default: `http`)
- `EMISTREAM__EMISHOWS__HTTP__HOST` -
  host of the HTTP API of the emishows service
  (default: `localhost`)
- `EMISTREAM__EMISHOWS__HTTP__PORT` -
  port of the HTTP API of the emishows service
  (default: `35000`)
- `EMISTREAM__EMISHOWS__HTTP__PATH` -
  path of the HTTP API of the emishows service
  (default: ``)
