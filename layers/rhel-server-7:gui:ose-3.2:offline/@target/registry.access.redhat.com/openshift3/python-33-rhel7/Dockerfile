FROM registry.access.redhat.com/openshift3/python-33-rhel7
ENV http_proxy http://openshift.example.com:8080/
ENV https_proxy http://openshift.example.com:8080/
ENV no_proxy localhost
USER 0
RUN sed -i -e 's!pip install!pip install --cert /tmp/ca_cert!; 1a curl -so /tmp/ca_cert http://cacert/' /usr/libexec/s2i/assemble
# bz1255516
COPY connection.py /opt/rh/python33/root/usr/lib/python3.3/site-packages/pip/_vendor/requests/packages/urllib3/connection.py
COPY connectionpool.py /opt/rh/python33/root/usr/lib/python3.3/site-packages/pip/_vendor/requests/packages/urllib3/connectionpool.py
COPY util-connection.py /opt/rh/python33/root/usr/lib/python3.3/site-packages/pip/_vendor/requests/packages/urllib3/util/connection.py
USER 1001
