FROM pytorch
#FROM ubuntu:xenial

# anaconda
#ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
#RUN apt-get update --fix-missing && apt-get install -y wget bzip2 ca-certificates \
#    libglib2.0-0 libxext6 libsm6 libxrender1 \
#    git mercurial subversion
#RUN echo 'export PATH=/opt/conda/bin:$PATH' > /etc/profile.d/conda.sh && \
#    wget --quiet https://repo.continuum.io/archive/Anaconda3-5.0.1-Linux-x86_64.sh -O ~/anaconda.sh && \
#    /bin/bash ~/anaconda.sh -b -p /opt/conda && \
#    rm ~/anaconda.sh
#ENV PATH /opt/conda/bin:$PATH
#
## torch
#RUN conda install --yes pytorch -c pytorch

# gunicorn
RUN apt-get update --fix-missing
RUN apt-get -y install gunicorn
RUN pip install gunicorn

# application itself
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN python -m nltk.downloader punkt

# additional code
COPY /codegen /codegen
ENV PYTHONPATH /codegen:$PYTHONPATH

#ENTRYPOINT ["./entrypoint.sh"]
ENTRYPOINT ["gunicorn"]
CMD ["-w", "2", "-b", ":5000", "app:app"]