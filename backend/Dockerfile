# Configure the base image
FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1


# Install base dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    tree \
    jq \
    vim \
    python3-pip \
    libpcap-dev \
    libssl-dev \
    curl \
    wget \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*



# Install newer Go version
RUN wget https://go.dev/dl/go1.23.0.linux-amd64.tar.gz && \
    rm -rf /usr/local/go && \
    tar -C /usr/local -xzf go1.23.0.linux-amd64.tar.gz && \
    rm go1.23.0.linux-amd64.tar.gz

# Set Go environment
ENV GOPATH=/root/go
ENV PATH=$PATH:/usr/local/go/bin:$GOPATH/bin

# # Install the tools
# RUN go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest && \
#     go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest && \
#     go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest && \
#     go install -v github.com/rix4uni/haktrailsfree@latest && \
#     go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest && \
#     go install -v github.com/projectdiscovery/katana/cmd/katana@latest && \
#     go install -v github.com/projectdiscovery/notify/cmd/notify@latest



# Create Scripts directory & static binaries
WORKDIR /work

# Configure python dependencies
COPY requirements.txt /work/
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

COPY . /work
COPY api/tools/bin/ /usr/local/bin
RUN chmod +x /usr/local/bin/* 2>/dev/null || true


# Configure python dependencies
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 


EXPOSE 8000

RUN go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest

CMD ["python3", "backend/manage.py", "runserver", "0.0.0.0:8000"]
