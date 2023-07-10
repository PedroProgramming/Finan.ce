from django.shortcuts import render
from perfil.models import Categoria
from extrato.models import Valores
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Sum
import json

def definir_planejamento(request):
    categorias = Categoria.objects.all()
    return render(request, 'definir_planejamento.html', {'categorias': categorias})

@csrf_exempt
def update_valor_categoria(request, id):
    novo_valor = json.load(request)['novo_valor']
    categoria = Categoria.objects.get(id=id)
    categoria.valor_planejamento = novo_valor
    categoria.save()

    return JsonResponse({'status': 'Sucesso'})

def ver_planejamento(request):
    categorias = Categoria.objects.all()
    valor_total_categoria = categorias.aggregate(Sum('valor_planejamento'))['valor_planejamento__sum']
    valores = Valores.objects.all().filter(tipo='S').aggregate(Sum('valor'))['valor__sum']
    return render(request, 'ver_planejamento.html', {'categorias': categorias, 'valores': valores, 'valor_total_categoria': valor_total_categoria})