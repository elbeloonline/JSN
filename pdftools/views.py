# -*- coding: utf-8 -*-


from django.contrib.auth.decorators import login_required
from django.shortcuts import render


# Create your views here.
@login_required
def results_comparison(request, order_id):
    context = {
        'order_id': order_id
    }
    return render(request, 'orders/results_comparison.html', context)


@login_required
def cj_comparison(request):
    from .utils import JudgmentsExtractor
    return JudgmentsExtractor.cj_pdf_comparison(request)
