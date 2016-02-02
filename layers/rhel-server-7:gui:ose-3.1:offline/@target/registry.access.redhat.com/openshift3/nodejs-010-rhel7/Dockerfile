FROM registry.access.redhat.com/openshift3/nodejs-010-rhel7
ENV http_proxy http://openshift.example.com:8080/
ENV https_proxy http://openshift.example.com:8080/
ENV no_proxy localhost
USER 0
RUN sed -i -e '1a curl -so /tmp/ca_cert http://cacert/; npm config set cafile /tmp/ca_cert' /usr/libexec/s2i/assemble
USER 1001
