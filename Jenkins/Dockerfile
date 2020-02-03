FROM ubuntu:18.04

# Set version for the build stage
ARG PYTHON_MAJOR=3.6
ARG PYTHON_PATCH=10


# Set up locales
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update -y && \
	apt-get install -y \
		postgresql-10-postgis-2.4 \
		postgresql-server-dev-10\
		git \
		wget

# Determine which set of requirements are needed for python 3.6/7
RUN if [ "${PYTHON_MAJOR}" = "3.6" ]; \
	then \
		# 3.6
		apt-get install -y libreadline-gplv2-dev \
			libssl-dev \
			libsqlite3-dev \
			tk-dev \
			libc6-dev \
			libbz2-dev; \
	else \
		# Assume 3.7
		apt-get install -y build-essential \
			zlib1g-dev \
			libnss3-dev \
			libssl-dev \
			libreadline-dev \
			libffi-dev; \
	fi

# Download and install Python
RUN wget https://www.python.org/ftp/python/${PYTHON_MAJOR}.${PYTHON_PATCH}/Python-${PYTHON_MAJOR}.${PYTHON_PATCH}.tgz && \
	tar -xvf Python-${PYTHON_MAJOR}.${PYTHON_PATCH}.tgz && \
	cd Python-${PYTHON_MAJOR}.${PYTHON_PATCH} && \
	./configure && \
	make && \
	make install

# Create custom user
RUN useradd -ms /bin/bash -u 1000 tester

# Set up some directories for python installations
RUN mkdir -p /usr/local/lib/python${PYTHON_MAJOR}/ && \
	chown -R tester /usr/local/lib/python${PYTHON_MAJOR} && \
	chown -R tester /usr/local/bin/

# Use custom user
USER tester
