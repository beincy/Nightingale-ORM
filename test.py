from NightingaleORM.dbmodel import Model
from NightingaleORM.fields import StringField,IntegerField,DateTimeField,FloatField
import datetime,json


class TestModel(Model):
    id=IntegerField('id',True,0)
    name=StringField('name',False,'')
    curTime=DateTimeField('thetime',False,datetime.datetime.now())
    times=FloatField('times',False,0.5)
    # pass

class big():
    id=1
    name='ispig'


def mian():
    aa={'id':1,'name':"卞辉"}
    ee=TestModel(**aa)
    # print(TestModel.curTime)
    # print (json.dumps(ee))
    # print (TestModel.name)
    print (TestModel.id)
    print (ee.curTime)
    print(json.dumps(ee))

if __name__ == "__main__":
    mian()
    