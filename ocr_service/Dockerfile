FROM mambaorg/micromamba:0.21.2
COPY --chown=$MAMBA_USER:$MAMBA_USER environment.yml /tmp/env.yaml
RUN micromamba install -y -f /tmp/env.yaml && \
    micromamba clean --all --yes

COPY worker.py .

CMD [ "python", "worker.py" ]