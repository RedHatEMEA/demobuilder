FROM registry.access.redhat.com/jboss-webserver-3/webserver30-tomcat7-openshift
ENV http_proxy http://openshift.example.com:8080/
ENV https_proxy http://openshift.example.com:8080/
ENV no_proxy localhost
USER 0
RUN sed -i -e 's!mvn !mvn -Djavax.net.ssl.trustStore=/tmp/trust.jks -Djavax.net.ssl.trustStorePassword=password !' /usr/local/s2i/assemble
RUN mv /usr/local/s2i/assemble /usr/local/s2i/_assemble
COPY assemble /usr/local/s2i/assemble
USER 185
