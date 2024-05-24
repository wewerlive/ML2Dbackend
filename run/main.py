from flask import Flask, request
from pymongo import MongoClient
import json
from bson import json_util
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# from gradio_client import Client, file

# client = Client("kadirnar/IDM-VTON")

# result = client.predict(
# 		dict={"layers":[file('https://raw.githubusercontent.com/gradio-app/gradio/main/test/test_files/bus.png')]},
# 		garm_img=file('https://raw.githubusercontent.com/gradio-app/gradio/main/test/test_files/bus.png'),
# 		garment_des="Hello!!",
# 		is_checked=True,
# 		is_checked_crop=False,
# 		denoise_steps=20,
# 		seed=42,
# 		api_name="/tryon"
# )
# print(result)

mongo_url = "mongodb+srv://roshanbiswanathpatra:j7yRepw9OPFdiGke@firstcluster.oy6mzmy.mongodb.net/?retryWrites=true&w=majority&appName=firstCluster"

client = MongoClient(mongo_url)
print(client.test.products)
# print(client['firstCluster'])


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.get("/products")
def products():
    products = client.test.products.find({})
    # print(list(products))
    # pList = list(products)
    pList = json.loads(json_util.dumps(products))
    # pList = json.loads(json_util.dumps(products))
    print(pList)
    return {"products": pList}

@app.post("/productInfo")
def product_info():
    print(request.json)
    products = []
    for i in request.json['products']:
        p = client.test.products.find_one({"product_id": i})
        if p != None:
            products.append(p)
    # products = client.test.products.find_one({"product_id": request.json['product_id']})
    pList = json.loads(json_util.dumps(products))
    print(pList)
    return {"products": pList}

@app.post("/tryon")
def tryon():
    print(request.json)
    return "<p>Tryon</p>"