FROM registry.access.redhat.com/jboss-eap-6/eap-openshift:6.4
USER 0
RUN mv /usr/local/sti/assemble /usr/local/sti/_assemble
COPY assemble /usr/local/sti/assemble
USER 185
