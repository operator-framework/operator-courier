ARG OMPS_VERSION=latest
FROM quay.io/operator-manifests/omps:${OMPS_VERSION}

# Install operator-courier.
USER 0
RUN pip3 install koji tox
COPY . /operator-courier
WORKDIR /operator-courier
RUN pip3 install -U .

# Re-install omps with this version of operator-courier.
WORKDIR /src
RUN pip3 install -U --no-deps .

# Override parent entrypoint(s).
ENTRYPOINT []
