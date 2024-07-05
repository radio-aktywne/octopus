---
slug: /configuration
title: Configuration
---

## Environment variables

You can configure the app at runtime using various environment variables:

- `EMISTREAM__SERVER__HOST` -
  host to run the server on
  (default: `0.0.0.0`)
- `EMISTREAM__SERVER__PORTS__HTTP` -
  port to listen on for HTTP requests
  (default: `10000`)
- `EMISTREAM__SERVER__PORTS__SRT` -
  port to listen on for SRT streams
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
- `EMISTREAM__EMIRECORDS__HTTP__SCHEME` -
  scheme of the HTTP API of the emirecords service
  (default: `http`)
- `EMISTREAM__EMIRECORDS__HTTP__HOST` -
  host of the HTTP API of the emirecords service
  (default: `localhost`)
- `EMISTREAM__EMIRECORDS__HTTP__PORT` -
  port of the HTTP API of the emirecords service
  (default: `31000`)
- `EMISTREAM__EMIRECORDS__HTTP__PATH` -
  path of the HTTP API of the emirecords service
  (default: ``)
- `EMISTREAM__EMIRECORDS__SRT__HOST` -
  host of the SRT stream of the emirecords service
  (default: `localhost`)
- `EMISTREAM__EMIRECORDS__SRT__PORT` -
  port of the SRT stream of the emirecords service
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
