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
        return self.razao_social

class AuditoriaAlteracao(models.Model):
    cliente = models.ForeignKey(
    Cliente, on_delete=models.PROTECT, 
    related_name='auditoria_altera'
    )
    id_cliente = models.IntegerField()
    campo_alterado = models.CharField(max_length=100)
    valor_original = models.TextField(null=True, blank=True)
    valor_tratado = models.TextField(null=True, blank=True)
    criterio = models.CharField(max_length=225)
    data_alteracao = models.DateTimeField(auto_now_add=True)
