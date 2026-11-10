from django.db import models


class Thing(models.Model):
    code = models.CharField(max_length=20)
    kind = models.CharField(max_length=20, blank=True)
    qty = models.DecimalField(max_digits=10, decimal_places=2, default=0)
