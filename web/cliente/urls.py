from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_clientes, name='lista_clientes'),
    path('tratados/', views.clientes_tratados, name='clientes_tratados'),
    path('auditoria/', views.lista_auditoria, name='lista_auditoria'),
]