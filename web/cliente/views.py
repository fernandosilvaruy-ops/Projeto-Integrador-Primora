from django.shortcuts import render
from django.shortcuts import render
from .models import Cliente


def listar_clientes(request):
    # função que utiliza o ORM para buscar todos os registos da tabela do PostgreSQL
    clientes = Cliente.objects.all()
    
    contexto = {
        'clientes': clientes
    }
    return render(request, 'cliente/lista.html', contexto)