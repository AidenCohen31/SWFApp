from django.db import models

# Create your models here.


class Datas(models.Model):
    id = models.IntegerField(primary_key=True)
    firstname = models.CharField(db_column='FirstName', max_length=1, blank=True, null=True)  # Field name made lowercase.
    lastname = models.CharField(db_column='LastName', max_length=1, blank=True, null=True)  # Field name made lowercase.
    age = models.IntegerField(db_column='Age', blank=True, null=True)  # Field name made lowercase.
    ssn = models.IntegerField(db_column='SSN', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'datas'

class EDI(models.Model):
    FOrderNumber = models.IntegerField(primary_key=True)
    TOrderNumber = models.IntegerField()
    Customer = models.CharField(max_length=6)
    PriceAs = models.CharField(max_length=6)
    PONumber = models.CharField(max_length=20)
    ProductNumber = models.CharField(max_length=15)
    LineNumber = models.DecimalField(max_digits=5,decimal_places=2)
    Qty = models.DecimalField(max_digits=9,decimal_places=1)
    PRICE = models.DecimalField(max_digits=38,decimal_places=2)
    PRODPRICE = models.DecimalField(max_digits=38,decimal_places=2)
    PriceDiff = models.DecimalField(max_digits=38,decimal_places=2)
    PercentChange = models.CharField(max_length=31)
    ProductionDiscount = models.DecimalField(max_digits=38,decimal_places=3)
    FourZeroDiscount = models.DecimalField(max_digits=38,decimal_places=3)
    DIFFWITHDISCOUNTS = models.DecimalField(max_digits=38,decimal_places=2)
    class Meta:
        managed = False
        db_table = 'EDI_PricingComparison2240'
    
