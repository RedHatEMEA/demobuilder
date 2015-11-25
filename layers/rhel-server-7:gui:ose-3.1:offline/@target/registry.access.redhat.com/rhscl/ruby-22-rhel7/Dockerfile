FROM registry.access.redhat.com/rhscl/ruby-22-rhel7
ENV http_proxy http://openshift.example.com:8080/
ENV https_proxy http://openshift.example.com:8080/
USER 0
RUN mv /usr/libexec/s2i/assemble /usr/libexec/s2i/_assemble
COPY assemble /usr/libexec/s2i/assemble
USER 1001
