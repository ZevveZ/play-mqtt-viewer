FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir -p /code/site
WORKDIR /code
ADD requirements.txt .
RUN pip install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
RUN apt-get update &&apt-get install -y supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
CMD ["/usr/bin/supervisord"]
