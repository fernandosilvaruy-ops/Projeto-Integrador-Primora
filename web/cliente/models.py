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
    codigo = models.CharField(max_length=10, unique=True, editable=False, blank=True)


def save(self, *args, **kwargs):
    super().save(*args, **kwargs)          # gera o id_cliente
    if not self.codigo:
        self.codigo = f"CLI{self.id_cliente:04d}"
        super().save(update_fields=["codigo"])

    
def __str__(self):
    return f"{self.codigo} - {self.razao_social}"