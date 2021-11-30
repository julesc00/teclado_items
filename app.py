from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from flask_jwt import JWT, jwt_required

from security import authenticate, identity
from user import UserRegister

app = Flask(__name__)
app.secret_key = "julito"
api = Api(app)

jwt = JWT(app, authenticate, identity)  # new endpoint /auth

items = []


# a model, urls
class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        "price",
        type=float,
        required=True,
        help="This field cannot be left blank!"
    )

    @jwt_required()
    def get(self, name):
        """Get an item."""
        item = next(filter(lambda x: x["name"] == name, items), None)
        return {"item": item}, 200 if item else 404

    def post(self, name):
        """Create a new item."""
        if next((filter(lambda x: x["name"] == name, items)), None):
            return {"message": f"An item with name {name} already exists."}, 400

        data = Item.parser.parse_args()
        item = {"name": name, "price": data["price"]}
        items.append(item)

        return item, 201

    def put(self, name):
        """Edit an existing item"""
        item = next(filter(lambda x: x["name"] == name, items), None)
        data = Item.parser.parse_args()
        if item is None:
            item = {"name": name, "price": data["price"]}
            items.append(item)
        else:
            item.update(data)

        return item

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
api.add_resource(UserRegister, "/register")

app.run(port=5000, debug=True)
