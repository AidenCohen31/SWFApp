from django.db import models

# Create your models here.

class Rules(models.Model):
    SQL_ID = models.AutoField(db_column="SMID_SqlId", primary_key=True)
    RuleName = models.CharField(db_column="SMRULENM_RuleName", max_length = 50)
    RuleNumber = models.DecimalField(max_digits=8, decimal_places=0, db_column="SMRULE#_RuleNumber")
    RuleSequence = models.DecimalField(max_digits=8,decimal_places=0, db_column="SMRULESEQ_RuleSequence")
    ObjectType = models.CharField(max_length = 20, db_column="SMOBJTYPE_ObjectType")
    Table = models.CharField(max_length=10, db_column="SMTABLE_Table")
    Field = models.CharField(max_length=20, db_column= "SMFIELD_Field")
    TestObject = models.CharField(max_length=15, db_column="SMTSTOBJ_TestObject")
    Operator = models.CharField(max_length=2, db_column = "SMOPER_Operator")
    ObjectType = models.CharField(max_length=20, db_column = "SMTSTOTYP_ObjectType")
    TestTable = models.CharField(max_length=10, db_column="SMTSTOTBL_Table")
    TestField = models.CharField(max_length=20, db_column= "SMTSTOFLD_Field")
    TestValue = models.CharField(max_length=160, db_column="SMTSTVAL_TestValue")
    Status = models.CharField(max_length=20, db_column="SMSTATUS_Status")
    InEffectiveDate = models.DecimalField(max_digits=8,decimal_places=0, db_column="SMIEFF_InEffectiveDate")
    OutEffectiveDate = models.DecimalField(max_digits=8,decimal_places=0, db_column="SMOEFF_OutEffectiveDate")
    AddDate = models.DecimalField(max_digits=8,decimal_places=0, db_column="SMADTE_AddDate")
    AddTime = models.DecimalField(max_digits=6, decimal_places=0, db_column="SMATME_AddTime")
    AddUser = models.CharField(max_length=10, db_column="SMAUSR_AddUser")
    ProcessedDate = models.DecimalField(max_digits=8,decimal_places=0, db_column="SMUDTE_ProcessedDate")
    ProcessedTime = models.DecimalField(max_digits=6, decimal_places=0, db_column="SMUTME_ProcessedTime")
    ProcessedUser = models.CharField(max_length=10, db_column="SMUUSR_ProcessedUser")
    class Meta:
        managed = True
        db_table = '[OS].[ZMPSTSP_OrderStatusRules]'
        
        
        
class Master(models.Model):
    SQL_ID = models.AutoField(db_column="STID_SqlId", primary_key=True)
    InternalStatusCode = models.CharField(max_length=20, db_column="STICDE_InternalStatusCode")
    InternalDescription = models.CharField(max_length=50, db_column="STIDSC_InternalDescription")
    ExternalStatusCode = models.CharField(max_length=20, db_column="STECDE_InternalStatusCode")
    ExternalDescription = models.CharField(max_length=50, db_column="STEDSC_InternalDescription")
    StatusGroup1 = models.CharField(max_length=20, db_column="STGRP1_StatusGroup1")
    StatusGroup2 = models.CharField(max_length=20, db_column="STGRP2_StatusGroup2")
    StatusGroup3 = models.CharField(max_length=20, db_column="STGRP3_StatusGroup3")
    StatusGroup4 = models.CharField(max_length=20, db_column="STGRP4_StatusGroup4")
    StatusGroup5 = models.CharField(max_length=20, db_column="STGRP5_StatusGroup5")
    AddDate = models.DecimalField(max_digits=8,decimal_places=0, db_column="STADTE_AddDate")
    AddTime = models.DecimalField(max_digits=6, decimal_places=0, db_column="STATME_AddTime")
    AddUser = models.CharField(max_length=10, db_column="STAUSR_AddUser")
    ProcessedDate = models.DecimalField(max_digits=8,decimal_places=0, db_column="STUDTE_ProcessedDate")
    ProcessedTime = models.DecimalField(max_digits=6, decimal_places=0, db_column="STUTME_ProcessedTime")
    ProcessedUser = models.CharField(max_length=10, db_column="STUUSR_ProcessedUser")
    class Meta:
        managed = True
        db_table = '[OS].[ZORDSTSP_OrderStatusMaster]'
        
        
        
class LifeCycle(models.Model):
    SQL_ID = models.AutoField(db_column="LCID_SqlId", primary_key=True)
    OrderCategory = models.CharField(max_length=10,db_column="LCCTGY_OrderCategory")
    ProcessingSequence - models.DecimalField(max_digits=5,decimal_places=2,db_column="LCSEQ_ProcessingSequence")
    RuleName = models.CharField(max_length=50,db_column="LCRULENM_RuleName")
    InEffectiveDate = models.DecimalField(max_digits=8,decimal_places=0, db_column="LCEFFI_InEffectiveDate")
    OutEffectiveDate = models.DecimalField(max_digits=8,decimal_places=0, db_column="LCEFFO_OutEffectiveDate")
    AddDate = models.DecimalField(max_digits=8,decimal_places=0, db_column="LCADTE_AddDate")
    AddTime = models.DecimalField(max_digits=6, decimal_places=0, db_column="LCATME_AddTime")
    AddUser = models.CharField(max_length=10, db_column="LCAUSR_AddUser")
    ProcessedDate = models.DecimalField(max_digits=8,decimal_places=0, db_column="LCUDTE_ProcessedDate")
    ProcessedTime = models.DecimalField(max_digits=6, decimal_places=0, db_column="LCUTME_ProcessedTime")
    ProcessedUser = models.CharField(max_length=10, db_column="LCUUSR_ProcessedUser")
    class Meta:
        managed = False
        db_table = '[ACR].[DropdownSelections]'

class Temp(models.Model):
    CANAME = models.CharField(primary_key = True, max_length = 50, db_column = "CANAME")
    class Meta:
        managed = False