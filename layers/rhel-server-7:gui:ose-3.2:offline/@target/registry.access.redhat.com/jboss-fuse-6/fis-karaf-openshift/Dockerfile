FROM registry.access.redhat.com/fis-karaf-openshift
USER 0
RUN sed -i -e 's!mvn !mvn -Dhttp.proxyHost=openshift.example.com -Dhttp.proxyPort=8080 -Dhttps.proxyHost=openshift.example.com -Dhttps.proxyPort=8080 -Djavax.net.ssl.trustStore=/tmp/trust.jks -Djavax.net.ssl.trustStorePassword=password !' /usr/local/s2i/assemble
RUN mv /usr/local/s2i/assemble /usr/local/s2i/_assemble
COPY assemble /usr/local/s2i/assemble
USER 185
