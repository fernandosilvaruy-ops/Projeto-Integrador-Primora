import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from cliente.models import Cliente
import os
from django.conf import settings

raiz_projeto = os.path.dirname(settings.BASE_DIR)
caminho_arquivo = os.path.join(raiz_projeto, 'clientes_distribuidora_vetor.csv')

class Command(BaseCommand):
    help = 'Importa clientes de um arquivo CSV para o banco de dados PostgreSQL'

    def handle(self, *args, **options):
        caminho_arquivo = os.path.join(settings.BASE_DIR, '..', 'clientes_distribuidora_vetor.csv')

        caminho_csv = caminho_arquivo

        self.stdout.write(f"A ler o arquivo '{caminho_csv}'...")
        
        try:
            with open(caminho_csv, mode='r', encoding='utf-8-sig') as arquivo:
                leitor = csv.DictReader(arquivo, delimiter=';')
                contador = 0
                
                for linha in leitor:
                    # Tratamento robusto para a data de cadastro
                    data_cad = linha.get('data_cadastro')
                    if data_cad:
                        parsed = False
                        for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%b %d, %Y', '%m-%d-%Y'):
                            try:
                                data_cad = datetime.strptime(data_cad.strip(), fmt).date()
                                parsed = True
                                break
                            except ValueError:
                                continue
                        if not parsed:
                            data_cad = None
                    else:
                        data_cad = None

                    cnpj_cliente = linha.get('cnpj', '').strip()
                    email_cliente = linha.get('email', '').strip()
                    
                    if not cnpj_cliente and not email_cliente:
                        continue 

                    Cliente.objects.update_or_create(
                        cnpj=cnpj_cliente,
                        defaults={
                            'razao_social': linha.get('razao_social', '').strip(),
                            'email': email_cliente,
                            'telefone': linha.get('telefone', '').strip() or None,
                            'bairro': linha.get('bairro_informado', '').strip() or None,  # Corrigido para bairro_informado
                            'cep': linha.get('cep', '').strip() or None,
                            'cidade': linha.get('cidade', '').strip() or None,
                            'uf': linha.get('uf', '').strip() or None,
                            'data_cadastro': data_cad,
                            'vendedor': linha.get('vendedor_responsavel', '').strip() or None,  # Corrigido para vendedor_responsavel
                        }
                    )
                    contador += 1
                    
                self.stdout.write(
                    self.style.SUCCESS(f"Sucesso! {contador} clientes processados e carregados para o PostgreSQL.")
                )

        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f"Erro: O arquivo '{caminho_csv}' não foi encontrado.")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Ocorreu um erro durante o ETL: {e}")
            )