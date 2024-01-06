import json
import os
from pprint import pprint
from datetime import datetime
import locale

locale.setlocale(locale.LC_TIME, 'pt_BR.utf-8') # Traduz o mês em português do strptime

class ActivitiesManager:
    def __init__(self, file_name):
        self.data = self.read_json_activities(file_name)

    def read_json_activities(self, file_name):
        with open(file_name) as f:
            data = json.load(f)
            return data

    def get_develop_activities(self):
        develop = []
        for row in self.data:
            if row["Status"] == "Em Desenvolvimento":
                atividade = row["Atividade"]
                setor = row["Setor"]
                responsavel = row.get("Reponsavel")
                entrega_prevista = row.get("Entrega_Prevista", None)

                develop.append({"Atividade": atividade, "Setor": setor, "Responsavel": responsavel, "Entrega_Prevista": entrega_prevista})

        return develop

    def get_waiting_test_activities(self):
        waiting_test = []
        for row in self.data:
            if row["Status"] == "Aguardando Teste":
                atividade = row["Atividade"]
                setor = row["Setor"]
                responsavel = row.get("Reponsavel")
                entrega_prevista = row.get("Entrega_Prevista", None)

                waiting_test.append({"Atividade": atividade, "Setor": setor, "Responsavel": responsavel, "Entrega_Prevista": entrega_prevista})
        return waiting_test
    
    def missing_requirements(self):
        missing = []
        for row in self.data:
            if row["Status"] == "Falta Pre-Requisito":
                atividade = row["Atividade"]
                setor = row["Setor"]
                responsavel = row.get("Reponsavel")
                

                missing.append({"Atividade": atividade, "Setor": setor, "Responsavel": responsavel})
        return missing
    
    def formatar_mensagem(self):
        atividades_desenvolvimento = self.get_develop_activities()
        atividades_aguardando_teste = self.get_waiting_test_activities()
        atividades_faltam_prerequisitos = self.missing_requirements()

        mensagem = "_*RELATORIO DE ATIVIDADES DE SOFTWARE*_:\n\n"

        mensagem += "*Atividades em Desenvolvimento:*\n"
        mensagem += self.formatar_atividades(atividades_desenvolvimento) + "\n"

        """ mensagem += "*Atividades Aguardando Teste*:\n"
        mensagem += self.formatar_atividades(atividades_aguardando_teste) + "\n" """

        mensagem += "*Atividades que faltam pre-requisitos*:\n"
        mensagem += self.formatar_atividades(atividades_faltam_prerequisitos)

        return mensagem

    def formatar_atividades(self, atividades):
        resultado = ""
        for atividade in atividades:
            resultado += f"    - *` Atividade`*: {atividade['Atividade']}\n"
            resultado += f"    - *`Setor`*: {atividade['Setor']}\n"
            resultado += f"    - *`Responsavel`*: {atividade['Responsavel']}\n"

            entrega_prevista = atividade.get("Entrega_Prevista", None)
            if entrega_prevista is None:
                resultado += "\n"
            else:
                entrega_prevista = self.format_date(entrega_prevista)
                resultado += f"    - *` Entrega Prevista`*: {entrega_prevista}\n\n"
        return resultado   

    def format_date(self, date_str):
        date_obj  = datetime.strptime(date_str, "%Y-%m-%d")
        date_str_formatted = f"{date_obj .day}, {date_obj .strftime('%B')} de {date_obj .year}"

        return date_str_formatted

    
           