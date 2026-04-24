---
slug: /usage
title: Usage
---

## Checking availability

You can check if something is currently being streamed
by sending a `GET` request to the `/check` endpoint.
The response will contain the information about the event
associated with the stream, if any.

For example, you can use `curl` to do that:

```sh
curl --request GET http://localhost:10300/check
```

## Reserving the stream

You can request a reservation by sending a `POST` request to the `/reserve` endpoint.
The request body should contain the information
about the event associated with the stream
and if it should be recorded.
See the API documentation for more details.

For example, you can use `curl` to do that:

```sh
curl \
    --request POST \
    --header "Content-Type: application/json" \
    --data '{
      "event": "747c31a8-74d2-497f-ba89-cdd85b243e5d",
      "record": true
    }' \
    http://localhost:10300/reserve
```

You should receive a response containing the credentials
that you need to use to connect to the stream within a limited time.

## Sending audio

You can send live audio using the
[`SRT`](https://www.haivision.com/products/srt-secure-reliable-transport)
protocol.

You need to use a supported audio container format,
which is currently limited to [`Ogg`](https://www.xiph.org/ogg).
You can use any audio codec supported by that container format,
but we recommend using [`Opus`](https://opus-codec.org).

Remember to use the credentials you received in the previous step
to connect to the stream.

For example, you can use [`ffmpeg`](https://ffmpeg.org) for that:

```sh
ffmpeg \
    -re \
    -f lavfi \
    -i sine \
    -c libopus \
    -f ogg \
    -ar 48000 \
    -b:a 256k \
    -metadata title=test \
    -passphrase XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX \
    srt://127.0.0.1:10300
```

## Ping

You can check the status of the service by sending
either a `GET` or `HEAD` request to the `/ping` endpoint.
The service should respond with a `204 No Content` status code.

For example, you can use `curl` to do that:

```sh
curl --request HEAD --head http://localhost:10300/ping
```

## Server-Sent Events

You can subscribe to
[`Server-Sent Events (SSE)`](https://developer.mozilla.org/docs/Web/API/Server-sent_events)
by sending a `GET` request to the `/sse` endpoint.
The service should send you the events as they happen.

For example, you can use `curl` to do that:

```sh
curl --request GET --no-buffer http://localhost:10300/sse
```

## OpenAPI

You can view the [`OpenAPI`](https://www.openapis.org)
documentation made with [`Scalar`](https://scalar.com)
by navigating to the `/openapi` endpoint in your browser.

You can also download the specification in JSON format
by sending a `GET` request to the `/openapi/openapi.json` endpoint.

For example, you can use `curl` to do that:

```sh
curl --request GET http://localhost:10300/openapi/openapi.json
```
