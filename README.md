## How to connect
Check the IP given to the instance, eg. 10.121.243.250

There is a 'test' table you can use to verify everything works:

```python
import happybase
connection = happybase.Connection(host='10.121.243.250')
test = connection.table('test') 
for k, d in test.scan(): print k, d
```

To connect using java you can use our [Sample Java HBase client](https://github.com/bigdatacesga/hbase-client-java) and modify the hbase.zookeeper.quorum to reflect the right IP of your instance:

```java
Configuration conf = HBaseConfiguration.create();
conf.set("hbase.zookeeper.quorum","10.121.243.250");
Connection connection = ConnectionFactory.createConnection(conf);
```

## Quick start: How to create a new product
1. Generate the Docker image

2. Edit:
- template.json
- options.json
- `fabfile_pre.py`
- register.sh

3. Generate the orchestrator:

    ./generate_orchestrator.py > fabfile.py

4. Upload the logo:

    scp hbase-logo.png bigdata.cesga.gal:/var/www/html/img/hbase-logo.png

5. Register the product:

    ./register.sh

## Orchestrator
You need to provide a fabric `fabfile.py` orchestrator to coordinate the
configuration of the cluster once it is started.

### `fabfile_pre.py` 
It supports including the content of config files using `include_file_contents` 
without having to include them directly in the fabfile.

For example:

    MONGOD_CONF = """{{ include_file_contents('files/mongod.conf.jinja') }}"""

Then you can generate the `fabfile.py` orchestrator using the provided script:

    ./generate_orchestrator.py > fabfile.py

This will produce the required fabfile.py file.


### Testing the orchestrator

To run the orchestrator manually, once you have started the cluster run:

    # NOOP mode (no changes done)
    INSTANCE='clusters/sistemas/gluster/3.7.11/4' NOOP=1 fab test
    # Normal mode (real mode)
    INSTANCE='clusters/sistemas/gluster/3.7.11/4' fab test
