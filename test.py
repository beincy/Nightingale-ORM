from NightingaleORM.dbmodel import Model
from NightingaleORM.fields import StringField,IntegerField,DateTimeField,FloatField
import datetime,json,ujson
from PYLINQ import PYLINQ


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
    # selectSQL,parameters,countSQL=ee.addShow(TaskModel.tname) \
    #     .addShow("tenddate") \
    #     .addWhere(TaskModel.tid==1) \
    #     .addWhere(TaskModel.tupdatetime==datetime.datetime.now()) \
    #     .startBrackets() \
    #     .addWhere(TaskModel.tiid==2) \
    #     .addWhere("temployerid>0") \
    #     .addWhere(("tassignorid","in","1,2")) \
    #      addWhere(("tassignorid","in",[1,2])) \
    #     .addWhere(TaskModel.tremark=='das')\
    #     .endBracket() \
    #     .selectSql(100)
    # print(selectSQL)
    # print(parameters)
    # print(countSQL)

    # ee.tname='i am cat'
    # ee.tremark='喵'
    # ee.tiid=13579
    # sql,parameters=ee.insertSql()
    # oldData={"tid": 201, "tname": "", "tflag": 0, "trowstatus": 0, "tremark": "",
    #  "tiid": 0, "tsid": 0, "tstartdate":datetime.datetime.strptime("2019-05-16 09:21:25", '%Y-%m-%d %H:%M:%S'), 
    #  "tenddate": datetime.datetime.strptime("2019-05-18 09:21:25", '%Y-%m-%d %H:%M:%S'), "tassignorid": 0, "temployerid": 0, 
    #  "tcreater": "", 
    #  "tcreatetime":  datetime.datetime.strptime("2019-05-19 09:21:25", '%Y-%m-%d %H:%M:%S'), "tupdater": "", 
    #  "tupdatetime":  datetime.datetime.strptime("2019-05-20 09:21:25", '%Y-%m-%d %H:%M:%S'), "tparentid": 0}#this is the data from db  Analog data
    # ee=TaskModel(**oldData)
    # ee.tflag=1
    # ee.tupdatetime=datetime.datetime.now()
    # ee.tcreatetime=None
    # sql,parameters=ee.updateModel()


    sql,parameters=TaskModel() \
    .addShow(TaskModel.tflag==1) \
    .addShow(TaskModel.tupdatetime==datetime.datetime.now()) \
    .addJoin(TaskModel.tupdatetime==datetime.datetime.now()) \
    .addWhere(TaskModel.tid==1) \
    .addWhere(TaskModel.tupdatetime==datetime.datetime.now()) \
    .startBrackets() \
    .addWhere(TaskModel.tiid==2) \
    .addWhere("temployerid>0") \
    .addWhere(("tassignorid","in","1,2")) \
    .addWhere(("tassignorid","in",[1,2])) \
    .addWhere(TaskModel.tremark=='das')\
    .endBracket() \
    .selectSql()
    print(sql)
    print(parameters)
    # print(countsql)
    # print(TestModel.curTime)
    # print (json.dumps(ee))
    # print (TestModel.name)
    # dd=TaskModel(**aa)
    # ee.tid=1
    # ee.tname='123'
    # ee.tflag=1
    # ddee.tcreatetime=datetime.datetime.now()
    # sql,perm=dd.updateModel()
    # print(sql)
    # print(perm)
    # print(len(perm))
    # print (json.dumps(ee,cls=ComplexEncoder))
    # mylist=[{"name":"卞辉","age":18,"size":41}
    # ,{"name":"袁伟","age":2,"size":41}
    # ,{"name":"赵雪峰","age":50,"size":41}
    # ,{"name":"姜坤","age":18,"size":42}
    # ,{"name":"国豪","age":2,"size":41}]
    # a=PYLINQ(mylist).where(lambda x:x['age']>1).skip(4)
    # print(a)
    # # print(ujson.dumps(a,ensure_ascii=False,indent=4))
    # for item in a:
    #     print(ujson.dumps(item,ensure_ascii=False,indent=4))

if __name__ == "__main__":
    mian()

#python setup.py sdist bdist_wheel
#twine upload dist/*
    
