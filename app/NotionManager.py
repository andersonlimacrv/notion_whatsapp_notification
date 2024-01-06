from notion_client import Client
import json

class NotionManager:
    def __init__(self, token, page_id, database_id):
        self.client = Client(auth=token)
        self.page_id = page_id
        self.database_id = database_id

    def write_dict_to_file_as_json(self, content, file_name):
        content_as_json_str = json.dumps(content, indent=4)

        with open(file_name, "w") as f:
            f.write(content_as_json_str)

    def read_text(self, page_id):
        response = self.client.blocks.children.list(block_id=page_id)
        return response["results"]

    def safe_get(self, data, dot_chained_keys):
        keys = dot_chained_keys.split(".")
        for key in keys:
            try:
                if isinstance(data, list):
                    data = data[int(key)]
                else:
                    data = data[key]
            except (KeyError, TypeError, IndexError):
                return None
        return data

    def create_blocks_from_content(self, content):
        page_simple_blocks = []

        for block in content:
            block_id = block["id"]
            block_type = block["type"]
            has_children = block["has_children"]
            rich_text = block[block_type]["rich_text"]

            if not rich_text:
                return

            simple_block = {
                "id": block_id,
                "type": block_type,
                "text": rich_text[0]["plain_text"],
            }

            if has_children:
                nested_children = self.read_text(block_id)
                simple_block["children"] = self.create_blocks_from_content(nested_children)

            page_simple_blocks.append(simple_block)

        return page_simple_blocks

    def get_notion_db_info(self):
        return self.client.databases.retrieve(database_id=self.database_id)

    def get_notion_db_rows(self):
        return self.client.databases.query(database_id=self.database_id)["results"]

    def read_user_from_json(self, user_id, file_name):
        with open(file_name) as f:
            users = json.load(f)
            for user in users:
                if user["id"] == user_id:
                    return user