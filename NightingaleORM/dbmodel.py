from NightingaleORM.fields import Field


class ModelMetaClass(type):
    def __new__(cls, name, bases, attrs):
        if name == "Model":
            return type.__new__(cls, name, bases, attrs)
        dateBaseType = attrs.get('__dbType__', '')  # 数据库类型
        dataBaseName = attrs.get('__dataBase__') or attrs.get(
            '__dateBase__', '')  # 数据库名称
        schemaName = attrs.get('__schema__', '')  # 如果有schema，schema的名称
        tableName = attrs.get('__table__', None) or name.replace(
            'Model', '').lower()  # 表名称，如果没有默认实体去掉Model

        mappings = dict()  # 属性参照
        fields = []  # 字段
        primaryKey = None  # 主键

        for k, v in attrs.items():
            if isinstance(v, Field):
                mappings[k] = v
                mappings[k].__dataBase__ = dataBaseName
                mappings[k].__schema__ = schemaName
                mappings[k].__table__ = tableName
                if v.primary_key:
                    if primaryKey:
                        raise RuntimeError(
                            "Douplicate primary key for field :%s" %
                            primaryKey)
                    primaryKey = k
                else:
                    fields.append(k)
        if not primaryKey:
            raise RuntimeError("Primary key not found")
        # for k in mappings:
        #     attrs.pop(k)
        attrs['__mappings__'] = mappings  # 保存属性和列的映射关系
        attrs['__dateBase__'] = dataBaseName  # 保存db name
        attrs['__dataBase__'] = dataBaseName  # 保存db name
        attrs['__schema__'] = schemaName  # 保存schema
        attrs['__table__'] = tableName  # 保存table name
        attrs['__dbType__'] = dateBaseType  # 保存数据库类型
        attrs['__pk__'] = mappings[primaryKey]  # 保存数据库类型
        return type.__new__(cls, name, bases, attrs)


class BracketModel:
    '''
    括号整体类，括号的条件会关联在一起
    '''

    # whereList=[]
    # relation='AND'
    def __init__(self, model, relation):
        self.whereList = []
        self.relation = 'AND'
        self.orginModel = model
        self.BracketModel = relation

    def addWhere(self, operation, relation='AND'):
        '''
        添加where条件
        operation:class ConditionModel or tuple like ('id','>',1)
        relation:'and' or 'or'
        '''
        if isinstance(operation, ConditionModel):
            operation.relation = relation
            self.whereList.append(operation)
        elif isinstance(operation, tuple) and len(operation) == 3:
            con = ConditionModel(*operation)
            con.relation = relation
            self.whereList.append(con)
        return self

    def endBracket(self):
        self.orginModel.addBracketsWhere(self)
        return self.orginModel


class ConditionModel:
    # fields='' #字段
    # operation='=' #操作符
    # value='' #值
    # _relation='' #与前一个条件的关系

    def __init__(self, fields, operation, value):
        self.fields = ''  # 字段
        self.operation = '='  # 操作符
        self.value = ''  # 值
        self._relation = ''  # 与前一个条件的关系
        self.fields, self.operation, self.value = fields, operation.upper(
        ), value

    @property
    def relation(self):
        return self._relation

    @relation.setter
    def relation(self, value):
        if isinstance(value, str):
            self._relation = value.upper()


class JoinConditionModel():
    # joinType=''#the type of  join
    # onList=[] # the condition affter on
    def __init__(self, joinType):
        self.joinType = ''  # the type of  join
        self.onList = []  # the condition affter on
        self.joinType = joinType.upper()

    def addOn(self, condition, relation):
        condition.relation = relation
        self.onList.append(condition)


class OrderMOdel:
    # field=''
    # orderType='ASC'
    def __init__(self, field, orderType):
        self.field = ''
        self.orderType = 'ASC'
        self.field, self.orderType = field, orderType


class Model(dict, metaclass=ModelMetaClass):
    def __init__(self, **kw):
        self.__showFields__ = []
        self.__orderFields__ = []
        self.__whereFields__ = []
        self.__updateFields__ = []
        self.__groupByFields__ = []
        self.__bracketsWhereFields__ = []
        self.__Joins__ = []
        self.__alias__ = ''
        self._interpreter = None  # sql翻译器
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

    def __getattribute__(self, key):
        try:
            if key in object.__getattribute__(self, '__mappings__'):
                return self[key]
            return object.__getattribute__(self, key)
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        if key in self.__mappings__:
            self[key] = Field.fieldTest(self.__mappings__[key], value)
        elif key.find("_") == 0:
            self.__dict__[key] = value

    def addBracketsWhere(self, bracket: BracketModel):
        '''
        bracket:BracketModel
        '''
        if isinstance(bracket, BracketModel) and len(bracket.whereList) > 0:
            self.__bracketsWhereFields__.append(bracket)

    def addShow(self, *args):
        '''
        添加查询的fields
        '''
        self.__showFields__ += args
        return self

    def startBrackets(self, relation='AND'):
        '''
        开始括号 开始括号
        relation:
        '''
        return BracketModel(self, relation)

    def addWhere(self, operation, relation='AND'):
        '''
        添加where条件
        operation:class ConditionModel or tuple like ('id','>',1) or string
        relation:'and' or 'or'
        '''
        if isinstance(operation, ConditionModel):
            operation.relation = relation
            self.__whereFields__.append(operation)
        elif isinstance(operation, tuple) and len(operation) == 3:
            con = ConditionModel(*operation)
            con.relation = relation
            self.__whereFields__.append(con)
        elif isinstance(operation, str):
            self.__whereFields__.append(operation)
        return self

    def addTableAlias(self, tableAlias):
        self.__alias__ = tableAlias
        return self

    def addOrder(self, field):
        '''
        添加排序的的fields，升序
        '''
        self.__orderFields__.append(OrderMOdel(field, 'ASC'))
        return self

    def addGroupBy(self, field):
        """
        添加分组字段
        """
        self.__groupByFields__.append(field)
        return self

    def addOrderDesc(self, field):
        '''
        添加排序字段，降序
        '''
        self.__orderFields__.append(OrderMOdel(field, 'DESC'))
        return self

    def addJoin(self, *operation, joinType='JOIN'):
        '''
        添加Join条件
        model1 joinType model2 alias on operation
        '''
        join = JoinConditionModel(joinType)
        for item in operation:
            if isinstance(item, tuple):
                join.addOn(item[0], item[1])
            else:
                join.addOn(item, 'AND')

        self.__Joins__.append(join)
        return self

    def addJoinStr(self, joinStr: str):
        '''
        添加Join条件
        joinStr
        '''
        if isinstance(joinStr, str):
            self.__Joins__.append(joinStr)
        return self

    def addUpdate(self, setCollection):
        '''
        添加Update条件
        set:the ConditionModel  .only equal  valid
        '''
        if isinstance(setCollection, ConditionModel):
            self.__updateFields__.append(setCollection)
        elif isinstance(setCollection, tuple) and len(setCollection) == 3:
            con = ConditionModel(*setCollection)
            self.__updateFields__.append(con)
        elif isinstance(setCollection, str):
            self.__updateFields__.append(setCollection)
        return self

    def loadInterpreter(self, customModule):
        '''
        添加翻译其，默认自动识别，可手动传入，进行覆盖。不传递则自动识别
        add Interpreter ，default,pgsql
        '''
        self._interpreter = customModule

    def selectSql(self, count=0) -> str:
        item = ()
        myInterpreter = None
        if self._interpreter:
            myInterpreter = self._interpreter
        elif self.__dbType__.lower() == 'pgsql':
            import NightingaleORM.pgsqlInterpreter as mpgsql
            myInterpreter = mpgsql
        item = myInterpreter.translateSelect(
            self.__dataBase__, self.__schema__, self.__table__, self.__alias__,
            self.__showFields__, self.__Joins__, self.__whereFields__,
            self.__bracketsWhereFields__, self.__orderFields__,
            self.__groupByFields__, self.__pk__, count, 0)
        return item

    def pageOfList(self, index, pageSize):
        '''
        index:the index of pages
        pageSize:the size of each page
        '''
        myInterpreter = None
        if self._interpreter:
            # 这里是获取实际的值
            myInterpreter = self._interpreter
        elif self.__dbType__.lower() == 'pgsql':
            import NightingaleORM.pgsqlInterpreter as mpgsql
            myInterpreter = mpgsql
        # 这里是获取实际的值
        item = myInterpreter.translateSelect(
            self.__dataBase__, self.__schema__, self.__table__, self.__alias__,
            self.__showFields__, self.__Joins__, self.__whereFields__,
            self.__bracketsWhereFields__, self.__orderFields__,
            self.__groupByFields__, self.__pk__, pageSize,
            (index - 1) * pageSize)
        # 这里是获取总数的sql

        return item

    def insertSql(self):
        '''
        获取新增的的sql
        '''
        myInterpreter = None
        if self._interpreter:
            myInterpreter = self._interpreter
        elif self.__dbType__.lower() == 'pgsql':
            import NightingaleORM.pgsqlInterpreter as mpgsql
            myInterpreter = mpgsql

        item = myInterpreter.translateInsert(self.__dataBase__,
                                             self.__schema__, self.__table__,
                                             self.__mappings__, self)
        return item

    def updateModel(self):
        '''
        获取新增的的sql
        '''
        myInterpreter = None
        if self._interpreter:
            myInterpreter = self._interpreter
        elif self.__dbType__.lower() == 'pgsql':
            import NightingaleORM.pgsqlInterpreter as mpgsql
            myInterpreter = mpgsql
        item = myInterpreter.translateUpdateModel(self.__dataBase__,
                                                  self.__schema__,
                                                  self.__table__,
                                                  self.__mappings__, self)
        return item

    def updateSql(self):
        item = ()
        myInterpreter = None
        if self._interpreter:
            myInterpreter = self._interpreter
        elif self.__dbType__.lower() == 'pgsql':
            import NightingaleORM.pgsqlInterpreter as mpgsql
            myInterpreter = mpgsql
        item = myInterpreter.translateUpdate(self.__dataBase__,
                                             self.__schema__, self.__table__,
                                             self.__updateFields__,
                                             self.__whereFields__,
                                             self.__bracketsWhereFields__)
        return item


def useTransaction(*sqls, interpreter=None):
    """
    使用事务
    sqls:sql的集合
    interpreter:执行的方法
    """
    if interpreter is None:
        import NightingaleORM.pgsqlInterpreter as interpreter
    return interpreter.translateTransaction(*sqls)
