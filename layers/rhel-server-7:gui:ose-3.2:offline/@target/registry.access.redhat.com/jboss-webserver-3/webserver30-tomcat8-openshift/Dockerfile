FROM registry.access.redhat.com/jboss-webserver-3/webserver30-tomcat8-openshift
USER 0
RUN sed -i -e 's!mvn !mvn -Djavax.net.ssl.trustStore=/tmp/trust.jks -Djavax.net.ssl.trustStorePassword=password !' /usr/local/s2i/assemble
RUN mv /usr/local/s2i/assemble /usr/local/s2i/_assemble
COPY assemble /usr/local/s2i/assemble
USER 185
