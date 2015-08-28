FROM registry.access.redhat.com/openshift3/python-33-rhel7
USER 0
RUN mv /usr/local/sti/assemble /usr/local/sti/_assemble
COPY assemble /usr/local/sti/assemble
# bz1255516
COPY connection.py /opt/rh/python33/root/usr/lib/python3.3/site-packages/pip/_vendor/requests/packages/urllib3/connection.py
COPY connectionpool.py /opt/rh/python33/root/usr/lib/python3.3/site-packages/pip/_vendor/requests/packages/urllib3/connectionpool.py
COPY util-connection.py /opt/rh/python33/root/usr/lib/python3.3/site-packages/pip/_vendor/requests/packages/urllib3/util/connection.py
USER 1001
