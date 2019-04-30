from NightingaleORM.fields import Field


def translate(database, schema, table, alias, shows, joins,wheres):
    if database is None or schema is None or table is None:
        raise 'interpreter cannot find the db or table'
    sqlStr = ''
    if shows is None or len(shows):
        raise 'select field can not be empty'
    # select
    sqlStr = '''SELECT'''
    for showfield in shows:
        if isinstance(showfield, Field):
            sqlStr = f'''{sqlStr} {'' if len(alias)<=0 else f'{alias}.'}{showfield.name},'''
    sqlStr.strip(',')

    # from
    schemaStr='' if len(schema)<=0 else f'.{schema}'
    sqlStr = f'''{sqlStr} 
    FROM { database}{schemaStr}.'{table}' {alias}'''

    # join
    if joins is not None or len(joins):
        for joinfield in joins:
            if isinstance(joinfield[0],str):
                sqlStr = f'''{sqlStr} {joinfield[0]}'''
            else:
                joinSchemaStr='' if len(joinfield[0][1].__schema__)<=0 else f'.{joinfield[0][1].__schema__}'
                joinTable=f'''{joinfield[0][1].__dateBase__}{joinSchemaStr}.'{joinfield[0][1].__table__}' '''
                sqlStr = f'''{sqlStr} 
                {joinfield[1]} {joinTable} {joinfield[2]} ON {'' if len(joinfield[2])<=0 else f'{joinfield[2]}.'}{joinfield[0][0].name}{joinfield[0][1]}{'' if len(joinfield[3])<=0 else f'{joinfield[3]}.'}{joinfield[0][2].name}'''
    # where
    if wheres is None or len(wheres)<=0:
        raise 'where fields cannot be empty'
    for whereField in wheres:
        sqlStr = f'''{sqlStr} 
    WHERE { database}{schemaStr}.'{table}' {alias}'''
    