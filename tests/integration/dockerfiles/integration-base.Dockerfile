FROM fedora:29

RUN dnf install -y --setopt=install_weak_deps=False --best \
    git \
    python3-tox \
    python3-coveralls \
    && dnf -y clean all \
    && rm -rf /tmp/*
