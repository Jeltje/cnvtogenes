FROM ubuntu:14.04

MAINTAINER Jeltje van Baren, jeltje.van.baren@gmail.com

RUN apt-get update && apt-get install -y \
	python-pip 


RUN pip install intervaltree
ADD  cnvToGenes.py /usr/local/bin/

RUN mkdir /data
WORKDIR /data

ENTRYPOINT ["python", "/usr/local/bin/cnvToGenes.py"]
CMD ["--help"]

# And clean up
RUN apt-get clean && rm -rf /var/lib/apt/lists/*


