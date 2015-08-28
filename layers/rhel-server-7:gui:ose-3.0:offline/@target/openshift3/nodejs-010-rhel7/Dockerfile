FROM registry.access.redhat.com/openshift3/nodejs-010-rhel7
USER 0
RUN mv /usr/local/sti/assemble /usr/local/sti/_assemble
COPY assemble /usr/local/sti/assemble
USER 1001
