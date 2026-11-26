import csv
import io
from pathlib import Path
from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect, render
from .forms import UploadArquivoETLForm
from .models import ClienteBruto, ClienteTratado, AuditoriaAlteracao


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
        messages.error(request, "Envie um arquivo CSV válido antes de continuar.")
        return redirect("lista_clientes")

    arquivo = form.cleaned_data["arquivo"]
    raw_bytes = arquivo.read()

    try:
        texto_csv = raw_bytes.decode("utf-8-sig")
    except UnicodeDecodeError:
        texto_csv = raw_bytes.decode("cp1252")
        # Detecta separador (, ou ;) automaticamente
        amostra = texto_csv[:2048]
        separador = ";" if amostra.count(";") > amostra.count(",") else ","

        leitor = csv.DictReader(io.StringIO(texto_csv), delimiter=separador)
        linhas = list(leitor)

        if not linhas:
            messages.warning(request, "O arquivo CSV enviado está vazio.")
            return redirect("lista_clientes")

        # Salva o CSV na raiz do projeto, criando o diretório se necessário
        CSV_RAIZ.parent.mkdir(parents=True, exist_ok=True)
        arquivo_ja_existia = CSV_RAIZ.exists() and CSV_RAIZ.stat().st_size > 0

        with open(CSV_RAIZ, "a", newline="", encoding="utf-8") as f_out:
            escritor = csv.DictWriter(f_out, fieldnames=leitor.fieldnames)
            if not arquivo_ja_existia:
                escritor.writeheader()
            for linha in linhas:
                escritor.writerow({campo: linha.get(campo, "") for campo in leitor.fieldnames})

        # Salva/atualiza os registros no banco de dados dentro de uma transação atômica
        with transaction.atomic():
            _persistir_linhas_no_banco(linhas)

        messages.success(
            request,
            f"{len(linhas)} registro(s) adicionados ao CSV da raiz e salvos no banco de dados.",
        )
    except Exception as exc:
        messages.error(request, f"Erro ao processar o CSV: {exc}")

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