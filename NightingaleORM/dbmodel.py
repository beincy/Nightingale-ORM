from NightingaleORM.fields import Field

class Model(dict, metaclass=ModelMetaClass):
    def __init__(self, **kw):
        super(Model, self).__init__(**kw)
    # 实现__getattr__与__setattr__方法，可以使引用属性像引用普通字段一样  如self['id']

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value
    # 貌似有点多次一举


class ModelMetaClass(type):
    def __new__(cls, name, bases, attrs):
        if name == "Model":
            return type.__new__(cls, name, bases, attrs)
        dateBaseType=attrs.get('__dbType__', None)#数据库类型
        dateBaseName = attrs.get('__dateBase__', None)#数据库名称
        schemaName = attrs.get('__schema__', None) #如果有schema，schema的名称
        tableName = attrs.get('__table__', None) or name.replace('Model','').lower()#表名称，如果没有默认实体去掉Model
        
        mappings = dict()#属性参照
        fields = []#字段
        primaryKey = None#主键

        for k, v in attrs.items():
            if isinstance(v, Field):
                mappings[k] = v
                if v.primary_key:
                    if primaryKey:
                        raise RuntimeError("Douplicate primary key for field :%s" % primaryKey)
                    primaryKey = k
                else:
                    fields.append(k)
                v=v.default
                
        if not primaryKey:
            raise RuntimeError("Primary key not found")
