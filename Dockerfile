from rockylinux

RUN dnf install -y git python3 python3-devel python3-requests gcc make 
ADD . /apps/
WORKDIR /apps
RUN pip3 install .
CMD ["tail", "-f", "/dev/null"]

