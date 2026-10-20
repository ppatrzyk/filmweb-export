LABEL org.opencontainers.image.source=https://github.com/ppatrzyk/filmweb-export

FROM docker.io/library/python:3.15.0-trixie AS python-build

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
WORKDIR /filmweb
COPY . /filmweb
RUN pip3 install .

FROM docker.io/library/python:3.15.0-slim-trixie AS final-image

WORKDIR /filmweb
COPY --from=python-build /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

CMD ["filmweb", "--help"]
