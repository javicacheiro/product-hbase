#!/usr/bin/env python
# encoding: utf-8
"""Orchestration template

The following tasks must be implemented:
    - start
    - stop
    - restart
    - status

An instance endpoint has to be provided using the CLUSTERDN environment variable.
For example:

    CLUSTERDN="instances/test/reference/1.0.0/1"

A fabric roledef  is created for each service defined in the registry.
It can be used with the decorator: @roles('servicename1')

WARN: The hosts are accesed using the IP address of the second network device,
usually eth1.

The properties of a given service can be accessed through:

    SERVICES['servicename'].propertyname

for example:

    SERVICES['namenode'].heap
    # If the property has dots we can use
    SERVICES['datanode'].get('dfs.blocksize')
    # Or even define a default value in case it does not exist
    SERVICES['datanode'].get('dfs.blocksize', '134217728')

Details about a given node can be obtained through each Node object returned by service.nodes

The fabfile can be tested running it in NOOP mode (testing mode) exporting a NOOP env variable.

Required roles: initiator, responders, peerback

"""
from __future__ import print_function
import os
import sys
from fabric.api import *
from fabric.colors import red, green, yellow, blue
from fabric.contrib.files import exists, append, sed, comment, uncomment
# FIXME: Installing configuration-registry with pip and importing registry directly does not work
#  inside the fabfile. Temporarily it is copied manually in the utils directory
#from utils import registry
# In the big data nodes configuration-registry is installed globally
import registry
import time
from pprint import pprint
from StringIO import StringIO
import jinja2


# Maximum number of retries to wait for a node to change to status running
MAX_RETRIES = 100
# Seconds between retries
DELAY = 5


def eprint(*args, **kwargs):
    """Print to stderr"""
    print(*args, file=sys.stderr, **kwargs)


if os.environ.get('CLUSTERDN'):
    CLUSTERDN = os.environ.get('CLUSTERDN')
else:
    eprint(red('An instance endpoint has to be provided using the CLUSTERDN environment variable'))
    sys.exit(2)

if os.environ.get('REGISTRY'):
    REGISTRY = os.environ.get('REGISTRY')
else:
    REGISTRY = 'http://consul.service.int.cesga.es:8500/v1/kv'

# Retrieve info from the registry
registry.connect(REGISTRY)
cluster = registry.Cluster(CLUSTERDN)
nodes = cluster.nodes
services = cluster.services


def wait_until_node_is_running(node):
    """Wait until node is in status running: i.e. docker-executor finished"""
    name = node.name
    retry = 0
    while not node.status == 'running':
        retry += 1
        if retry > MAX_RETRIES: sys.exit(3)
        print('Waiting for node {}: {}/{}'.format(name, retry, MAX_RETRIES))
        time.sleep(DELAY)


def address(node):
    """Return the network address to be used by the cluster"""
    return node.networks[0].address


def put_template(tmpl_string, dest, context=None):
    """Upload a template contained in tmpl_string to the dest path
       The context is passed as p
    """
    t = jinja2.Template(tmpl_string)
    rendered = t.render(p=context)
    put(StringIO(rendered), dest)


# Expose the relevant information
NODES = {node.name: node for node in nodes}
SERVICES = {service.name: service for service in services}
NODE = {}
for node in nodes:
    wait_until_node_is_running(node)
    properties = {'hostname': node.name}
    for dev in node.networks:
        properties[dev.name] = dev.address
    for disk in node.disks:
        properties[disk.name] = disk.destination
    # Using virbrBIGDATA we no longer need two addresses
    properties['address'] = address(node)
    #properties['address_int'] = internal_address(node)
    #properties['address_ext'] = external_address(node)
    # The node is labeled with the network address that will be used by fabric
    # to connect to the node, this allows to retrieve the node using NODE[env.host]
    label = properties['address']
    NODE[label] = properties


env.user = 'root'
env.hosts = NODE.keys()
# Allow known hosts with changed keys
env.disable_known_hosts = True
# Retry 30 times each 10 seconds -> (30-1)*10 = 290 seconds
env.connection_attempts = 30
env.timeout = 10
# Enable ssh client keep alive messages
env.keepalive = 15

# Define the fabric roles according to the cluster services
for service in services:
    env.roledefs[service.name] = [address(n) for n in service.nodes]

# Define also a global var ROLE to be used for internal cluster configuration
ROLE = {}
for service in services:
    ROLE[service.name] = [address(n) for n in service.nodes]

print(blue('= Summary of cluster information ='))
print('== NODE ==')
pprint(NODE)
print('== Fabric roles ==')
pprint(env.roledefs)
print('== ROLE ==')
pprint(ROLE)
print(blue('= End of summary ='))

#
# Debugging mode
#
# To enable it use: export NOOP=1
if os.environ.get('NOOP'):

    print(yellow('\n\n== Running in NOOP mode ==\n\n'))

    def run(name):
        print('[{0}] run: {1}'.format(env.host, name))

    def put(source, destination):
        print('[{0}] put: {1} {2}'.format(env.host, source, destination))

    @task
    @parallel
    def hostname():
        """Print the hostnames: mainly used for testing purposes"""
        run('/bin/hostname')


#
# CONFIGURATION FILE TEMPLATES
#
# hbase-site.xml
HBASE_CONF = """"""


@task
@runs_once
def start():
    """Start the service"""
    print('No orchestration needed.')
    cluster.status = 'running'


@task
def status():
    """Check the status of the service"""
    print(red('Not supported.'))


@task
@runs_once
def stop():
    """Stop the service and all the containers that provide it"""
    print(red('Not supported.'))


@task
@runs_once
def restart():
    """Restart all the services of the cluster"""
    print(red('Restart is not supported'))
