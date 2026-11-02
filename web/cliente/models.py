from django.db import models


class Cliente(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    razao_social = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    telefone = models.CharField(max_length=50, blank=True, null=True)
    cnpj = models.CharField(max_length=20, unique=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cep = models.CharField(max_length=20, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    uf = models.CharField(max_length=2, blank=True, null=True)
    data_cadastro = models.DateField(blank=True, null=True)
    vendedor = models.CharField(max_length=100, blank=True, null=True)

    
    def __str__(self):
        return self.razao_social