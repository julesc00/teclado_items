from flask import Flask, request
from flask_restful import Resource, Api
from flask_jwt import JWT, jwt_required

from security import authenticate, identity

app = Flask(__name__)
app.secret_key = "julito"
api = Api(app)

jwt = JWT(app, authenticate, identity)  # new endpoint /auth

items = []


# a model, urls
class Item(Resource):
    @jwt_required()
    def get(self, name):
        """Get an item."""
        item = next(filter(lambda x: x["name"] == name, items), None)
        return {"item": item}, 200 if item else 404

    def post(self, name):
        """Create a new item."""
        if next((filter(lambda x: x["name"] == name, items)), None):
            return {"message": f"An item with name {name} already exists."}, 400

        data = request.get_json()
        item = {"name": name, "price": data["price"]}
        items.append(item)

        return item, 201

    def update(self, name):
        """Edit an existing item"""
        data = request.get_json()

    def delete(self, name):
        """Delete multiple item."""
        global items
        items = list(filter(lambda i: i["name"] != name, items))
        # Below, my way of deleting an item and it worked.
        # item = next(filter(lambda i: i["name"] == name, items), None)
        # items.remove(item)
        return {"message:": "Item was deleted successfully."}


class ItemList(Resource):
    def get(self):
        """Return all items."""
        return {"items": items}


api.add_resource(Item, "/item/<string:name>")
api.add_resource(ItemList, "/items")

app.run(port=5000, debug=True)
