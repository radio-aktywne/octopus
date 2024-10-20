---
slug: /config
title: Configuration
---

## Environment variables

You can configure the service at runtime using various environment variables:

- `OCTOPUS__SERVER__HOST` -
  host to run the server on
  (default: `0.0.0.0`)
- `OCTOPUS__SERVER__PORTS__HTTP` -
  port to listen for HTTP requests on
  (default: `10000`)
- `OCTOPUS__SERVER__PORTS__SRT` -
  port to listen for SRT connections on
  (default: `10000`)
- `OCTOPUS__SERVER__TRUSTED` -
  trusted IP addresses
  (default: `*`)
- `OCTOPUS__STREAM__TIMEOUT` -
  time after which a stream will be stopped if no connections are made
  (default: `PT1M`)
- `OCTOPUS__STREAM__WINDOW` -
  time window to search for event instances around the current time
  (default: `PT1H`)
- `OCTOPUS__DINGO__SRT__HOST` -
  host of the SRT stream of the dingo service
  (default: `localhost`)
- `OCTOPUS__DINGO__SRT__PORT` -
  port of the SRT stream of the dingo service
  (default: `9000`)
- `OCTOPUS__GECKO__HTTP__SCHEME` -
  scheme of the HTTP API of the gecko service
  (default: `http`)
- `OCTOPUS__GECKO__HTTP__HOST` -
  host of the HTTP API of the gecko service
  (default: `localhost`)
- `OCTOPUS__GECKO__HTTP__PORT` -
  port of the HTTP API of the gecko service
  (default: `31000`)
- `OCTOPUS__GECKO__HTTP__PATH` -
  path of the HTTP API of the gecko service
  (default: ``)
- `OCTOPUS__BEAVER__HTTP__SCHEME` -
  scheme of the HTTP API of the beaver service
  (default: `http`)
- `OCTOPUS__BEAVER__HTTP__HOST` -
  host of the HTTP API of the beaver service
  (default: `localhost`)
- `OCTOPUS__BEAVER__HTTP__PORT` -
  port of the HTTP API of the beaver service
  (default: `35000`)
- `OCTOPUS__BEAVER__HTTP__PATH` -
  path of the HTTP API of the beaver service
  (default: ``)
- `OCTOPUS__DEBUG` -
  enable debug mode
  (default: `false`)
