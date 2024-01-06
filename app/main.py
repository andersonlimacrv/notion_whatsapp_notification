import os
from dotenv import load_dotenv
import json
import pywhatkit
from pprint import pprint

from NotionManager import NotionManager
from ActivitiesManager import ActivitiesManager

load_dotenv()

notion_token = os.getenv("NOTION_TOKEN_CESS")
notion_page_id = os.getenv("NOTION_PAGE_ID_CESS")
notion_database_id = os.getenv("NOTION_DATABASE_ID_CESS")
wpp_group_id = os.getenv("WHATSAPP_GROUP_ID")

def main():

    notion_manager = NotionManager(notion_token, notion_page_id, notion_database_id)
    activities_manager = ActivitiesManager('simple_rows.json')

    # Obtém informações sobre o banco de dados e salva em um arquivo json
    notion_db_info = notion_manager.get_notion_db_info()
    notion_manager.write_dict_to_file_as_json(notion_db_info, "notion_db_info.json")

    # Consulta as linhas do banco de dados e salva em um um arquivo json
    notion_db_rows = notion_manager.get_notion_db_rows()
    notion_manager.write_dict_to_file_as_json(notion_db_rows, "notion_db_rows.json")

    simple_rows = []

    # Simplifica as linhas do banco de dados para um formato mais amigável
    for row in notion_db_rows:
        activity = notion_manager.safe_get(row, "properties.Atividade.title.0.text.content")
        functionality = notion_manager.safe_get(row, "properties.Funcionalidade.select.name")
        sector = notion_manager.safe_get(row, "properties.Setor.select.name")
        priority = notion_manager.safe_get(row, "properties.Prioridade.select.name")
        made_by = notion_manager.safe_get(row, "properties.Responsavel.people.0.id")
        test_by = notion_manager.safe_get(row, "properties.Testado_por.people.0.id")
        deadline = notion_manager.safe_get(row, "properties.Entrega_Prevista.date.start")
        status = notion_manager.safe_get(row, "properties.Status.status.name")

        if made_by is None:
            made_by_name = "Nao Preenchido"
        else:
            made_by_name = notion_manager.read_user_from_json(made_by, "users.json")["name"]
        if test_by is None:
            test_by_name = "Nao Preenchido"
        else:
            test_by_name = notion_manager.read_user_from_json(test_by, "users.json")["name"]

        simple_rows.append({
            "Atividade": activity,
            "Funcionalidade": functionality,
            "Setor": sector,
            "Prioridade": priority,
            "Reponsavel": made_by_name,
            "Testado_por": test_by_name,
            "Entrega_Prevista": deadline,
            "Status": status
        })

    # Salva as linhas simplificadas em um arquivo JSON
    notion_manager.write_dict_to_file_as_json(simple_rows, "simple_rows.json")

    mensagem_formatada = activities_manager.formatar_mensagem()
    pprint(mensagem_formatada)

    # Envia a mensagem para o WhatsApp
    try:
        pywhatkit.sendwhatmsg_to_group_instantly(wpp_group_id, mensagem_formatada)
    except Exception as e:
        print(f"Erro ao enviar mensagem para o WhatsApp: {e}")
    

if __name__ == "__main__":
    main()