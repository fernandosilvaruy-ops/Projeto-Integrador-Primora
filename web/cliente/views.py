from django.shortcuts import render
from .models import ClienteBruto, ClienteTratado, AuditoriaAlteracao

def listar_clientes(request):
    clientes = ClienteBruto.objects.all()
    context = {'clientes': clientes, 'total_registos': clientes.count()}
    return render(request, 'cliente/lista.html', context)

def clientes_tratados(request):
    clientes = ClienteTratado.objects.all()
    context = {'clientes': clientes, 'total_registos': clientes.count()}
    return render(request, 'cliente/clientes_tratados.html', context)

def lista_auditoria(request):
    auditorias = AuditoriaAlteracao.objects.all().order_by('-data_alteracao')
    context = {'auditorias': auditorias, 'total_registos': auditorias.count()}
    return render(request, 'cliente/auditoria.html', context)