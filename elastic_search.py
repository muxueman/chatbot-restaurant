from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3
import json


AWS_ACCESS_KEY = ''
AWS_SECRET_KEY = ''
region = 'us-east-1'
service = 'es'

awsauth = AWS4Auth(AWS_ACCESS_KEY, AWS_SECRET_KEY, region, service)

host = ''

es = Elasticsearch(
    hosts = [{'host': host, 'port': 443, 'use_ssl': True}],
    http_auth = awsauth,
    use_ssl = True,
    verify_certs = True,
    connection_class = RequestsHttpConnection,
    request_timeout = 30
)


dynamodb_resource = boto3.resource('dynamodb')
table = dynamodb_resource.Table('yelp-restaurants')
response = table.scan()


cnt = 0 #initialize document id

for i in response['Items']:
	restaurant = i
	document = {
	    "business_id": restaurant["business_id"],
	    "cuisine": restaurant["cuisine"]
	   }
	es.index(index="restaurant", doc_type="_doc", body=document,id = cnt)
	cnt += 1
	# print(type(restaurant))
	# print('#'*20)

print(cnt)
print(es.get(index="restaurant", doc_type="_doc", id="55"))
print(es.get(index="restaurant", doc_type="_doc", id="2555"))
print(es.get(index="restaurant", doc_type="_doc", id="4500"))
print(es.get(index="restaurant", doc_type="_doc", id="5000"))


# document = {
#     "title": "Moneyball",
#     "director": "Bennett Miller",
#     "year": "2011"
# }

# es.index(index="movies", doc_type="_doc", id="5", body=document)

# print(es.get(index="movies", doc_type="_doc", id="5"))