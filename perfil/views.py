from django.shortcuts import render, redirect, get_object_or_404
from .models import Categoria, Conta
from contas.models import ContaPaga, ContaPagar
from django.contrib import messages
from django.contrib.messages import constants
from django.db.models import Sum
from datetime import datetime

from extrato.models import Valores
from .utils import fields_validate, calcula_total, calcula_equilibro_financeiro

def home(request):
    MES_ATUAL = datetime.now().month
    DIA_ATUAL = datetime.now().day
    
    contas = ContaPagar.objects.all()

    contas_pagas = ContaPaga.objects.filter(data_pagamento__month=MES_ATUAL).values('conta')

    contas_vencidas = contas.filter(dia_pagamento__lt=DIA_ATUAL).exclude(id__in=contas_pagas)
    
    contas_proximas_vencimento = contas.filter(dia_pagamento__lte = DIA_ATUAL + 5).filter(dia_pagamento__gte=DIA_ATUAL).exclude(id__in=contas_pagas)

    valores = Valores.objects.filter(data__month=datetime.now().month)
    entradas = valores.filter(tipo='E')
    saidas = valores.filter(tipo='S')

    total_entradas = calcula_total(entradas, 'valor')
    total_saidas = calcula_total(saidas, 'valor')
    contas = Conta.objects.all()
    saldo_total = calcula_total(contas, 'valor')

    percentual_gastos_essenciais, percentual_gastos_não_essenciais = calcula_equilibro_financeiro()
    return render(request, 'home.html', {'contas_vencidas': contas_vencidas, 'contas_proximas_vencimento': contas_proximas_vencimento, 'percentual_gastos_essenciais': percentual_gastos_essenciais, 'percentual_gastos_não_essenciais': percentual_gastos_não_essenciais, 'total_saidas': total_saidas, 'total_entradas': total_entradas, 'contas': contas, 'saldo_total': saldo_total,})
def gerenciar(request):
    a = Conta.objects.all()
    for i in a:
        print(i.banco_choices)
    context = {
        'contas': Conta.objects.all(),
        'valor_total': f"{Conta.objects.all().aggregate(Sum('valor'))['valor__sum']:.2f}",
        'categorias': Categoria.objects.all(),
     }
    return render(request, 'gerenciar.html', context)

def cadastrar_banco(request):
    data = request.POST
    icone = request.FILES.get('icone')

    if not fields_validate(data['apelido'], data['banco'], data['tipo'], data['valor']):
        messages.add_message(request, constants.ERROR, 'Preencha todos os campos')
        return redirect('/perfil/gerenciar/')
    
    if icone == None:
        messages.add_message(request, constants.ERROR, 'Nenhuma imagem inserida!')
        return redirect('/perfil/gerenciar/')

    conta = Conta(
        apelido = data['apelido'],
        banco=data['banco'],
        tipo=data['tipo'],
        valor=data['valor'],
        icone=icone
    )
    conta.save()
    messages.add_message(request, constants.SUCCESS, 'Conta cadastrada com sucesso!')
    return redirect('/perfil/gerenciar/')

def deletar_banco(request, id):
    conta = get_object_or_404(Conta, pk=id)
    conta.delete()
    messages.add_message(request, constants.SUCCESS, 'Conta deletada com sucesso!')
    return redirect('/perfil/gerenciar/')

def cadastrar_categoria(request):
    data = request.POST
    essencial = bool(request.POST.get('essencial'))

    if not fields_validate(data['categoria']):
        messages.add_message(request, constants.ERROR, 'Campo inválido.')
        return redirect('/perfil/gerenciar/')

    categoria = Categoria(
        categoria=data['categoria'],
        essencial=essencial,
    )
    categoria.save()

    messages.add_message(request, constants.SUCCESS, 'Categoria cadastrada com sucesso')
    return redirect('/perfil/gerenciar/')

def update_categoria(request, id):
    categoria = get_object_or_404(Categoria, pk=id)

    categoria.essencial = not categoria.essencial
    categoria.save()
    messages.add_message(request, constants.INFO, 'Categoria alterada com sucesso')
    return redirect('/perfil/gerenciar/')

def dashboard(request):
    dados = {}
    categorias = Categoria.objects.all()

    for categoria in categorias:
        dados[categoria.categoria] = Valores.objects.filter(categoria=categoria).aggregate(Sum('valor'))['valor__sum']

    return render(request, 'dashboard.html', {'labels': list(dados.keys()), 'values': list(dados.values())})