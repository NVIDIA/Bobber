#!/bin/bash
set -e
# Pass the list of hosts in as a string
hosts=$1
# Optionally pass a username to login to remote nodes
user=$2

# Generate a new RSA key locally for SSH to share across the cluster
mkdir -p /tmp/bobber
rm -f /tmp/bobber/*
ssh-keygen -t rsa -b 4096 -f /tmp/bobber/id_rsa -N ""

echo "Copying keys to containers on all hosts"
echo "For remote hosts, if passwordless-ssh is not configured, you will be prompted for the password for all nodes"

if [[ $hosts=="localhost" || -z "$hosts" ]]; then
  docker cp /tmp/bobber/id_rsa bobber:/root/.ssh/id_rsa
  docker cp /tmp/bobber/id_rsa.pub bobber:/root/.ssh/authorized_keys
fi

# Copy the key to the container
for host in ${hosts//,/ }; do
  if [ ! -z "$user" ]; then
    scp -r /tmp/bobber $user@$host:/tmp/
    ssh $user@$host 'docker cp /tmp/bobber/id_rsa bobber:/root/.ssh/id_rsa && docker cp /tmp/bobber/id_rsa.pub bobber:/root/.ssh/authorized_keys && rm /tmp/bobber/id_rsa*'
  else
    scp -r /tmp/bobber $host:/tmp/
    ssh $host 'docker cp /tmp/bobber/id_rsa bobber:/root/.ssh/id_rsa && docker cp /tmp/bobber/id_rsa.pub bobber:/root/.ssh/authorized_keys && rm /tmp/bobber/id_rsa*'
  fi
done

# Cleanup the local key
rm -f /tmp/bobber/id_rsa*
