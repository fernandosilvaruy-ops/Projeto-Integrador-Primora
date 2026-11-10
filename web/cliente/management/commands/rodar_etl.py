import sys
import os
from django.conf import settings
from django.core.management.base import BaseCommand

# Adiciona a raiz do projeto (pai de web/) ao path do Python
project_root = os.path.dirname(str(settings.BASE_DIR))
if project_root not in sys.path:
    sys.path.append(project_root)

class Command(BaseCommand):
    help = 'Executa o pipeline ETL da Distribuidora Vetor (carregamento, tratamento e auditoria)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Iniciando o pipeline ETL da Distribuidora Vetor...'))

        try:
            # Importa e executa a função principal do ETL na pasta src/database/loader.py
            from src.database.loader import executar_etl
            
            executar_etl()
            
            self.stdout.write(self.style.SUCCESS('Pipeline ETL executado e dados auditados com sucesso!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro durante a execução do ETL: {e}'))