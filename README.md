# Nightingale-ORM
Lightweight python orm for  mysql or postgresql . it is Simple use
## Welcome to the Nightingale-ORM wiki!
A simple and compact ORM tool that only generates SQL and objects
It can generate SQL without relying on any database driver，So you can use it to generate any database SQL you want。
一个简单而紧凑的ORM工具，只生成SQL和对象，它可以在不依赖任何数据库驱动程序的情况下生成SQL，因此您可以使用它生成所需的任何数据库SQL。
### 那么如何使用他：
### Then how to use him:
### 1. 定义数据库的实体
### 1. Define the entity of the database
ORM适合关系型数据库。首先我们需要根据数据库的表定义一个model（class）
ORM is suitable for relational databases. First, we need to define a model based on the tables in the database.
举个例子：
For instance：
```
from NightingaleORM.dbmodel import Model
from NightingaleORM.fields import StringField,IntegerField,DateTimeField,FloatField
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
```
模型的名称是表名称，__dbType__ 是数据库类型，默认是postgres，__dateBase__是数据库名称，__schema__是图名称
modelName is table name ， dbType_ is the database type, default is postgres, _dateBase_ is the database name, _schema_ is the graph name.
然后你需要定义你的数据库字段，第一个参数是你表的列名，第二个是是否是主键，第三个字段是默认值，第四个字段是数据库类型如果有的话
hen you need to define your database field. The first parameter is the column name of your table, the second is whether it is the primary key, the third field is the default value, and the fourth field is the database type, if any.
```
tid=IntegerField('tid',True,0,ddl='bigint')
```
### 如何生成查询sql
### How to Generate Query SQL
```
selectSQL,parameters,countSQL=TaskModel().addShow(TaskModel.tname) \
        .addShow("tenddate") \
        .addWhere(TaskModel.tid==1) \
        .addWhere(TaskModel.tupdatetime==datetime.datetime.now()) \
        .startBrackets() \
        .addWhere(TaskModel.tiid==2) \
        .addWhere("temployerid>0") \
        .addWhere(("tassignorid","in","1,2")) \
        .addWhere(("tassignorid","in",[1,2])) \
        .addWhere(TaskModel.tremark=='das')\
        .endBracket() \
        .selectSql(100)
```
selectSQL：
```
SELECT tenddate 
FROM resource.DataAnnotations."task"   
WHERE 1=1 AND tid = $1 AND tupdatetime = $2 AND (1=1  AND tiid = $3 AND tassignorid IN (1,2) AND tassignorid IN ($4,$5) AND tremark = $6) 
ORDER BY tid 
LIMIT 100
```
parameters：
```
[1, datetime.datetime(2019, 5, 31, 8, 58, 23, 600520), 2, 1, 2, 'das']
```
countSQL
```
SELECT count(1) 
FROM resource.DataAnnotations."task"   
WHERE 1=1 AND tid = $1 AND tupdatetime = $2 AND (1=1  AND tiid = $3 AND tassignorid IN (1,2) AND tassignorid IN ($4,$5) AND tremark = $6) 
```


### 如何生成新增sql
### How to generate insert SQL
```
ee=TaskModel()
ee.tname='i am cat'
ee.tremark='喵'
ee.tiid=13579
sql,parameters=ee.insertSql()
```
sql:
```
INSERT resource.DataAnnotations."task" (tname,tflag,trowstatus,tremark,tiid,tsid,tstartdate,tenddate,tassignorid,temployerid,tcreater,tcreatetime,tupdater,tupdatetime,tparentid) 
VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15)
```
parameters:
```
['i am cat', 0, 0, '喵', 13579, 0, datetime.datetime(2019, 5, 31, 9, 13, 59, 162788), datetime.datetime(2019, 5, 31, 9, 13, 59, 162793), 0, 0, '', datetime.datetime(2019, 5, 31, 9, 13, 59, 162797), '', datetime.datetime(2019, 5, 31, 9, 13, 59, 162800), 0]
```
### 如何生成更新的sql
### How to generate updated SQL
```
oldData={"tid": 201, "tname": "", "tflag": 0, "trowstatus": 0, "tremark": "",
     "tiid": 0, "tsid": 0, "tstartdate": "2019-05-31 09:21:25", 
     "tenddate": "2019-05-31 09:21:25", "tassignorid": 0, "temployerid": 0, 
     "tcreater": "", "tcreatetime": "2019-05-31 09:21:25", "tupdater": "", 
     "tupdatetime": "2019-05-31 09:21:25", "tparentid": 0}#this is the data from db  Analog data
ee=TaskModel(**oldData)
ee.tflag=1
ee.tupdatetime=datetime.datetime.now()
ee.tcreatetime=None
sql,parameters=ee.updateModel()
```
sql：
```
UPDATE resource.DataAnnotations."task" 
SET tname=$0, tflag=$1, trowstatus=$2, tremark=$3, tiid=$4, tsid=$5, tstartdate=$6, tenddate=$7, tassignorid=$8, temployerid=$9, tcreater=$10, tcreatetime=$11, tupdater=$12, tupdatetime=$13, tparentid=$14 
WHERE tid=$16
```
parameters：
```
['', 1, 0, '', 0, 0, datetime.datetime(2019, 5, 16, 9, 21, 25), datetime.datetime(2019, 5, 18, 9, 21, 25), 0, 0, '', datetime.datetime(2019, 5, 31, 10, 17, 9, 142662), '', datetime.datetime(2019, 5, 31, 10, 17, 9, 145357), 0, 201]
```
### 但是我不想依据实体进行更新怎么办
### But I don't want to update by entity.
```
sql,parameters=TaskModel() \
    .addUpdate(TaskModel.tflag==1) \
    .addUpdate(TaskModel.tupdatetime==datetime.datetime.now()) \
    .addWhere(TaskModel.tid==1) \
    .addWhere(TaskModel.tupdatetime==datetime.datetime.now()) \
    .startBrackets() \
    .addWhere(TaskModel.tiid==2) \
    .addWhere("temployerid>0") \
    .addWhere(("tassignorid","in","1,2")) \
    .addWhere(("tassignorid","in",[1,2])) \
    .addWhere(TaskModel.tremark=='das')\
    .endBracket() \
    .updateSql()
```
sql：
```
UPDATE resource.DataAnnotations."task"
SET tflag = $1,tupdatetime = $2
WHERE 1=1 AND tid = $3 AND tupdatetime = $4 AND (1=1  AND tiid = $5 AND tassignorid IN (1,2) AND tassignorid IN ($6,$7) AND tremark = $8)
```
parameters：
```
[1, datetime.datetime(2019, 5, 31, 10, 37, 0, 600446), 1, datetime.datetime(2019, 5, 31, 10, 37, 0, 600453), 2, 1, 2, 'das']
```
