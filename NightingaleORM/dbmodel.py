from NightingaleORM.fields import Field
from NightingaleORM.pgsqlInterpreter import translate


class ModelMetaClass(type):
    def __new__(cls, name, bases, attrs):
        if name == "Model":
            return type.__new__(cls, name, bases, attrs)
        dateBaseType = attrs.get('__dbType__', '')  # 数据库类型
        dateBaseName = attrs.get('__dateBase__', '')  # 数据库名称
        schemaName = attrs.get('__schema__', '')  # 如果有schema，schema的名称
        tableName = attrs.get('__table__', None) or name.replace(
            'Model', '').lower()  # 表名称，如果没有默认实体去掉Model

        mappings = dict()  # 属性参照
        fields = []  # 字段
        primaryKey = None  # 主键

        for k, v in attrs.items():
            if isinstance(v, Field):
                mappings[k] = v
                mappings[k].__dateBase__=dateBaseName
                mappings[k].__schema__=schemaName
                mappings[k].__table__=tableName
                if v.primary_key:
                    if primaryKey:
                        raise RuntimeError(
                            "Douplicate primary key for field :%s" % primaryKey)
                    primaryKey = k
                else:
                    fields.append(k)
        if not primaryKey:
            raise RuntimeError("Primary key not found")
        # for k in mappings:
        #     attrs.pop(k)
        attrs['__mappings__'] = mappings  # 保存属性和列的映射关系
        attrs['__dateBase__'] = dateBaseName  # 保存属性和列的映射关系
        attrs['__schema__'] = schemaName  # 保存属性和列的映射关系
        attrs['__table__'] = tableName  # 保存属性和列的映射关系
        return type.__new__(cls, name, bases, attrs)


class Model(dict, metaclass=ModelMetaClass):
    def __init__(self, **kw):
        super(Model, self).__init__(**kw)
        for k in self.__mappings__:
            field = self.__mappings__[k]
            if isinstance(field, Field):
                if field.name in self:
                    setattr(self, k, self[field.name])
                elif k in self:
                    setattr(self, k, self[k])
                else:
                    setattr(self, k, field.default)

    # 实现__getattr__与__setattr__方法，可以使引用属性像引用普通字段一样  如self['id']

    def __getattr__(self, key):
        try:
            if key not in self.__mappings__:
                raise AttributeError(r"'%s' is not field of db." % key)
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)

    __showFields__=[]
    __orderFields__=[]
    __bracketsWhereFields__={}
    __Joins__=[]
    __alias__=''
    def addShow(self,*args):
        '''
        添加查询的fields
        '''
        self.__showFields__+=args
        return self
    
    
    def addWhere(self,operation,relation='AND',bracketsTag=0):
        '''
        添加where条件
        operation:(fields,operation,value)
        relation:'and' or 'or'
        bracketsTag:same tag add in same brackets
        '''
        if bracketsTag not in self.__bracketsWhereFields__:
            self.__bracketsWhereFields__[bracketsTag]=[operation+(relation.upper())]
        else:
            self.__bracketsWhereFields__[bracketsTag].append(operation+(relation.upper()))
        return self

    def addTableAlias(self,tableAlias):
        self.__alias__=tableAlias
        return self

    def addOrder(self,field):
        '''
        添加排序的的fields，升序
        '''
        self.__orderFields__.append((field,'ASC'))
        return self
    
    def addOrderDesc(self,field):
        '''
        添加排序字段，降序
        '''
        self.__orderFields__.append((field,'DESC'))
        return self


    def addJoin(self,operation,joinType='JOIN',alias1='',alias2=''):
        '''
        添加Join条件
        model1 joinType model2 alias on operation
        '''
        self.__Joins__.append((operation,joinType.upper(),alias1,alias2))
        return self
    def addJoinStr(self,joinStr:str):
        '''
        添加Join条件
        joinStr
        '''
        if not isinstance(joinStr,str): 
            return 'joinStr must be str'
        self.__Joins__.append((joinStr,None,None,None))
        return self

    def GetSelectSql(self)->str:
        pass
    


    
    
