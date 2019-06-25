import asyncio
import uvloop
import asyncpg
import io

DB_CONFIG = {
   'resource': { 'host': '192.168.88.103',
    'user': 'postgres',
    'password': 'postgres_123',
    'port': '5453',
    'database': 'resource'
    },
}

async def main():
    tableName="wordclass"
    connection = await asyncpg.connect(**DB_CONFIG['resource'])
    sql=f'''
    SELECT col_description(a.attrelid,a.attnum) as comment,format_type(a.atttypid,a.atttypmod) as type
     ,a.attname as name, a.attnotnull as notnull,d.adsrc as default
     , (case when a.attlen > 0 then a.attlen else a.atttypmod - 4 end) as length
FROM pg_class as c,pg_attribute as a
left join (select a.attname, ad.adsrc
                  from pg_class c,
                       pg_attribute a,
                       pg_attrdef ad
                  where relname = '{tableName}'
                    and ad.adrelid = c.oid
                    and adnum = a.attnum
                    and attrelid = c.oid) as d on a.attname = d.attname
where c.relname = '{tableName}' and a.attrelid = c.oid and a.attnum>0;
    '''
    tableInfo=await connection.fetch(sql)
    await connection.close()

    tableNameArray=tableName.split('_')
    ModelName=""
    if len(tableNameArray)>1:
        for nameItem in tableNameArray:
            ModelName=ModelName+(nameItem[:1].upper() + nameItem[1:])
    else:
        ModelName=tableName
    ModelName=ModelName[:1].lower() + ModelName[1:]
    with open(f'../app/model/{ModelName}Model.py', 'w') as f:
        f.write('from NightingaleORM.dbmodel import Model'+'\n')
        f.write('from NightingaleORM.fields import StringField,IntegerField,DateTimeField,FloatField'+'\n')
        f.write('import datetime'+'\n')
        f.write('\n')
        ModelName=ModelName[:1].upper() + ModelName[1:]
        f.write(f'class {ModelName}Model(Model):'+'\n')
        f.write(f"    __dbType__='pgsql'"+'\n')
        f.write(f"    __dateBase__='resource'"+'\n')
        f.write(f"    __schema__='DataAnnotations'"+'\n')
        f.write(f"    __table__='{tableName}'"+'\n')
        f.write('\n')
        f.write(f"    def __init__(self,**kwargs):"+'\n')
        f.write(f"          super({ModelName}Model,self).__init__(**kwargs)"+'\n')
        f.write('\n')
        for item in tableInfo:
            item=dict(item)
            valName=item['name']
            if 'dropped.' in valName:
                continue
            f.write(f"    ")
            valNameArray=valName.split('_')
            if len(valNameArray)>1:
                valName=""
                for nameItem in valNameArray:
                    valName=valName+(nameItem[:1].upper() + nameItem[1:])
                valName=valName[:1].lower() + valName[1:]
            f.write(f"{valName}")
            typeStr=''
            dbType=item['type'].lower()
            if 'int' in dbType:
                typeStr='IntegerField'
            elif 'char' in dbType:
                typeStr='StringField'
            elif 'timestamp' in dbType:
                typeStr='DateTimeField'
            elif 'float' in dbType or 'decimal'in dbType:
                typeStr='DateTimeField'
            f.write(f" = {typeStr}('{item['name']}',")
            if 'regclass' in item['default']:
                f.write(f" True, 0")
            else:
                f.write(f" False,")
                defaultArray=item['default'].split("::")
                if 'timestamp' in dbType:
                    if 'createtime' in item['name'] or 'updatetime' in item['name']:
                        f.write(f" datetime.datetime.now()")
                    else:
                        f.write(f" datetime.datetime.strptime({defaultArray[0]}, '%Y-%m-%d %H:%M:%S')")
                else:
                    f.write(f" {defaultArray[0]}",)
            f.write(')'+'\n')

        f.write('\n')
        f.write('    """\n')
        f.write('    快捷方法，拷贝用\n')
        f.write('\n')
        f.write('    dal = DAL({ModelName}Model) #初始化\n')
        f.write('    async with dal: #建立链接\n')  
        f.write('\n')
        ModelName2=ModelName[:1].lower() + ModelName[1:]
        f.write(f"    {ModelName2}DAL={ModelName}Model()"+'\n')
        for item in tableInfo:
            item=dict(item)
            valName=item['name']
            if 'dropped.' in valName:
                continue
            # f.write(f"    ")
            valNameArray=valName.split('_')
            if len(valNameArray)>1:
                valName=""
                for nameItem in valNameArray:
                    valName=valName+(nameItem[:1].upper() + nameItem[1:])
                valName=valName[:1].lower() + valName[1:]
            f.write(f"    {ModelName2}DAL.addShow({ModelName}Model.{valName})"+'\n')
        f.write('\n')
        for item in tableInfo:
            item=dict(item)
            valName=item['name']
            if 'dropped.' in valName:
                continue
            # f.write(f"    ")
            valNameArray=valName.split('_')
            if len(valNameArray)>1:
                valName=""
                for nameItem in valNameArray:
                    valName=valName+(nameItem[:1].upper() + nameItem[1:])
                valName=valName[:1].lower() + valName[1:]
            f.write(f"    {ModelName2}DAL.addWhere({ModelName}Model.{valName}==kwargs['{item['name']}'])"+'\n')
        f.write('\n')
        for item in tableInfo:
            item=dict(item)
            valName=item['name']
            if 'dropped.' in valName:
                continue
            # f.write(f"    ")
            valNameArray=valName.split('_')
            if len(valNameArray)>1:
                valName=""
                for nameItem in valNameArray:
                    valName=valName+(nameItem[:1].upper() + nameItem[1:])
                valName=valName[:1].lower() + valName[1:]
            f.write(f"    {ModelName2}DAL.addUpdate({ModelName}Model.{valName}==kwargs['{item['name']}'])"+'\n')
        f.write('\n')
        f.write(f'    dal.getList({ModelName2}DAL)#查询\n')
        f.write(f'    dal.update({ModelName2}DAL)#更新\n')
        f.write('    """\n')

            
            
        


if __name__ == "__main__":
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    asyncio.run(main())