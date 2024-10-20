---
slug: /usage
title: Usage
---

## Checking availability

You can check if something is currently being streamed
by sending a `GET` request to the `/check` endpoint.
The response will contain the information about the event
associated with the stream, if any.

For example, you can use [`curl`](https://curl.se) to do that:

```sh
curl \
    --request GET \
    http://localhost:10000/check
```

## Reserving the stream

You can request a reservation by sending a `POST` request to the `/reserve` endpoint.
The request body should contain the information
about the event associated with the stream
and if it should be recorded.
See the API documentation for more details.

For example, you can use [`curl`](https://curl.se) to do that:

```sh
curl \
    --request POST \
    --header "Content-Type: application/json" \
    --data '{
      "event": "747c31a8-74d2-497f-ba89-cdd85b243e5d",
      "record": true
    }' \
    http://localhost:10000/reserve
```

You should receive a response containing the credentials and port number
that you can use to connect to the stream and start sending audio.
The credentials are only valid for a limited time.

## Sending audio

You can send audio to record using the
[`SRT`](https://www.haivision.com/products/srt-secure-reliable-transport)
protocol.

As the audio codec and container,
by default you should use [`Opus`](https://opus-codec.org) and
[`Ogg`](https://www.xiph.org/ogg) respectively.
They are free and open source, focused on quality and efficiency,
and support embedding metadata into the stream.

Remember to use the token and port you received in the previous step
to connect to the stream.

For example, you can use [`Liquidsoap`](https://www.liquidsoap.info) for that:

```sh
liquidsoap \
    'output.srt(
        host="127.0.0.1",
        port=10000,
        passphrase="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        %ogg(%opus),
        sine()
    )'
```

Alternatively, you can use [`ffmpeg`](https://ffmpeg.org) to do the same:

```sh
ffmpeg \
    -re \
    -f lavfi \
    -i sine \
    -c libopus \
    -f ogg \
    -passphrase "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" \
    srt://127.0.0.1:10000
```

## Ping

You can check the status of the service by sending
either a `GET` or `HEAD` request to the `/ping` endpoint.
The service should respond with a `204 No Content` status code.

For example, you can use `curl` to do that:

```sh
curl \
    --request HEAD \
    --head \
    http://localhost:10000/ping
```

## Server-Sent Events

You can subscribe to the Server-Sent Events (SSE) by sending
a `GET` request to the `/sse` endpoint.
The service will send you the events as they happen.

For example, you can use `curl` to do that:

```sh
curl \
    --request GET \
    --no-buffer \
    http://localhost:10000/sse
```
