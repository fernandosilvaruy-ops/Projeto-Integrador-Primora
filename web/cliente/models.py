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