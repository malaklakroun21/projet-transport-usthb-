from django.shortcuts import render
from django.shortcuts import get_object_or_404
from .models import Invoice, Payment

#auto update solde client lors d'un paiement

def register_payment(invoice_id, amount, method):
    invoice = get_object_or_404(Invoice, id=invoice_id)

    Payment.objects.create(
        invoice=invoice,
        amount=amount,
        method=method
    )

    remaining = invoice.remaining_amount()

    if remaining > 0:
        invoice.client.balance += remaining
        invoice.client.save()

#Journal des invoices (consultation + filtres) (I AM NOT SURE ABOUT THE TEMPLATE PATHS)

def invoice_list(request):
    invoices = Invoice.objects.all()

    if request.GET.get('client'):
        invoices = invoices.filter(client_id=request.GET['client'])

    if request.GET.get('date'):
        invoices = invoices.filter(created_at__date=request.GET['date'])

    return render(request, 'billing/invoice_list.html', {'invoices': invoices})


def payment_list(request):
    payments = Payment.objects.all()

    if request.GET.get('invoice'):
        payments = payments.filter(invoice_id=request.GET['invoice'])

    if request.GET.get('method'):
        payments = payments.filter(method=request.GET['method'])

    return render(request, 'billing/payment_list.html', {'payments': payments})

