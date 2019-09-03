ARG OMPS_VERSION=latest
FROM quay.io/operator-manifests/omps:${OMPS_VERSION}

# Install operator-courier.
USER 0
RUN pip3 install koji
COPY . /repo
WORKDIR /repo
RUN pip3 install -U .
RUN rm -rf /repo

# Re-install omps with this version of operator-courier.
WORKDIR /src
RUN pip3 install -U --no-deps .

USER 1001
ENTRYPOINT docker/install-ca.sh && gunicorn-3 --workers ${WORKERS_NUM} --timeout ${WORKER_TIMEOUT} --bind 0.0.0.0:8080 --access-logfile=- --enable-stdio-inheritance omps.app:app
