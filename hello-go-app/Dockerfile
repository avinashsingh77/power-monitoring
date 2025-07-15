FROM golang:1.21-alpine AS builder
# Dummy change
WORKDIR /app
COPY go.mod ./
COPY . .
RUN go mod download
RUN CGO_ENABLED=0 go build -o hello-app cmd/main.go

FROM alpine:latest
RUN adduser -D appuser
WORKDIR /app
COPY --from=builder /app/hello-app .
USER appuser
EXPOSE 8080
CMD ["./hello-app"]