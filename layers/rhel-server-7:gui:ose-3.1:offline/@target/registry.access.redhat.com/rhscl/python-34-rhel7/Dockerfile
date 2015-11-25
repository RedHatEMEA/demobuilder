FROM registry.access.redhat.com/rhscl/python-34-rhel7
ENV http_proxy http://openshift.example.com:8080/
ENV https_proxy http://openshift.example.com:8080/
USER 0
RUN mv /usr/libexec/s2i/assemble /usr/libexec/s2i/_assemble
COPY assemble /usr/libexec/s2i/assemble
# bz1255516
COPY connection.py /opt/rh/rh-python34/root/usr/lib/python3.4/site-packages/pip/_vendor/requests/packages/urllib3/connection.py
COPY connectionpool.py /opt/rh/rh-python34/root/usr/lib/python3.4/site-packages/pip/_vendor/requests/packages/urllib3/connectionpool.py
COPY util-connection.py /opt/rh/rh-python34/root/usr/lib/python3.4/site-packages/pip/_vendor/requests/packages/urllib3/util/connection.py
USER 1001
