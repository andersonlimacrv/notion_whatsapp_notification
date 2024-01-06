from notion_client import Client
import pprint
import os
from dotenv import load_dotenv
import json

load_dotenv()

notion_token = os.getenv("NOTION_TOKEN")
notion_page_id = os.getenv("NOTION_PAGE_ID")
notion_database_id = os.getenv("NOTION_DATABASE_ID")

def write_dict_to_file_as_json(content, file_name):
    """
    Escreve um dicionário para um arquivo JSON.

    Args:
        content (dict): Dicionário a ser escrito.
        file_name (str): Nome do arquivo.

    Returns:
        None
    """ 
    content_as_json_str = json.dumps(content, indent=4)

    with open(file_name, "w") as f:
        f.write(content_as_json_str)

def read_text(client, page_id):
    """
    Le um texto de uma página no Notion.

    Args:
        client (Client): Instância do cliente Notion.
        page_id (str): ID da página.

    Returns:
        str: Lista de blocos de texto na página.
    """
    response = client.blocks.children.list(block_id=page_id)
    return response["results"]

    
def safe_get(data, dot_chined_keys):
    """
    Obtém um valor de um dicionário ou lista usando uma cadeia de chaves pontilhadas.

    Args:
        data (dict or list): Dicionário ou lista a ser acessado.
        dot_chined_keys (str): Cadeia de chaves pontilhadas (por exemplo, "a.b.0.c").

    Returns:
        Valor correspondente às chaves, ou None se a chave não existir.
    """
    keys = dot_chined_keys.split(".")
    for key in keys:
        try:
            if isinstance(data, list):
                data = data[int(key)]
            else:
                data = data[key]
        except (KeyError, TypeError, IndexError):
            return None
    return data

def create_blocks_from_content(client, content):
    """
    Cria uma representação simplificada de blocos a partir do conteúdo da API do Notion.

    Args:
        client (Client): Instância do cliente Notion.
        content (list): Lista de blocos da API do Notion.

    Returns:
        list: Lista de blocos simplificados.
    """

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
            nested_children = read_text(client, block_id)
            simple_block["children"] = create_blocks_from_content(client, nested_children)

        page_simple_blocks.append(simple_block)

    return page_simple_blocks

def main():
    """
    Função principal que interage com a API do Notion para obter informações e gerar arquivos JSON.
    """
    client = Client(auth=notion_token)

    # Obtém informações sobre o banco de dados e salva em um arquivo json
    notion_db_info = client.databases.retrieve(database_id=notion_database_id)
    write_dict_to_file_as_json(notion_db_info, "notion_db_info.json")

    # Consulta as linhas do banco de dados e salva em um um arquivo json
    notion_db_rows = client.databases.query(database_id=notion_database_id)
    write_dict_to_file_as_json(notion_db_rows, "notion_db_rows.json")

    simple_rows = []

    # Simplifica as linhhas do banco de dados para um formato mais amigável
    for row in notion_db_rows["results"]:
        user_id = safe_get(row, "properties.UserId.title.0.text.content")
        event = safe_get(row, "properties.Event.select.name")
        date = safe_get(row, "properties.Date.date.start")

        simple_rows.append({"user_id": user_id, "event": event, "date": date})

    # Salva as linhas simplificadas em um arquivo JSON
    write_dict_to_file_as_json(simple_rows, "simple_rows.json")


if __name__ == "__main__":
    main()
