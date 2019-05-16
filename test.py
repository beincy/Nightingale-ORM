from NightingaleORM.dbmodel import Model
from NightingaleORM.fields import StringField,IntegerField,DateTimeField,FloatField
import datetime,json


class TaskModel(Model):
    __dbType__='pgsql'
    __dateBase__='resource'
    __schema__='DataAnnotations'

    tid=IntegerField('tid',True,0)
    tname=StringField('tname',False,'')
    tflag=IntegerField('tflag',False,0)
    trowstatus=IntegerField('trowstatus',False,0)
    tremark=StringField('tremark',False,'')
    tiid=IntegerField('tiid',False,0)
    tsid=IntegerField('tsid',False,0)
    tstartdate=DateTimeField('tstartdate',False,datetime.datetime.now())
    tenddate=DateTimeField('tenddate',False,datetime.datetime.now())
    tassignorid=IntegerField('tassignorid',False,0)
    temployerid=IntegerField('temployerid',False,0)
    tcreater=StringField('tcreater',False,'')
    tcreatetime=DateTimeField('tcreatetime',False,datetime.datetime.now())
    tupdater=StringField('tupdater',False,'')
    tupdatetime=DateTimeField('tupdatetime',False,datetime.datetime.now())
    tparentid=IntegerField('tparentid',False,0)
    # pass

class big():
    id=1
    name='ispig'


def mian():
    aa={'id':1,'name':"卞辉"}
    ee=TaskModel()
    sql,perm,countsql=ee.addShow(TaskModel.tid,TaskModel.tname).addWhere(TaskModel.tid==1).GetSelectSql(10)
    print(sql)
    print(perm)
    print(countsql)
    # print(TestModel.curTime)
    # print (json.dumps(ee))
    # print (TestModel.name)

if __name__ == "__main__":
    mian()
    