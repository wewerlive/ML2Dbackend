
from pymongo import MongoClient
import json
from bson import json_util
import torch
import os
from fastapi import FastAPI, Request

app = FastAPI()


from pathlib import Path  
import sys
PROJECT_ROOT = Path(__file__).absolute().parents[1].absolute()
sys.path.insert(0, str(PROJECT_ROOT))


from ootd.inference_ootd_dc import OOTDiffusionDC

if torch.cuda.is_available():
    torch.cuda.empty_cache()



model = None
if torch.cuda.is_available():
    from predictFunction import predictTryOn
    model = OOTDiffusionDC(0)

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

@app.get("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.get("/products")
def products(request: Request):
    products = client.test.products.find({})
    # print(list(products))
    # pList = list(products)
    pList = json.loads(json_util.dumps(products))
    # pList = json.loads(json_util.dumps(products))
    print(pList)
    return {"products": pList}

@app.post("/productInfo")
async  def product_info(request: Request):
    request.json = await request.json()
    products = []
    for i in request.json['products']:
        p = client.test.products.find_one({"product_id": i})
        if p != None:
            products.append(p)
    # products = client.test.products.find_one({"product_id": request.json['product_id']})
    pList = json.loads(json_util.dumps(products))
    print(pList)
    return {"products": pList}

if torch.cuda.is_available():
    @app.post("/tryon")
    async def tryon(request: Request):  
        request.json = await request.json()
        # print(request.json)
        # print(request.json['topId'])
        # print(request.json['bottomId'])
        # print(request.json['dressId'])
        # if 'topId' in request.json:
        #     top = client.test.products.find_one({"product_id": request.json['topId']})
        # else:
        #     top = None
        # if 'bottomId' in request.json:
        #     bottom = client.test.products.find_one({"product_id": request.json['bottomId']})
        # else:
        #     bottom = None
        # if bottom == None and top == None:
        #     return {"error": "No top or bottom found"}
        # personImg = request.json['personImg']
        # if bottom != None:
        #     bottomLink = bottom['product_link']
        #     tryImg = predictTryOn(1, bottomLink, personImg)
        if 'pId' in request.json:
            product = client.test.products.find_one({"product_id":request.json['pId']})
            print(product)
            category = {"top":0,"bottom":1}
            tryImg = predictTryOn(category[product["product_type"]],product['product_link'],request.json['personImg'],model)
            return {"tryOn":tryImg}
        else:
            return "No ProductID given"
        

# @socketio.on('connect')
# def test_connect():
#     print('Client connected')

# @socketio.on('tryon')
# def asynctryon(data):
#     print(data)
#     print("Tryon")
#     if 'pId' in data:
#         product = client.test.products.find_one({"product_id":data['pId']})
#         print(product)
#         category = {"top":0,"bottom":1}
#         tryImg = predictTryOn(category[product["product_type"]],product['product_link'],data['personImg'],model)
#         emit('tryonResult', {'tryOn':tryImg})
#         # return {"tryOn":tryImg}
#     # else:
#     #     return "No ProductID given"
#     # socketio.emit('tryon', "Tryon")

# if __name__ == '__main__':
#     socketio.run(app, host='0.0.0.0')   