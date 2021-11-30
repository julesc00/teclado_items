import sqlite3
from flask_restful import Resource, reqparse
from flask_jwt import jwt_required

items = []

ERROR_MSG = "An database error occurred!"


# a model, urls
class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        "price",
        type=float,
        required=True,
        help="This field cannot be left blank!"
    )

    @classmethod
    def find_by_name(cls, name):
        connection = sqlite3.connect("data.db")
        cursor = connection.cursor()
        try:
            query = "SELECT * FROM items WHERE name=?"
            result = cursor.execute(query, (name,))
            row = result.fetchone()
            connection.close()

            if row:
                return {"item": {"name": row[0], "price": row[1]}}, 200
        except ConnectionError:
            return {"message": ERROR_MSG}, 500

    @classmethod
    def insert(cls, item):
        connection = sqlite3.connect("data.db")
        cursor = connection.cursor()

        try:
            query = "INSERT INTO items VALUES (?, ?)"
            cursor.execute(query, (item["name"], item["price"]))
            connection.commit()
            connection.close()
        except ConnectionError:
            return {"message": ERROR_MSG}, 500

    @classmethod
    def update(cls, item):
        connection = sqlite3.connect("data.db")
        cursor = connection.cursor()

        query = "UPDATE items SET price=? WHERE name=?"
        cursor.execute(query, (item["price"], item["name"]))

        connection.commit()
        connection.close()

    @jwt_required()
    def get(self, name):
        """Get an item from db."""
        item = self.find_by_name(name)
        if item:
            return item
        return {"message": "Item not found."}, 404

    def post(self, name):
        """Create a new item."""
        if self.find_by_name(name):
            return {"message": f"An item with name {name} already exists."}, 400

        data = Item.parser.parse_args()
        item = {"name": name, "price": data["price"]}

        try:
            self.insert(item)
        except NotImplemented:
            return {"message": ERROR_MSG}, 500

        return item, 201

    def put(self, name):
        """Edit an existing item"""
        data = Item.parser.parse_args()
        item = self.find_by_name(name)
        updated_item = {"name": name, "price": data["price"]}

        if item is None:
            try:
                self.insert(updated_item)
            except ConnectionError:
                return {"message": ERROR_MSG}, 500
        else:
            try:
                self.update(updated_item)
            except ConnectionError:
                return {"message": ERROR_MSG}, 500

        return updated_item

    def delete(self, name):
        """Delete multiple item."""
        connection = sqlite3.connect("data.db")
        cursor = connection.cursor()

        try:
            query = "DELETE FROM items WHERE name=?"
            cursor.execute(query, (name,))
            connection.commit()
            connection.close()
            return {"message:": "Item was deleted successfully."}
        except ConnectionError:
            return {"message": ERROR_MSG}, 500


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
