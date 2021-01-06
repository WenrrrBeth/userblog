from pymongo import MongoClient
import json
from datetime import datetime
import sys

def main():  
    p = "mongodb://localhost:" + sys.argv[1]
    user = MongoClient(p)
    db = user["291db"]

    db.drop_collection("posts_collection")
    db.drop_collection("tags_collection")
    db.drop_collection("votes_collection")

    collist = db.list_collection_names()
    if ("posts_collection" in collist or "tags_collection" in collist or "votes_collection" in collist):
        print("The collection exist")

    posts_collection = db["posts_collection"]
    tags_collection = db["tags_collection"]
    votes_collection = db["votes_collection"]

    posts_collection.delete_many({})
    tags_collection.delete_many({})
    votes_collection.delete_many({})


    with open('Posts.json') as json_file:
        data = json.load(json_file)
        posts = data["posts"]['row']

    ret = posts_collection.insert_many(posts)
    posts_ids = ret.inserted_ids #???
    # print(posts_ids)

    with open('Tags.json') as json_file:
        data = json.load(json_file)
        tags = data["tags"]["row"]

    ret = tags_collection.insert_many(tags)
    tags_ids = ret.inserted_ids #???
    # print(tags_ids)

    with open('Votes.json') as json_file:
        data = json.load(json_file)
        votes = data["votes"]["row"]

    ret = votes_collection.insert_many(votes)
    votes_ids = ret.inserted_ids #???


if __name__ == "__main__":
    main()