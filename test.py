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


class ComplexEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return json.JSONEncoder.default(self, obj)

def mian():
    aa={'tid':1,'tname':"卞辉"}
    ee=TaskModel()
    sql,perm=ee.addUpdate(TaskModel.tname=="cat").addWhere(TaskModel.tid==1).updateSql()
    print(sql)
    print(perm)
    # print(countsql)
    # print(TestModel.curTime)
    # print (json.dumps(ee))
    # print (TestModel.name)
    # dd=TaskModel(**aa)
    # dd.tid=1
    # dd.tname='123'
    # dd.tflag=1
    # dd.tcreatetime=datetime.datetime.now()
    # sql,perm=dd.updateModel()
    # print(sql)
    # print(perm)
    # print(len(perm))
    # print (json.dumps(dd,cls=ComplexEncoder))


if __name__ == "__main__":
    mian()
    
