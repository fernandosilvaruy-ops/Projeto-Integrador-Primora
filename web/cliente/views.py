import csv
import json
import urllib.request
import unicodedata
import re
import io
from pathlib import Path
import sys
from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from .forms import UploadArquivoETLForm
from .models import ClienteBruto, ClienteTratado, AuditoriaAlteracao
from datetime import datetime, date

RAIZ_PROJETO = Path(settings.BASE_DIR).parent
CSV_RAIZ = RAIZ_PROJETO / "clientes_distribuidora_vetor.csv"

RAIZ_PROJETO = Path(settings.BASE_DIR).parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

CEPS_INVALIDOS_CONHECIDOS = {
    "00000000", "11111111", "22222222", "33333333", "44444444",
    "55555555", "66666666", "77777777", "88888888", "99999999",
}

RAIZ_PROJETO = Path(__file__).resolve().parents[2]
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

CAMINHO_SERVICO_CEP = str(Path(settings.BASE_DIR).parent / "src1" / "servico")
if CAMINHO_SERVICO_CEP not in sys.path:
    sys.path.insert(0, CAMINHO_SERVICO_CEP)


from src1.servico.cep_servico import buscar_cep_por_bairro
from cep_servico import buscar_cep

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
            "cep": (linha.get("cep") or "").strip(),
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
                cep_atual = (getattr(bruto, "cep", "") or "").strip()
                cidade_base = (bruto.cidade or "").strip()
                uf_base = (bruto.uf or "").strip()
                bairro_base = (bruto.bairro_informado or "").strip()

                cep_encontrado = ""
                dados_cep = {}
                origem_cep = "nenhuma"

                if cep_atual:
                    cep_encontrado = cep_atual
                    origem_cep = "proprio_bruto"
                else:
                    # 1. Consulta o banco primeiro por cidade + uf + bairro_informado
                    filtro_local = {
                        "bairro_informado__iexact": bairro_base,
                    }
                    if cidade_base:
                        filtro_local["cidade__iexact"] = cidade_base
                    if uf_base:
                        filtro_local["uf__iexact"] = uf_base

                    if bairro_base:
                        tratado_com_cep = (
                            ClienteTratado.objects.filter(**filtro_local)
                            .exclude(cep__isnull=True)
                            .exclude(cep="")
                            .first()
                        )
                        if tratado_com_cep:
                            cep_encontrado = tratado_com_cep.cep.strip()
                            origem_cep = "banco_tratado"
                        else:
                            bruto_com_cep = (
                                ClienteBruto.objects.filter(**filtro_local)
                                .exclude(cep__isnull=True)
                                .exclude(cep="")
                                .first()
                            )
                            if bruto_com_cep:
                                cep_encontrado = bruto_com_cep.cep.strip()
                                origem_cep = "banco_bruto"

                    # 2. Só consulta o ViaCEP se não encontrou CEP no banco
                    if not cep_encontrado:
                        consulta_viacep = buscar_cep(cep_atual) if cep_atual else None
                        if isinstance(consulta_viacep, dict) and "erro" not in consulta_viacep:
                            dados_cep = consulta_viacep
                            cep_encontrado = str(dados_cep.get("cep") or "").strip()
                            origem_cep = "viacep"

                cep_valido = bool(cep_encontrado) and not dados_cep
                if dados_cep and "erro" not in dados_cep:
                    cep_valido = True

                cep_tratado = cep_encontrado
                cidade_tratada = cidade_base.title()
                uf_tratada = uf_base.upper()
                bairro_tratado = bairro_base.title()

                if origem_cep == "viacep" and cep_valido:
                    if dados_cep.get("localidade"):
                        cidade_tratada = str(dados_cep["localidade"]).strip().title()
                    if dados_cep.get("uf"):
                        uf_tratada = str(dados_cep["uf"]).strip().upper()
                    if dados_cep.get("bairro"):
                        bairro_tratado = str(dados_cep["bairro"]).strip().title()

                cep_tratado = resolver_cep_tratado(
                    cep_atual=cep_tratado,
                    cidade=cidade_tratada,
                    uf=uf_tratada,
                    bairro=bairro_tratado,
                )

                dados_tratados = {
                    "razao_social": (bruto.razao_social or "").strip().title(),
                    "cnpj": (bruto.cnpj or "").strip(),
                    "cep": cep_tratado,
                    "email": (bruto.email or "").strip().lower(),
                    "telefone": (bruto.telefone or "").strip(),
                    "cidade": cidade_tratada,
                    "uf": uf_tratada,
                    "bairro_informado": bairro_tratado,
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
                        if campo == "cep" and origem_cep in {"banco_tratado", "banco_bruto"}:
                            criterio = "Reaproveitamento de CEP do banco por bairro/cidade/UF"
                        elif origem_cep == "viacep" and campo in {"cep", "cidade", "uf", "bairro_informado"}:
                            criterio = "Validação e enriquecimento ViaCEP"
                        else:
                            criterio = "Tratamento de clientes pendentes via web"

                        AuditoriaAlteracao.objects.create(
                            cliente=cliente_tratado,
                            id_cliente=str(bruto.id_cliente),
                            campo_alterado=campo,
                            valor_original=str(valor_antigo or ""),
                            valor_tratado=str(valor_novo or ""),
                            criterio=criterio,
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

def limpar_bairro_para_busca(bairro: str) -> str:
    texto = (bairro or "").replace("\ufffd", " ")
    texto = re.sub(r"\([^)]*\)", " ", texto)
    return " ".join(texto.split()).strip()


def resolver_cep_cliente(bruto, modelo_bruto, modelo_tratado) -> str:
    cep_existente = str(getattr(bruto, "cep", "") or "").strip()
    if cep_existente:
        return cep_existente

    bairro_limpo = limpar_bairro_para_busca(getattr(bruto, "bairro_informado", ""))
    cidade = str(getattr(bruto, "cidade", "") or "").strip()
    uf = str(getattr(bruto, "uf", "") or "").strip().upper()

    if bairro_limpo:
        tratado_existente = (
            modelo_tratado.objects.filter(
                bairro_informado__iexact=bairro_limpo,
                cidade__iexact=cidade,
            )
            .exclude(cep__isnull=True)
            .exclude(cep__exact="")
            .first()
        )
        if tratado_existente and tratado_existente.cep:
            return str(tratado_existente.cep).strip()

        bruto_existente = (
            modelo_bruto.objects.filter(
                bairro_informado__iexact=bairro_limpo,
                cidade__iexact=cidade,
            )
            .exclude(cep__isnull=True)
            .exclude(cep__exact="")
            .first()
        )
        if bruto_existente and bruto_existente.cep:
            return str(bruto_existente.cep).strip()

        if cidade:
            cep_viacep = buscar_cep_por_bairro(cidade, uf, bairro_limpo)
            if cep_viacep:
                return cep_viacep.strip()

    return ""

def _normalizar_texto(valor: str | None) -> str:
    texto = (valor or "").strip().lower()
    sem_acento = "".join(
        c for c in unicodedata.normalize("NFKD", texto)
        if not unicodedata.combining(c)
    )
    return " ".join(sem_acento.split())


def _cep_valido_no_viacep(cep_digitos: str, cidade: str, uf: str) -> bool:
    if not re.fullmatch(r"\d{8}", cep_digitos) or cep_digitos in CEPS_INVALIDOS_CONHECIDOS:
        return False

    try:
        url = f"https://viacep.com.br/ws/{cep_digitos}/json/"
        with urllib.request.urlopen(url, timeout=5) as resp:
            dados = json.loads(resp.read().decode("utf-8"))
    except Exception:
        return False

    if not isinstance(dados, dict) or dados.get("erro"):
        return False

    uf_ok = _normalizar_texto(dados.get("uf")) == _normalizar_texto(uf)
    cidade_ok = _normalizar_texto(dados.get("localidade")) == _normalizar_texto(cidade)
    return uf_ok and cidade_ok


def resolver_cep_tratado(cep_atual: str | None, cidade: str | None, uf: str | None, bairro: str | None) -> str:
    cep_limpo = (cep_atual or "").strip()
    digitos = re.sub(r"\D", "", cep_limpo)

    if _cep_valido_no_viacep(digitos, cidade or "", uf or ""):
        return cep_limpo

    novo_cep = (buscar_cep_por_bairro(cidade or "", uf or "", bairro or "") or "").strip()
    return novo_cep or cep_limpo