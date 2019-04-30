
class Field:
    def __init__(self, name, column_type, primary_key, default):
        self.name = name  # 字段名
        self.column_type = column_type  # 字段数据类型
        self.primary_key = primary_key  # 是否是主键
        self.default = default  # 有无默认值

    def __str__(self):
        return '<%s:%s>' % (self.__class__.__name__, self.name)
    
    def __lt__(self,rhs):
        return (self,'<',rhs)
    def __le__(self,rhs):
        return (self,'<=',rhs)
    def __gt__(self,rhs):
        return (self,'>',rhs)
    def __ge__(self,rhs):
        return (self,'>=',rhs)
    def __eq__(self,rhs):
        return (self,'=',rhs)
    def __ne__(self,rhs):
        return (self,'!=',rhs)


class StringField(Field):
    def __init__(self, name=None, primary_key=False, default=None, ddl='varchar(128)'):
        super(StringField, self).__init__(name, ddl, primary_key, default)
class IntegerField(Field):
    def __init__(self, name=None, primary_key=False, default=None, ddl='bigint'):
        super(IntegerField, self).__init__(name, ddl, primary_key, default)
class FloatField(Field):
    def __init__(self, name=None, primary_key=False, default=None, ddl='float'):
        super(FloatField, self).__init__(name, ddl, primary_key, default)
class DateTimeField(Field):
    def __init__(self, name=None, primary_key=False, default=None, ddl='datetime)'):
        super(DateTimeField, self).__init__(name, ddl, primary_key, default)