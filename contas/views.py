from django.shortcuts import render, redirect, get_object_or_404
from perfil.models import Categoria
from .models import ContaPagar, ContaPaga
from django.contrib import messages
from django.contrib.messages import constants
from datetime import datetime
from perfil.models import Conta


def definir_contas(request):
    if request.method == "GET":
        categorias = Categoria.objects.all()
        return render(request, 'definir_contas.html', {'categorias': categorias})
    else:
        data = request.POST

        conta = ContaPagar(
            titulo=data['titulo'],
            categoria_id=data['categoria'],
            descricao=data['descricao'],
            valor=data['valor'],
            dia_pagamento=data['dia_pagamento']
        )
        conta.save()

        messages.add_message(request, constants.SUCCESS, 'Conta cadastrada com sucesso')
        return redirect('/contas/definir_contas')
    
def ver_contas(request):
    MES_ATUAL = datetime.now().month
    DIA_ATUAL = datetime.now().day
    
    contas = ContaPagar.objects.all()

    contas_pagas = ContaPaga.objects.filter(data_pagamento__month=MES_ATUAL).values('conta')

    contas_vencidas = contas.filter(dia_pagamento__lt=DIA_ATUAL).exclude(id__in=contas_pagas)
    
    contas_proximas_vencimento = contas.filter(dia_pagamento__lte = DIA_ATUAL + 5).filter(dia_pagamento__gte=DIA_ATUAL).exclude(id__in=contas_pagas)
    
    restantes = contas.exclude(id__in=contas_vencidas).exclude(id__in=contas_pagas).exclude(id__in=contas_proximas_vencimento)

    return render(request, 'ver_contas.html', {'contas_pagas': contas_pagas, 'contas_vencidas': contas_vencidas, 'contas_proximas_vencimento': contas_proximas_vencimento, 'restantes': restantes})

def pagar_conta(request, id):
    conta_a_pagar = get_object_or_404(ContaPagar, pk=id)
    user = Conta.objects.get(id=1)


    conta_pagar = ContaPaga(
        conta=conta_a_pagar,
        data_pagamento=datetime.now().date()
    )

    user.valor - conta_a_pagar.valor
    user.save()
    conta_pagar.save()
    messages.add_message(request, constants.SUCCESS, 'Conta paga com sucesso')
    return redirect('/contas/ver_contas/')