#!/usr/bin/env bash
# Deploy pkushal.com.np: build -> package -> upload -> extract into the docroot.
# The SSH key is referenced by path (never committed). Override with DEPLOY_KEY.
#
#   DEPLOY_KEY="/c/Users/ASUS/Downloads/SSHKushalWebsite_nopass" ./deploy.sh
#
set -e
KEY="${DEPLOY_KEY:-$HOME/Downloads/SSHKushalWebsite_nopass}"
HOST="rankmeto@65.98.12.7"
PORT="22"
DOCROOT="/home/rankmeto/pkushal.com.np"
HERE="$(cd "$(dirname "$0")" && pwd)"

echo "==> building"
python "$HERE/build.py" >/dev/null

echo "==> packaging"
tar czf /tmp/pk.tgz -C "$HERE/site" .

echo "==> uploading + extracting"
scp -i "$KEY" -P "$PORT" -o StrictHostKeyChecking=accept-new /tmp/pk.tgz "$HOST:/home/rankmeto/pk_deploy.tgz"
ssh -i "$KEY" -p "$PORT" -o StrictHostKeyChecking=accept-new "$HOST" \
  "tar xzf /home/rankmeto/pk_deploy.tgz -C '$DOCROOT' && rm -f /home/rankmeto/pk_deploy.tgz && echo DEPLOYED"

echo "==> live check"
curl -sSI --max-time 25 https://pkushal.com.np/ | head -1
