from extrato.models import Valores
from datetime import datetime


def fields_validate(*args):
    return all(arg.strip() != '' for arg in args)

def calcula_total(obj, campo):
    total = 0
    for i in obj:
        total += getattr(i, campo)

    return total

def calcula_equilibro_financeiro():
    gastos_essencias = Valores.objects.filter(data__month=datetime.now().month).filter(tipo='S').filter(categoria__essencial=True)
    gastos_nao_essencias = Valores.objects.filter(data__month=datetime.now().month).filter(tipo='S').filter(categoria__essencial=False)

    total_gastos_essenciais = calcula_total(gastos_essencias, 'valor')
    total_gastos_nao_essenciais = calcula_total(gastos_nao_essencias, 'valor')
    
    total = total_gastos_essenciais + total_gastos_nao_essenciais

    try:
        percentual_gastos_essenciais = int((total_gastos_essenciais * 100) / total)
        percentual_gastos_nao_essenciais = int((total_gastos_nao_essenciais) * 100 / total)

        return percentual_gastos_essenciais, percentual_gastos_nao_essenciais
    except:
        return 0, 0