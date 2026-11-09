from django.shortcuts import render
from .models import ClienteBruto, ClienteTratado


def listar_clientes(request):
    # pagina principal: mostra todos os clientes cadastrados no banco de dados PostgreSQL
    clientes = ClienteBruto.objects.all()
    total_registos = clientes.count()
    return render(request, 'cliente/lista.html', {
        'clientes': clientes,
        'total_registos': total_registos
    })  

def clientes_tratados_view(request):
    # Pagina de tratados: mostra apenas os clientes validados e limpos
    clientes = ClienteTratado.objects.all()
    total_registos = clientes.count()
    return render(request, 'cliente/clientes_tratados.html', {
        'clientes': clientes,
        'total_registos': total_registos
    })