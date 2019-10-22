FROM certbot/dns-route53:latest

WORKDIR /app
COPY app /app
RUN chmod +x entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
