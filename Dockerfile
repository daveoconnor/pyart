FROM python:3.8.11-slim-buster as build

RUN apt update && apt -y upgrade && apt install -y \
    coinor-libcbc-dev \
    gcc \
    g++ \
    libbz2-dev \
    libproj-dev \
    libgdal-dev \
    libgeos-dev \
    make \
    python-dev \
    python-gdal \
    python-virtualenv \
    wget \
    zlib1g-dev
RUN pip install wheel

WORKDIR /tmp
RUN wget https://trmm-fc.gsfc.nasa.gov/trmm_gv/software/rsl/software/rsl-v1.50.tar.gz && \
    tar zxf rsl-v1.50.tar.gz && \
    cd rsl-v1.50 && \
    ./configure && \
    make install

RUN mkdir pyart
WORKDIR pyart
COPY . /tmp/pyart
SHELL ["/bin/bash", "-c"]
# Shapely is necessary to prevent a segmentation fault:
# > pyart/graph/tests/test_gridmapdisplay.py \
#  Fatal Python error: Segmentation fault
# setup.py install needed to install first to process pyx files
# need dev to get sdist etc.
RUN virtualenv -p python venv \
    && python --version \
    && source venv/bin/activate \
    && python setup.py install \
    && pip install -e .[dev] \
    && pip uninstall -y shapely \
    && pip install --no-binary :all: shapely \
    && python setup.py sdist bdist_wheel

#RUN PYART_QUIET=true python -m pytest

FROM scratch as artifact
COPY --from=build /tmp/pyart/dist /tmp/pyart/dist

ENTRYPOINT ["tail", "-f", "/dev/null"]
