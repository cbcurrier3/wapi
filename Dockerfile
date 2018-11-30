FROM centos:latest
MAINTAINER The CentOS Project <cloud-ops@centos.org>
LABEL Vendor="CentOS" \
      License=GPLv2 \
      Version=2.4.6-40


RUN yum -y --setopt=tsflags=nodocs update && \
    yum -y --setopt=tsflags=nodocs install httpd mod_ssl php && \
    yum -y --setopt=tsflags=nodocs install vim bash curl apache2 apache2-utils && \
    yum -y --setopt=tsflags=nodocs install python python-urllib3 python-openssl python-requests python-tools && \
    systemctl enable httpd && \
    yum -y clean all

EXPOSE 80 443

# Simple startup script to avoid some issues observed with container restart
COPY ./code.tgz /code.tgz
COPY ./conf.tgz /conf.tgz
RUN mkdir -p /var/www/html && \
    cd / && \
    tar -xzvf conf.tgz && \
    cd / && \
    tar -xzvf code.tgz

ENTRYPOINT ["/usr/sbin/init"]
