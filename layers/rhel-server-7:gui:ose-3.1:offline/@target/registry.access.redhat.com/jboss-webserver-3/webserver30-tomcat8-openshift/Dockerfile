FROM registry.access.redhat.com/jboss-webserver-3/webserver30-tomcat8-openshift
ENV http_proxy http://openshift.example.com:8080/
ENV https_proxy http://openshift.example.com:8080/
USER 0
RUN mv /usr/local/s2i/assemble /usr/local/s2i/_assemble
COPY assemble /usr/local/s2i/assemble
USER 185
