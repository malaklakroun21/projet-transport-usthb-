from decimal import Decimal
from django.db import models
from apps.clients.models import Client
from apps.logistics.models import Shipment


class Invoice(models.Model):
    TVA_RATE = Decimal('0.19')
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    shipments = models.ManyToManyField(Shipment)
    amount_ht = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    amount_tva = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    amount_ttc = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

#CALCULE HT, TVA, TTC


def calculate_amount_ht(self):
        return sum(
            (shipment.total_price for shipment in self.shipments.all()),
            Decimal('0.00')
        )
def calculate_totals(self):
        self.amount_ht = self.calculate_amount_ht()
        self.amount_tva = self.amount_ht * self.TVA_RATE
        self.amount_ttc = self.amount_ht + self.amount_tva


def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # save first (M2M needs ID)
        self.calculate_totals()
        super().save(update_fields=['amount_ht', 'amount_tva', 'amount_ttc'])


def total_paid(self):
        return sum(
            (p.amount for p in self.payment_set.all()),
            Decimal('0.00')
        )

def remaining_amount(self):
        return self.amount_ttc - self.total_paid()


def delete(self, *args, **kwargs):
        remaining = self.remaining_amount()
        if remaining > 0:
            self.client.balance -= remaining
            self.client.save()

        super().delete(*args, **kwargs)


class Payment(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    method = models.CharField(max_length=50)

