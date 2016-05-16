FROM registry.access.redhat.com/rhscl/ruby-22-rhel7
ENV SSL_CERT_FILE /tmp/ca_cert
USER 0
RUN sed -i -e '1a curl -so /tmp/ca_cert http://cacert/' /usr/libexec/s2i/assemble
USER 1001
