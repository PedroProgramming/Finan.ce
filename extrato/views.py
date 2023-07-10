from django.shortcuts import render, redirect
from perfil.models import Conta, Categoria
from .models import Valores
from django.contrib import messages
from django.contrib.messages import constants
from datetime import datetime, timedelta
from django.template.loader import render_to_string
from django.conf import settings
import os
from io import BytesIO
from weasyprint import HTML
from django.http import FileResponse

def novo_valor(request):
    if request.method == 'POST':
        data = request.POST
        
        valores = Valores(
            valor=data['valor'],
            categoria_id=data['categoria'],
            descricao=data['descricao'],
            data=data['data'],
            conta_id=data['conta'],
            tipo=data['tipo'],
        )
        valores.save()

        conta = Conta.objects.get(id=data['conta'])

        if data['tipo'] == 'E':
            conta.valor += int(data['valor'])
        else:
            conta.valor -= int(data['valor'])
        conta.save()

        messages.add_message(request, constants.SUCCESS, 'Entrada/Saida cadastrada com sucesso')
        return redirect('/extrato/novo_valor')

    contas = Conta.objects.all()
    categorias = Categoria.objects.all() 
    return render(request, 'novo_valor.html', {'contas': contas, 'categorias': categorias})

def view_extrato(request):
    contas = Conta.objects.all()
    categorias = Categoria.objects.all()
    conta_get = request.GET.get('conta')
    categoria_get = request.GET.get('categoria')
    periodo_get = request.GET.get('periodo')
    valores = Valores.objects.filter(data__month=datetime.now().month)

    if conta_get:
        valores = valores.filter(conta__id=conta_get)

    if categoria_get:
        valores = valores.filter(categoria__id=categoria_get)

    if periodo_get:
        date_current = datetime.now().date()
        date_7_days = date_current - timedelta(days=int(periodo_get))

        valores = valores.filter(data__gte=date_7_days, data__lte=date_current)
    
    if request.GET.get('limpar_filtro'):
        valores = Valores.objects.filter(data__month=datetime.now().month)
        
    return render(request, 'view_extrato.html', {'valores': valores, 'contas': contas, 'categorias': categorias})

def exportar_pdf(request):
    valores = Valores.objects.filter(data__month=datetime.now().month)
    contas = Conta.objects.all()
    categorias = Categoria.objects.all()
    
    path_template = os.path.join(settings.BASE_DIR, 'templates/partials/extrato.html')
    path_output = BytesIO()

    template_render = render_to_string(path_template, {'valores': valores, 'contas': contas, 'categorias': categorias})
    HTML(string=template_render).write_pdf(path_output)
    path_output.seek(0)

    return FileResponse(path_output, filename="extrato.pdf")