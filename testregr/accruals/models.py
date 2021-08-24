from django.db import models

# Create your models here.

class AccrualR(models.Model):
    RuleName = models.CharField(max_length=50, db_column="ARName_RuleName")
    RuleNumber = models.IntegerField(db_column="ARRULE#_RuleNumber")
    RuleSequence = models.IntegerField(db_column="ARRULESEQ_RuleSequence")
    ObjectType = models.CharField(max_length=20,db_column="AROBJTYPE_ObjectType")
    Table = models.CharField(max_length=10,db_column="ARTABLE_Table")
    Field = models.CharField(max_length=20, db_column="ARFIELD_Field")
    TestObject = models.CharField(max_length=15, db_column="ARTSTOBJ_TestObject")
    Operator = models.CharField(max_length=2, db_column="AROPER_Operator")
    TestValue = models.CharField(max_length=160, db_column="ARTSTVAL_TestValue")
    InEffectiveDate = models.DecimalField(max_digits=8,decimal_places=0,db_column="AREFFI_InEffectiveDate")
    OutEffectiveDate = models.DecimalField(max_digits=8,decimal_places=0, db_column="AREFFO_OutEffectiveDate")
    AddDate = models.DecimalField(max_digits=8,decimal_places=0, db_column="ARADTE_AddDate")
    AddTime = models.DecimalField(max_digits=6, decimal_places=0, db_column="ARATME_AddTime")
    AddUser = models.CharField(max_length=10, db_column="ARAUSR_AddUser")
    ProcessedDate = models.DecimalField(max_digits=8,decimal_places=0,db_column="ARUDTE_ProcessedDate")
    ProcessedTime = models.DecimalField(max_digits=6, decimal_places=0, db_column="ARUTME_ProcessedTime")
    ProcessedUser = models.CharField(max_length=10, db_column="ARUUSR_ProcessedUser")
    SQL_ID = models.IntegerField(primary_key=True, db_column="SQL_ID")
    def _do_insert(self, manager, using, fields, update_pk, raw):
        return super(AccrualR, self)._do_insert(
            manager, using,
            [f for f in fields if f.attname not in ['SQL_ID']],
            update_pk, raw)
    class Meta:
        managed = True
        db_table = '[ACR].[ZACRRULP_AccrualRules]'
        
        
        
class AccrualD(models.Model):
    AccrualName = models.CharField(max_length=50, primary_key=True, db_column="ACNAME_AccrualName")
    AccrualType = models.CharField(max_length=15, db_column="ACTYPE_AccrualType")
    InEffectiveDate = models.DecimalField(max_digits=8,decimal_places=0, db_column="ACEFFI_InEffectiveDate")
    OutEffectiveDate = models.DecimalField(max_digits=8,decimal_places=0, db_column="ACEFFO_OutEffectiveDate")
    InvoiceByDate = models.DecimalField(max_digits=8,decimal_places=0,db_column="ACINVBY_InvoiceByDate")
    AmtPerLine = models.DecimalField(max_digits=15, decimal_places =2, db_column="ACLINE$_AmtPerLine")
    AmtPerUnit = models.DecimalField(max_digits=15, decimal_places =2, db_column="ACUNIT$_AmtPerUnit")
    CostPercent = models.DecimalField(max_digits = 3, decimal_places = 2, db_column="ACCOSTP_CostPercent")
    PricePercent = models.DecimalField(max_digits=3, decimal_places = 2, db_column="ACPRICP_PricePercent")
    MonthlyThreshold = models.DecimalField(max_digits=15, decimal_places=2, db_column="ACMNTH$_MonthlyThreshold")
    AnnualThreshold = models.DecimalField(max_digits=15,decimal_places=2, db_column="ACANN$_AnnualThreshold")
    FromAlphaCode = models.CharField(max_length=10, db_column="ACFALPH_FromAlphaCode")
    ToAlphaCode = models.CharField(max_length=10, db_column="ACTALPH_ToAlphaCode")
    AddDate = models.DecimalField(max_digits=8,decimal_places=0, db_column="ACADTE_AddDate")
    AddTime = models.DecimalField(max_digits=6, decimal_places=0, db_column="ACATME_AddTime")
    AddUser = models.CharField(max_length=10, db_column="ACAUSR_AddUser")
    ProcessedDate = models.DecimalField(max_digits=8,decimal_places=0, db_column="ACPDTE_ProcessedDate")
    ProcessedTime = models.DecimalField(max_digits=6, decimal_places=0, db_column="ACPTME_ProcessedTime")
    ProcessedUser = models.CharField(max_length=10, db_column="ACPUSR_ProcessedUser")
    class Meta:
        managed = True
        db_table = '[ACR].[ZACRDEFP_AccrualDefinition]'
        
        
        
class Dropdown(models.Model):
    ids = models.AutoField(primary_key=True, db_column="id")
    view_name = models.CharField(max_length=50)
    entry_name = models.CharField(max_length=50)
    value_name = models.CharField(max_length=50)
    class Meta:
        managed = False
        db_table = '[ACR].[DropdownSelections]'
        
