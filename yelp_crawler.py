"""
search restaurant info from yelp
5072 restaurants

with dashed code, save data in csv file or json
without, save directly into dynamodb
"""
import unicodecsv as csv
import requests
import time
import json
import boto3

# pre-defined types
# 'new york', 'los angeles', 'chicago', 'san francisco', 'seattle', 'washington dc', 'boston', 'austin', 'portland', 'new orland',                      'louisville',
valid_cities = [ 'san diego', 'philadelphia', 'las vegas', 'miami', 'orlando', 'irvine', 'st.louis', 'columbus', 'charlotte','phoenix']
cuisine_types = ['Chinese', 'Mexican', 'Italian', 'American', 'Japanese']

# daily limit = 5000
SEARCH_LIMIT = 50
yelp_API_key = ""
yelp_url = ""

def request_yelp(term, location):
    url_params = {
        'term': term,
        'location': location,
        'limit': SEARCH_LIMIT
    }
    headers = {'Authorization': 'Bearer %s' % yelp_API_key}
    response = requests.request('GET', yelp_url, headers = headers, params = url_params)
    # proceed only if the status code is 200
    if response.status_code != 200:
        print('The status code is {}'.format(response.status_code))
    return response.json()

def get_businesses(response, city, cuisine, table):
    # datas = []
    for business in response['businesses']:
        # Parse useful data in business
        data = {
            'business_id': business['id'],
            'inserted_timestamp': str(time.time()),
            'business_name': business['name'],
            'city': city,
            'cuisine': cuisine,
            'address': business['location']['display_address'],
            'coordinates': str(business['coordinates']),
            'num_reviews': business['review_count'],
            'rating': str(business['rating']),
            'zipcode': business['location']['zip_code']
            # 'url': business['url']
        }
        # Put data into dynamoDB
        table.put_item(Item = data)
        # datas.append(data)
        # return datas

# create if not exists
def create_dynamoDB(table_name):
    table = dynamodb.create_table(
        TableName = table_name,
        KeySchema = [
            {'AttributeName': 'business_id', 'KeyType': 'HASH'},
            {'AttributeName': 'inserted_timestamp', 'KeyType': 'RANGE'}
        ],
        AttributeDefinitions = [
            {'AttributeName': 'business_id', 'AttributeType': 'S'},
            {'AttributeName': 'inserted_timestamp', 'AttributeType': 'S'}
        ],
        ProvisionedThroughput = {'ReadCapacityUnits': 15, 'WriteCapacityUnits': 15}
    )
    print("Table status:", table.table_status)
    return table

"""------main function-------"""

# Get access to dynamodb
dynamodb = boto3.resource(
        'dynamodb',
        'us-east-1',
        aws_access_key_id='',
        aws_secret_access_key='‘)

# table = create_dynamoDB("yelp-restaurants") 
# time.sleep(5) # should wait for 'created' before inserting
table = dynamodb.Table('yelp-restaurants')

# iterate all labels to search data
for city in valid_cities:
    for cuisine in cuisine_types:
        # Crawler data from yelp
        response = request_yelp(cuisine, city)
        if len(response['businesses']) < SEARCH_LIMIT: 
            print("Less that {} {} restaurant were found in {}!".format(SEARCH_LIMIT, cuisine, city))
        # Call function to deal with each restaurant data
        get_businesses(response, city, cuisine, table)
        time.sleep(2)
            # save data with either csv or json
            # with open("yelp_restaurant_{}_{}.csv".format(city, cuisine), "wb") as fp:
            #     fieldnames = ['business_id', 'inserted_timestamp', 'business_name', 'city', 'cuisine', 'address', 'coordinates', 'num_reviews', 'rating', 'zipcode']
            #     writer = csv.DictWriter(fp, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
            #     writer.writeheader()
            #     if restaurants:    # restuarants = get_businesses()
            #         for res in restaurants:
            #             writer.writerow(res)
            #     time.sleep(5)
            # with open('yelp_res_{}_{}.json'.format(city, cuisine), "w") as f:
            #     json.dump(restaurants, f)
            # load data with code: json.load(json_file, parse_float = decimal.Decimal)  
