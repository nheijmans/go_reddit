import json
import time
import boto3
import requests
import io
import csv
from botocore.exceptions import ClientError
from os import environ as env

SLEEP_TIME=0.5
# s3 bucket name to store csv posts
BUCKET_NAME= env['BucketName']
# list of subreddits to load
TOPICS = ['investing','stocks','StockMarket','wallstreetbets','CryptoCurrency']

def lambda_handler(event, context):
    for topic in TOPICS:
        try:
            load_subreddit(topic, BUCKET_NAME)
        except Exception as e:
            print("Failed to load subreddit " + topic)
            print(e)

def load_subreddit(topic_name, bucket_name):
    posts = [] 
    url = 'https://www.reddit.com/r/' + topic_name + '/new/.json'
    output_file = topic_name + '.csv'
    s3_client = boto3.resource("s3")

    if s3_file_exists(s3_client, bucket_name, output_file):
        posts = load_saved_posts(s3_client, bucket_name, output_file)
        last_post_id = posts[0][0]
        # load up to 100 most recent posts going backwards from the latest post
        load_posts(posts, "before", 100, url, last_post_id)
    else:
        # we have not loaded any posts yet - try to load all available posts, up to 1000
        load_posts(posts, "after", 100, url)
   
    posts_csv = convert_to_csv(posts)
    s3_client.Object(bucket_name, output_file).put(Body=posts_csv)

def parse_posts(posts, response):
    json_data = response.json()['data']
    for post in json_data['children']:
        post_data = post["data"]
        posts.append((post_data["name"], post_data["created_utc"], post_data["subreddit"], post_data["title"], post_data["selftext"]))
        comprehend_analysis(post_data["selftext"])

def load_posts(posts, direction, limit, url, pagingId=None):
    headers = {'User-agent': 'Bleep bot 0.1'}
    #create while loop, it'll be work until 'after'/'before' gets None
    while True:
        params = {'limit': limit}
        if pagingId is not None:
            params.update( {direction: pagingId} )
        response = requests.get(url, params = params, headers=headers)
        if response.status_code == 200:
            parse_posts(posts, response)
            pagingId = response.json()['data'][direction]
            if pagingId is None:
                break
        else:
            raise Exception('Failed to load reddit posts: ' + response.status_code + " - " + response.text)
        time.sleep(SLEEP_TIME)

def load_saved_posts(s3_client, bucket_name, file_name):
    file_object = s3_client.Object(bucket_name, file_name)
    lines = file_object.get()['Body'].read().decode('utf-8').splitlines(True)
    return [tuple(row) for row in csv.reader(lines)]

def s3_file_exists(s3_client, bucket_name, file_name):
    try:
        s3_client.Object(bucket_name, file_name).load()
        return True
    except ClientError as exc:
        return False

def convert_to_csv(posts):
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
    for post in posts:
        writer.writerow(post)
    return output.getvalue()

def comprehend_analysis(text):
    comprehend_client = boto3.client('comprehend')
    entity_data = comprehend_client.get_entities(Text=text)
    print(entity_data)

    return