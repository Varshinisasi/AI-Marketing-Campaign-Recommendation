from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["marketing_ai"]

product_collection = db["products"]
review_collection = db["reviews"]

def save_products(data):
    if data:
        product_collection.insert_many(data)

def save_reviews(product_name, reviews):
    for review in reviews:
        review_collection.insert_one({
            "product": product_name,
            "review": review
        })
