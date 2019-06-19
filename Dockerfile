FROM python:3.7.3-slim
MAINTAINER Justin L Lorieau <justin@lorieau.com>
COPY . /disseminate
WORKDIR /disseminate
RUN apt-get -y update && apt-get install -y \
    gcc \
    texlive-latex-base \
    texlive-latex-extra \
    pdf2svg \
    librsvg2-bin \
    asymptote
RUN pip install pytest
RUN python setup.py install

