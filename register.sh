# First get a TOKEN
# export TOKEN='<TOKEN>'
# export AUTH="x-auth-token: $TOKEN"
http POST http://paas:6000/bigdata/api/v1/products name=hbase version=1.1.13 description='The HBase database is the right choice when you need random, realtime read/write access to your Big Data.' logo_url='http://hadoop.cesga.es/img/hbase-logo.png' x-auth-token:$TOKEN
curl -X PUT http://paas:6000/bigdata/api/v1/products/hbase/1.1.13/template --data-binary @template.json -H "Content-type: application/json" -H "$AUTH"
curl -X PUT http://paas:6000/bigdata/api/v1/products/hbase/1.1.13/options --data-binary @options.json -H "$AUTH"
curl -X PUT http://paas:6000/bigdata/api/v1/products/hbase/1.1.13/orchestrator --data-binary @fabfile.py -H "$AUTH"

# Launching
# http POST http://paas:6000/bigdata/api/v1/products/hbase/1.1.13 cpu:=1 x-auth-token:$TOKEN
