from django.db import models

class ClienteBruto(models.Model):
    id_cliente = models.CharField(max_length=50, unique=True)
    razao_social = models.CharField(max_length=255, blank=True, null=True)
    cnpj = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    telefone = models.CharField(max_length=50, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    uf = models.CharField(max_length=10, blank=True, null=True)
    data_cadastro = models.CharField(max_length=100, blank=True, null=True)
    vendedor_responsavel = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.id_cliente} - {self.razao_social}"


class ClienteTratado(models.Model):
    id_cliente = models.CharField(max_length=50, unique=True)
    razao_social = models.CharField(max_length=255, blank=True, null=True)
    cnpj = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    telefone = models.CharField(max_length=50, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    uf = models.CharField(max_length=10, blank=True, null=True)
    data_cadastro = models.DateField(blank=True, null=True)
    vendedor_responsavel = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.id_cliente} - {self.razao_social}"