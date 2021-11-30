import sqlite3
from flask_restful import Resource, reqparse
from flask_jwt import jwt_required

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
        """Get an item from db."""
        item = self.find_by_name(name)
        if item:
            return item
        return {"message": "Item not found."}, 404

    @classmethod
    def find_by_name(cls, name):
        connection = sqlite3.connect("data.db")
        cursor = connection.cursor()

        query = "SELECT * FROM items WHERE name=?"
        result = cursor.execute(query, (name,))
        row = result.fetchone()
        connection.close()

        if row:
            return {"item": {"name": row[0], "price": row[1]}}, 200

    def post(self, name):
        """Create a new item."""
        if self.find_by_name(name):
            return {"message": f"An item with name {name} already exists."}, 400

        data = Item.parser.parse_args()
        item = {"name": name, "price": data["price"]}

        connection = sqlite3.connect("data.db")
        cursor = connection.cursor()

        query = "INSERT INTO items VALUES (?, ?)"
        cursor.execute(query, (item["name"], item["price"]))

        connection.commit()
        connection.close()

        return item, 201

    def put(self, name):
        """Edit an existing item"""
        item = self.find_by_name(name)
        data = Item.parser.parse_args()
        if item is None:
            item = {"name": name, "price": data["price"]}
            items.append(item)
        else:
            item.update(data)

        return item

    def delete(self, name):
        """Delete multiple item."""

        connection = sqlite3.connect("data.db")
        cursor = connection.cursor()

        query = "DELETE FROM items WHERE name=?"
        cursor.execute(query, (name,))

        connection.commit()
        connection.close()

        return {"message:": "Item was deleted successfully."}


class ItemList(Resource):
    def get(self):
        """Return all items."""
        connection = sqlite3.connect("data.db")
        cursor = connection.cursor()

        query = "SELECT * FROM items"
        result = cursor.execute(query)
        rows = result.fetchall()
        connection.close()

        for name, row in rows:
            if rows:
                return {"items": {"item": {"name": name, "price": row}}}, 200

            return {"message": "There are no entries."}
