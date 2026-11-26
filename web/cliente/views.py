import csv
import io
from pathlib import Path
from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from .forms import UploadArquivoETLForm
from .models import ClienteBruto, ClienteTratado, AuditoriaAlteracao
from datetime import datetime, date

RAIZ_PROJETO = Path(settings.BASE_DIR).parent
CSV_RAIZ = RAIZ_PROJETO / "clientes_distribuidora_vetor.csv"


def _persistir_linhas_no_banco(linhas):
    for linha in linhas:
        # Normaliza chaves em minúsculo para evitar problemas com maiúsculas/espaços no CSV
        dados = {k.strip().lower(): (v.strip() if isinstance(v, str) else v) for k, v in linha.items() if k}

        id_cliente = dados.get("id_cliente") or ""
        razao_social = dados.get("razao_social") or ""
        cnpj = dados.get("cnpj") or ""
        email = dados.get("email") or ""
        telefone = dados.get("telefone") or ""
        cidade = dados.get("cidade") or ""
        bairro_informado = dados.get("bairro_informado") or ""
        uf = dados.get("uf") or ""
        vendedor_responsavel = dados.get("vendedor_responsavel") or ""

        if not razao_social and not id_cliente and not cnpj:
            continue

        # Grava no ClienteBruto (evita duplicar se já existir pelo id_cliente quando preenchido)
        if id_cliente:
            ClienteBruto.objects.update_or_create(
                id_cliente=id_cliente,
                defaults={
                    "razao_social": razao_social,
                    "cnpj": cnpj,
                    "email": email,
                    "telefone": telefone,
                    "cidade": cidade,
                    "bairro_informado": bairro_informado,
                    "uf": uf,
                    "vendedor_responsavel": vendedor_responsavel,
                },
            )
        else:
            ClienteBruto.objects.create(
                id_cliente=id_cliente,
                razao_social=razao_social,
                cnpj=cnpj,
                email=email,
                telefone=telefone,
                cidade=cidade,
                bairro_informado=bairro_informado,
                uf=uf,
                vendedor_responsavel=vendedor_responsavel,
            )


def upload_csv_raiz(request):
    if request.method != "POST":
        return redirect("lista_clientes")

    form = UploadArquivoETLForm(request.POST, request.FILES)
    if not form.is_valid():
        messages.error(request, "Selecione um arquivo .csv válido.")
        return redirect("lista_clientes")

    arquivo = form.cleaned_data["arquivo"]
    raw_bytes = arquivo.read()

    try:
        texto_csv = raw_bytes.decode("utf-8-sig")
    except UnicodeDecodeError:
        texto_csv = raw_bytes.decode("cp1252")

    # Detecta separador (, ou ;) automaticamente
    primeira_linha = texto_csv.splitlines()[0] if texto_csv.splitlines() else ","
    delimitador = ";" if primeira_linha.count(";") > primeira_linha.count(",") else ","

    leitor = csv.DictReader(io.StringIO(texto_csv), delimiter=delimitador)
    if not leitor.fieldnames:
        messages.error(request, "O CSV está vazio ou sem cabeçalho.")
        return redirect("lista_clientes")

    # Normaliza nomes das colunas (ex.: "ID Cliente" ou "id_cliente" -> "id_cliente")
    fieldnames_norm = [
        col.strip().lower().replace(" ", "_").replace("/", "_")
        for col in leitor.fieldnames
    ]
    leitor.fieldnames = fieldnames_norm

    registros_por_id = {}
    for linha in leitor:
        id_cli = (linha.get("id_cliente") or "").strip()
        if not id_cli:
            continue

        registros_por_id[id_cli] = {
            "razao_social": (linha.get("razao_social") or "").strip(),
            "cnpj": (linha.get("cnpj") or "").strip(),
            "email": (linha.get("email") or "").strip(),
            "telefone": (linha.get("telefone") or "").strip(),
            "cidade": (linha.get("cidade") or "").strip(),
            "uf": (linha.get("uf") or "").strip(),
            "bairro_informado": (linha.get("bairro_informado") or linha.get("bairro") or "").strip(),
            "data_cadastro": (linha.get("data_cadastro") or "").strip(),
            "vendedor_responsavel": (linha.get("vendedor_responsavel") or "").strip(),
        }

    if not registros_por_id:
        messages.warning(request, "Nenhum registro válido com id_cliente foi encontrado no CSV.")
        return redirect("lista_clientes")

    # Salva o conteúdo enviado no CSV da raiz do projeto
    caminho_csv_raiz = Path(settings.BASE_DIR).parent / "clientes_brutos.csv"
    with open(caminho_csv_raiz, "w", encoding="utf-8", newline="") as f_out:
        escritor = csv.DictWriter(
            f_out,
            fieldnames=["id_cliente", *next(iter(registros_por_id.values())).keys()],
            delimiter=",",
        )
        escritor.writeheader()
        for id_cli, dados in registros_por_id.items():
            escritor.writerow({"id_cliente": id_cli, **dados})

    # Sincroniza o banco com o CSV (remove ausentes + cria/atualiza presentes)
    try:
        with transaction.atomic():
            removidos_qtd, _ = ClienteBruto.objects.exclude(
                id_cliente__in=registros_por_id.keys()
            ).delete()

            criados_ou_atualizados = 0
            for id_cli, dados in registros_por_id.items():
                ClienteBruto.objects.update_or_create(
                    id_cliente=id_cli,
                    defaults=dados,
                )
                criados_ou_atualizados += 1

        messages.success(
            request,
            f"CSV sincronizado: {criados_ou_atualizados} registro(s) salvo(s)/atualizado(s) e {removidos_qtd} removido(s).",
        )
    except Exception as exc:
        messages.error(request, f"Erro ao sincronizar com o banco: {exc}")

    return redirect("lista_clientes")


def listar_clientes(request):
    clientes = ClienteBruto.objects.all()
    form_upload = UploadArquivoETLForm()
    context = {
        "clientes": clientes,
        "total_registos": clientes.count(),
        "form_upload": form_upload,
    }
    return render(request, "cliente/lista.html", context)


def clientes_tratados(request):
    clientes = ClienteTratado.objects.all()
    form_upload = UploadArquivoETLForm()
    context = {
        "clientes": clientes,
        "total_registos": clientes.count(),
        "form_upload": form_upload,
    }
    return render(request, "cliente/clientes_tratados.html", context)


def lista_auditoria(request):
    auditorias = AuditoriaAlteracao.objects.all().order_by("-data_alteracao")
    context = {"auditorias": auditorias, "total_registos": auditorias.count()}
    return render(request, "cliente/auditoria.html", context)

def parse_data_cadastro(valor):
    if not valor:
        return None
    if isinstance(valor, date) and not isinstance(valor, datetime):
        return valor
    if isinstance(valor, datetime):
        return valor.date()

    texto = str(valor).strip()
    if not texto:
        return None

    for formato in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(texto, formato).date()
        except ValueError:
            continue

    return None

def tratar_clientes_pendentes(request):
    if request.method != "POST":
        return redirect("lista_clientes")

    ids_ja_tratados = ClienteTratado.objects.values_list("id_cliente", flat=True)
    pendentes = ClienteBruto.objects.exclude(id_cliente__in=ids_ja_tratados)

    total_pendentes = pendentes.count()
    if total_pendentes == 0:
        messages.info(request, "Não há clientes novos pendentes de tratamento.")
        return redirect("lista_clientes")

    try:
        with transaction.atomic():
            for bruto in pendentes:
                dados_tratados = {
                    "razao_social": (bruto.razao_social or "").strip().title(),
                    "cnpj": (bruto.cnpj or "").strip(),
                    "email": (bruto.email or "").strip().lower(),
                    "telefone": (bruto.telefone or "").strip(),
                    "cidade": (bruto.cidade or "").strip().title(),
                    "uf": (bruto.uf or "").strip().upper(),
                    "bairro_informado": (bruto.bairro_informado or "").strip().title(),
                    "data_cadastro": parse_data_cadastro(bruto.data_cadastro),
                    "vendedor_responsavel": (bruto.vendedor_responsavel or "").strip().title(),
                }

                cliente_tratado = ClienteTratado.objects.create(
                    id_cliente=bruto.id_cliente,
                    **dados_tratados,
                )

                for campo, valor_novo in dados_tratados.items():
                    valor_antigo = getattr(bruto, campo, "")
                    if str(valor_antigo or "") != str(valor_novo or ""):
                        AuditoriaAlteracao.objects.create(
                            cliente=cliente_tratado,
                            id_cliente=str(bruto.id_cliente),
                            campo_alterado=campo,
                            valor_original=str(valor_antigo or ""),
                            valor_tratado=str(valor_novo or ""),
                            criterio="Tratamento de clientes pendentes via web",
                        )

        messages.success(request, f"{total_pendentes} cliente(s) tratado(s) e registrado(s) na auditoria.")
        return redirect("clientes_tratados")
    except Exception as exc:
        messages.error(request, f"Erro ao tratar clientes pendentes: {exc}")
        return redirect("lista_clientes")


def excluir_cliente_tratado(request, pk):
    if request.method != "POST":
        return redirect("clientes_tratados")

    cliente = get_object_or_404(ClienteTratado, pk=pk)
    id_removido = cliente.id_cliente
    cliente.delete()

    messages.success(request, f"Cliente {id_removido} removido da lista de tratados.")
    return redirect("clientes_tratados")