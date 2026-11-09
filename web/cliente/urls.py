from django.urls import path
from . import views

urlpatterns = [
    # Rota principal de clientes (ficará em /clientes/)
    path('', views.listar_clientes, name='lista_clientes'),
    
    # Rota de dados tratados (ficará em /clientes/tratados/)
    path('tratados/', views.clientes_tratados_view, name='clientes_tratados'),
]