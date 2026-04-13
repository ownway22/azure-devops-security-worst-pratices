#!/bin/bash

# Validate required environment variables
if [ -z "${AZP_URL}" ]; then
  echo "error: AZP_URL is not set"
  exit 1
fi

if [ -z "${AZP_TOKEN}" ]; then
  echo "error: AZP_TOKEN is not set"
  exit 1
fi

AZP_POOL="${AZP_POOL:-Default}"
AZP_AGENT_NAME="${AZP_AGENT_NAME:-$(hostname)}"
AZP_WORK="${AZP_WORK:-_work}"

# Determine architecture for agent download
ARCH=$(uname -m)
case "${ARCH}" in
  aarch64) AGENT_ARCH="linux-arm64" ;;
  x86_64)  AGENT_ARCH="linux-x64" ;;
  *)
    echo "error: unsupported architecture: ${ARCH}"
    exit 1
    ;;
esac

echo "1/4: Determining matching Azure Pipelines agent..."
echo "  Platform: ${AGENT_ARCH}"
echo "  URL: ${AZP_URL}/_apis/distributedtask/packages/agent?platform=${AGENT_ARCH}&top=1&api-version=7.1"

# Get the latest agent version (capture HTTP status and body separately)
B64_PAT=$(printf ":%s" "${AZP_TOKEN}" | base64 -w 0)
HTTP_RESPONSE=$(curl -s -w "\n%{http_code}" \
  -H "Authorization: Basic ${B64_PAT}" \
  "${AZP_URL}/_apis/distributedtask/packages/agent?platform=${AGENT_ARCH}&top=1&api-version=7.1" 2>&1) || true

HTTP_STATUS=$(echo "${HTTP_RESPONSE}" | tail -1)
AZP_AGENT_RESPONSE=$(echo "${HTTP_RESPONSE}" | sed '$d')

echo "  HTTP Status: ${HTTP_STATUS}"

if [ "${HTTP_STATUS}" != "200" ]; then
  echo "error: API call failed with HTTP ${HTTP_STATUS}"
  echo "  Response: ${AZP_AGENT_RESPONSE}"
  exit 1
fi

AGENT_URL=$(echo "${AZP_AGENT_RESPONSE}" | jq -r '.value[0].downloadUrl')

if [ -z "${AGENT_URL}" ] || [ "${AGENT_URL}" = "null" ]; then
  echo "error: could not determine a matching agent."
  echo "  Response body: ${AZP_AGENT_RESPONSE}"
  exit 1
fi

echo "2/4: Downloading agent to /home/azpagent/agent..."

mkdir -p agent
cd agent

curl -sSfL "${AGENT_URL}" | tar -xz &
wait $!

echo "3/4: Configuring agent '${AZP_AGENT_NAME}'..."

./config.sh --unattended \
  --url "${AZP_URL}" \
  --auth pat \
  --token "${AZP_TOKEN}" \
  --pool "${AZP_POOL}" \
  --agent "${AZP_AGENT_NAME}" \
  --work "${AZP_WORK}" \
  --replace \
  --acceptTeeEula

# Cleanup function to remove agent on container stop
cleanup() {
  trap "" EXIT

  if [ -e config.sh ]; then
    echo "Removing agent..."
    ./config.sh remove --unattended --auth pat --token "${AZP_TOKEN}"
  fi
}

trap 'cleanup; exit 0' EXIT
trap 'cleanup; exit 130' INT
trap 'cleanup; exit 143' TERM

echo "4/4: Running agent..."

chmod +x run.sh
exec ./run.sh "$@"
