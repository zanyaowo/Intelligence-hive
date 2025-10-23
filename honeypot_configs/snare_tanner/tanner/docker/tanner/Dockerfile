FROM alpine:3.15

# Include dist
ADD docker/tanner/dist/ /root/dist/

# Copy modified files
COPY tanner/api/api.py /tmp/api.py
COPY tanner/web/server.py /tmp/web_server.py
COPY sessions_session_analyzer.py /tmp/session_analyzer.py
COPY sessions_session_manager.py /tmp/session_manager.py
COPY sessions_session.py /tmp/session.py
COPY server.py /tmp/main_server.py

# Setup apt
RUN apk -U --no-cache add \
               build-base \
               git \
               libcap \
               libffi-dev \
               libressl-dev \
               linux-headers \
               py3-yarl \
               python3 \
               python3-dev \
               py3-pip && \
# Setup Tanner
    git clone --depth=1 https://github.com/mushorg/tanner /opt/tanner && \
    cp /root/dist/config.yaml /opt/tanner/tanner/data/ && \
    cp /tmp/api.py /opt/tanner/tanner/api/api.py && \
    cp /tmp/web_server.py /opt/tanner/tanner/web/server.py && \
    cp /tmp/session_analyzer.py /opt/tanner/tanner/sessions/session_analyzer.py && \
    cp /tmp/session_manager.py /opt/tanner/tanner/sessions/session_manager.py && \
    cp /tmp/session.py /opt/tanner/tanner/sessions/session.py && \
    cp /tmp/main_server.py /opt/tanner/tanner/server.py && \
    cd /opt/tanner/ && \
    python3 -m venv tanner-env && \
    source /opt/tanner/tanner-env/bin/activate && \
    pip install --upgrade pip && \
    pip3 install --no-cache-dir wheel && \
    pip3 install --no-cache-dir -r requirements.txt && \
    python3 setup.py install && \
    cd / && \
# Setup configs, user, groups
    chown -R nobody:nobody /opt/tanner && \
# Clean up
    apk del --purge \
            build-base \
            linux-headers \
            python3-dev && \
    rm -rf /root/* && \
    rm -rf /tmp/* /var/tmp/* && \
    rm -rf /var/cache/apk/*

# Start tanner
USER nobody:nobody
WORKDIR /opt/tanner
CMD ["/opt/tanner/tanner-env/bin/tanner", "--config", "/opt/tanner/tanner/data/config.yaml"]

