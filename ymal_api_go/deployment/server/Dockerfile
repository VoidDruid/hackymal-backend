FROM golang:alpine as builder

RUN apk update && apk add --no-cache git ca-certificates tzdata && update-ca-certificates

WORKDIR /opt/app

COPY src/go.mo[d] .
COPY src/go.su[m] .

RUN go get -d -v ./...
RUN go install -v ./...

COPY src .

RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build \
    -ldflags='-w -s -extldflags "-static"' -a \
    -o /opt/app/bin/ymal .

FROM scratch
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=builder /opt/app/bin/ymal /opt/app/bin/ymal

CMD ["/opt/app/bin/ymal"]

EXPOSE 8000
