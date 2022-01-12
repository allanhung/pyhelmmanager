from centos

RUN dnf install -y git python3 
ADD . /apps/
WORKDIR /apps
RUN pip3 install .
CMD ["tail", "-f", "/dev/null"]

