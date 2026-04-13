FROM ubuntu:22.04

# Prevent prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install base dependencies + Node.js (required by Azure DevOps tasks)
RUN apt-get update && apt-get install -y --no-install-recommends \
  ca-certificates \
  curl \
  git \
  jq \
  libicu70 \
  libssl3 \
  lsb-release \
  gnupg \
  && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
  && apt-get install -y --no-install-recommends nodejs \
  && rm -rf /var/lib/apt/lists/*

# Optional: install Docker CLI for pipelines that need to build images
RUN curl -fsSL https://get.docker.com | sh

# Create a non-root user for the agent
RUN useradd -m -d /home/azpagent azpagent
WORKDIR /home/azpagent

COPY start.sh .
RUN chmod +x start.sh

USER azpagent

ENTRYPOINT ["./start.sh"]
