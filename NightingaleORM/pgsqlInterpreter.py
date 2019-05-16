from NightingaleORM.fields import Field
import json

def translateSelect(database, schema, table,alias, shows, joins,wheres,brackets,orders,pk,count=1,offset=0):
    if database is None or schema is None or table is None:
        raise 'interpreter cannot find the db or table'
    sqlStr = ''
    parameters=[]
    if shows is None or len(shows)<=0:
        raise 'select field can not be empty'
    # select
    sqlStrTop = f'''SELECT {translateShow(alias,shows)}'''
    sqlStrCountTop='SELECT count(1)'
    # from
    schemaStr='' if len(schema)<=0 else f'.{schema}'
    sqlStr = f'''{sqlStr} 
FROM { database}{schemaStr}."{table}" {alias}'''

    # join
    sqlStr = f'''{sqlStr} {translateJoin(joins,parameters)}'''
    # where
    if (wheres is None or len(wheres)<=0) and (brackets is None or len(brackets)<=0):
        raise 'where fields cannot be empty'

    sqlStr = f'''{sqlStr} 
WHERE 1=1 {translateWhere(alias,wheres,parameters)}'''
    
    for bracketItem in brackets:
        sqlStr = f'''{sqlStr} {bracketItem.relation} ({translateWhere(alias,bracketItem.whereList,parameters)})'''
    # order
    sqlStr = f'''{sqlStr} {translateOrder(orders,pk)}'''
    #countsql
    sqlStrCountTop=f'''{sqlStrCountTop}{sqlStr}'''
    # limit
    sqlStr = f'''{sqlStr} 
LIMIT {count} OFFSET {offset}'''
    return (sqlStrTop+sqlStr,parameters,sqlStrCountTop)

#添加where条件
def translateWhere(alias,wheres,parameters):
        sqlStr=''
        for whereField in wheres:
            if isinstance(whereField,str):
                sqlStr = f'''{sqlStr} {whereField}'''
            else:
                sqlStr = f'''{sqlStr} {whereField.relation} {'' if len(alias)<=0 else f'{alias}.'}{whereField.fields if isinstance(whereField.fields,str) else whereField.fields.name}'''
                if whereField.operation=='IN' or  whereField.operation=='NOT IN':
                    if isinstance(whereField.value,list):
                        sqlStr=f'''{sqlStr} {whereField.operation} ('''
                        for whereItem in whereField.value:
                            parameters.append(whereItem)
                            sqlStr=f'''{sqlStr}${len(parameters)},'''
                        sqlStr=sqlStr.strip(',')
                        sqlStr=f'''{sqlStr})'''
                    else:
                        sqlStr=f'''{sqlStr} {whereField.operation} ({whereField.value})'''
                elif  whereField.operation=='LEFT LIKE':
                    parameters.append(f'%{whereField.value}')
                    sqlStr=f'''{sqlStr} LIKE $%{len(parameters)}'''
                elif  whereField.operation=='RIGHT LIKE':
                    parameters.append(f'{whereField.value}%')
                    sqlStr=f'''{sqlStr} LIKE ${len(parameters)}'''
                elif  whereField.operation=='RIGHT LIKE':
                    parameters.append(f'%{whereField.value}%')
                    sqlStr=f'''{sqlStr} LIKE ${len(parameters)}'''
                else:
                    parameters.append( whereField.value)
                    sqlStr=f'''{sqlStr} {whereField.operation} ${len(parameters)}'''
        return sqlStr

def translateShow(alias,shows):
    sqlStr=''
    for showfield in shows:
        sqlStr = f'''{'' if len(alias)<=0 else f'{alias}.'}{ showfield.name if isinstance(showfield, Field) else showfield},'''
    sqlStr=sqlStr.strip(',')    
    return  sqlStr      

def translateJoin(joins,parameters):
    sqlStr=''
    if joins is not None and len(joins)>0:
        sqlStr=f'''
        '''
        for joinfield in joins:
            if isinstance(joinfield,str):
                sqlStr = f'''{joinfield[0]}'''
            else:
                onList=joinfield.onList
                if onList>0:
                    joinSchemaStr='' if len(onList[0].__schema__)<=0 else f'.{onList[0].__schema__}'
                    joinTable=f'''{onList[0].__dateBase__}{joinSchemaStr}.'{onList[0].__table__}' '''
                    sqlStr = f'''{sqlStr} 
                    {joinfield.joinType} {joinTable} ON 1=1'''
                    for eachOn in onList:
                        if isinstance(eachOn,str):
                            sqlStr=f'''{sqlStr} {eachOn}'''
                        else:
                            if isinstance(eachOn.value,str):
                                parameters.append(eachOn.value)
                            else:
                                sqlStr=f'''{sqlStr} {eachOn.relation} {eachOn.fields.name} {eachOn.operation} {f'${len(parameters)}' if isinstance(eachOn.value,str) else eachOn.value.name}'''        
    return sqlStr             
                        
def translateOrder(orders,pk):
    sqlStr=''                 
    if orders and len(orders)>0:
        sqlStr = f'''
ORDER BY
        '''
        for order in orders:
            if isinstance(order,str):
                sqlStr = f'''{sqlStr} {order}'''
            else:
                sqlStr = f'''{sqlStr} {order.field.name} {order.orderType},'''
        sqlStr=sqlStr.strip(',')
    else:
        sqlStr = f'''
ORDER BY {pk}'''
    return  sqlStr      

def translateInsert()
                    
                    

            