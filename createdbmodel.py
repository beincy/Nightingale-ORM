import asyncio
import uvloop
import asyncpg
import io
import sys
import os

DB_CONFIG = {
    'resource': {
        'host': '192.168.88.103',
        'user': 'postgres',
        'password': 'postgres_123',
        'port': '5453',
        'database': 'resource'
    },
}


async def main():
    # y（是）/n（否）
    print("开始生成数据库实体、增删改查便捷方法...\n")
    print("请选择数据库\n")
    dbReflex = {}
    for index, dbConfigItem in enumerate(DB_CONFIG.items()):
        dbReflex[index] = dbConfigItem
        print(f"【{index}】：{dbConfigItem[0]}")
    # print("【999】：其他\n")
    dbBaseNo = int(input(f" 输入数据库编号\n"))
    dbBaseName, dbBaseConfig = dbReflex[dbBaseNo]  # db名称
    print(f"选择数据库【{dbBaseName}】\n")
    connection = await asyncpg.connect(**dbBaseConfig)

    sql = f'''SELECT nspname FROM pg_namespace;'''
    schemasnfo = await connection.fetch(sql)
    schemasReflex = {}
    if schemasnfo and len(schemasnfo) > 0:
        for index, schemasItem in enumerate(schemasnfo):
            schemasReflex[index] = schemasItem['nspname']
            print(f"【{index}】：{schemasItem['nspname']}")
    else:
        print("该数据库没有有效的schemas\n")

    schemasNo = int(input(f" 请选择schemas编号\n"))
    schemasName = schemasReflex[schemasNo]  # schemas名
    print(f"选择schemas【{schemasName}】\n")

    tableReflex = {}
    sql = f'''select tablename from pg_tables where schemaname='{schemasName}';'''
    tableLIstinfo = await connection.fetch(sql)
    if tableLIstinfo and len(tableLIstinfo) > 0:
        for index, tabletem in enumerate(tableLIstinfo):
            tableReflex[index] = tabletem['tablename']
            print(f"【{index}】：{tabletem['tablename']}")
    else:
        print("该数据库没有有效的table\n")

    tableNo = int(input(f" 请选择table编号\n"))
    tableName = tableReflex[tableNo]  # 表明
    print(f"选择table【{tableName}】\n")

    dirPath = f"../app/model/{dbBaseName}"
    print(f"是否输出默认目录{dirPath} \n")
    isCurDir = input(f" y（开始生成）/n（重新输入路径）\n")

    if isCurDir != "y":
        dirPathNew = input(f" 输入新的路径\n")
        dirPath = dirPathNew

    print(f"输入的路径目录{dirPath} \n")

    if not os.path.exists(dirPath):
        print(f"未找到文件夹，是否生成文件夹\n")
        isNeed = input(f" y（是）/n（不必了，我自己创建好了）\n")
        if isNeed == 'y':
            os.makedirs(dirPath)
            print(f"创建成功\n")
    print(f"开始生成...\n")
    sql = f'''
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
    tableInfo = await connection.fetch(sql)
    await connection.close()

    tableNameArray = tableName.split('_')
    ModelName = ""
    if len(tableNameArray) > 1:
        for nameItem in tableNameArray:
            ModelName = ModelName + (nameItem[:1].upper() + nameItem[1:])
    else:
        ModelName = tableName
    ModelName = ModelName[:1].lower() + ModelName[1:]
    projectModelName = f'{dirPath}/{ModelName}Model.py'
    with open(projectModelName, 'w') as f:
        f.write('from NightingaleORM.dbmodel import Model' + '\n')
        f.write(
            'from NightingaleORM.fields import StringField,IntegerField,DateTimeField,FloatField'
            + '\n')
        f.write('import datetime' + '\n')
        f.write('\n')
        ModelName = ModelName[:1].upper() + ModelName[1:]
        f.write(f'class {ModelName}Model(Model):' + '\n')
        f.write(f"    __dbType__='pgsql'" + '\n')
        f.write(f"    __dataBase__='{dbBaseName}'" + '\n')
        f.write(f"    __schema__='{schemasName}'" + '\n')
        f.write(f"    __table__='{tableName}'" + '\n')
        f.write('\n')
        f.write(f"    def __init__(self,**kwargs):" + '\n')
        f.write(f"          super({ModelName}Model,self).__init__(**kwargs)" +
                '\n')
        f.write('\n')
        for item in tableInfo:
            item = dict(item)
            valName = item['name']
            if 'dropped.' in valName:
                continue
            f.write(f"    ")
            valNameArray = valName.split('_')
            if len(valNameArray) > 1:
                valName = ""
                for nameItem in valNameArray:
                    valName = valName + (nameItem[:1].upper() + nameItem[1:])
                valName = valName[:1].lower() + valName[1:]
            f.write(f"{valName}")
            typeStr = ''
            dbType = item['type'].lower()
            if 'int' in dbType:
                typeStr = 'IntegerField'
            elif 'char' in dbType:
                typeStr = 'StringField'
            elif 'timestamp' in dbType:
                typeStr = 'DateTimeField'
            elif 'float' in dbType or 'decimal' in dbType:
                typeStr = 'DateTimeField'
            f.write(f" = {typeStr}('{item['name']}',")
            if 'regclass' in item['default']:
                f.write(f" True, 0")
            else:
                f.write(f" False,")
                defaultArray = item['default'].split("::")
                if 'timestamp' in dbType:
                    if 'createtime' in item['name'] or 'updatetime' in item[
                            'name']:
                        f.write(f" datetime.datetime.now()")
                    else:
                        f.write(
                            f" datetime.datetime.strptime({defaultArray[0]}, '%Y-%m-%d %H:%M:%S')"
                        )
                else:
                    f.write(f" {defaultArray[0]}", )
            f.write(f") # {item['comment']}" + '\n')

        f.write('\n')
        f.write('    """\n')
        f.write('    快捷方法，拷贝用\n')
        f.write('\n')
        f.write('    dal = DAL({ModelName}Model) #初始化\n')
        f.write('    async with dal: #建立链接\n')
        f.write('\n')
        ModelName2 = ModelName[:1].lower() + ModelName[1:]
        f.write(f"    {ModelName2}DAL={ModelName}Model()" + '\n')
        for item in tableInfo:
            item = dict(item)
            valName = item['name']
            if 'dropped.' in valName:
                continue
            # f.write(f"    ")
            valNameArray = valName.split('_')
            if len(valNameArray) > 1:
                valName = ""
                for nameItem in valNameArray:
                    valName = valName + (nameItem[:1].upper() + nameItem[1:])
                valName = valName[:1].lower() + valName[1:]
            f.write(
                f"    {ModelName2}DAL.addShow({ModelName}Model.{valName}) # {item['comment']}"
                + '\n')
        f.write('\n')
        for item in tableInfo:
            item = dict(item)
            valName = item['name']
            if 'dropped.' in valName:
                continue
            # f.write(f"    ")
            valNameArray = valName.split('_')
            if len(valNameArray) > 1:
                valName = ""
                for nameItem in valNameArray:
                    valName = valName + (nameItem[:1].upper() + nameItem[1:])
                valName = valName[:1].lower() + valName[1:]
            f.write(
                f"    {ModelName2}DAL.addWhere({ModelName}Model.{valName}==kwargs['{item['name']}']) # {item['comment']}"
                + '\n')
        f.write('\n')
        for item in tableInfo:
            item = dict(item)
            valName = item['name']
            if 'dropped.' in valName:
                continue
            # f.write(f"    ")
            valNameArray = valName.split('_')
            if len(valNameArray) > 1:
                valName = ""
                for nameItem in valNameArray:
                    valName = valName + (nameItem[:1].upper() + nameItem[1:])
                valName = valName[:1].lower() + valName[1:]
            f.write(
                f"    {ModelName2}DAL.addUpdate({ModelName}Model.{valName}==kwargs['{item['name']}']) # {item['comment']}"
                + '\n')
        f.write('\n')
        f.write(f'    dal.getList({ModelName2}DAL)#查询\n')
        f.write(f'    dal.update({ModelName2}DAL)#更新\n')
        f.write('    """\n')

    print(f"数据库实体{projectModelName}生成完成...\n")
    # =======================================下方是生成快速查询的sql============================================
    print(f"是否继续生成快速查询方法 \n")
    isNeedFastSql = input(f"y（是）/n（否）\n")
    if isNeedFastSql != 'y':
        print("执行完毕")
        return

    dirPathFastSql = f"../app/dataAccess/{dbBaseName}"
    print(f"是否输出默认目录{dirPathFastSql} \n")
    isCurDir = input(f" y（开始生成）/n（重新输入路径）\n")

    if isCurDir != "y":
        dirPathNew = input(f" 输入新的路径\n")
        dirPathFastSql = dirPathNew

    print(f"输入的路径目录{dirPathFastSql} \n")

    if not os.path.exists(dirPathFastSql):
        print(f"未找到文件夹，是否生成文件夹\n")
        isNeed = input(f" y（是）/n（不必了，我自己创建好了）\n")
        if isNeed == 'y':
            os.makedirs(dirPathFastSql)
            print(f"创建成功\n")

    print(f"开始生成...\n")

    projectAccessName = f'{dirPathFastSql}/{ModelName[:1].lower() + ModelName[1:]}Access.py'

    modelNameBefore = ModelName[:1].upper() + ModelName[1:]
    with open(projectAccessName, 'w') as f:
        f.write('from utils import unity' + '\n')
        f.write('from app.dataAccess import DAL' + '\n')
        dirPathww = dirPath.replace('.', "")
        dirPathww = dirPathww.replace('/', ".")
        if len(dirPathww) > 0:
            if dirPathww[len(dirPathww) - 1] != '.':
                dirPathww += '.'
            if dirPathww[0] == '.':
                dirPathww = dirPathww[1:]
        f.write(
            f'from {dirPathww}{ModelName[:1].lower() + ModelName[1:]}Model import {modelNameBefore}Model'
            + '\n')
        f.write('import datetime' + '\n')
        f.write('\n')

        f.write(f'async def add(model:{modelNameBefore}Model):\n')
        f.write(f'  """\n')
        f.write(f'  新增数据\n')
        f.write(f'  """\n')
        f.write(f'  \n')
        f.write(f'  if model is None: \n')
        f.write(f'     return False\n')
        f.write(f'  dal = DAL( {modelNameBefore}Model)  # 初始化\n')
        f.write(f'  async with dal:  # 建立链接\n')
        f.write(f'     return await dal.add(model)\n')

        f.write(f'async def addReturnId(model:{modelNameBefore}Model):\n')
        f.write(f'  """\n')
        f.write(f'  新增数据，并返回主键Id\n')
        f.write(f'  """\n')
        f.write(f'  \n')
        f.write(f'  if model is None: \n')
        f.write(f'     return False\n')
        f.write(f'  dal = DAL( {modelNameBefore}Model)  # 初始化\n')
        f.write(f'  async with dal:  # 建立链接\n')
        f.write(f'     return await dal.addReturnId(model)\n')

        f.write(f'async def getList(**kwargs):\n')
        f.write(f'  """\n')
        f.write(f'  查询数据\n')
        f.write(f'  """\n')
        f.write(f'  model={modelNameBefore}Model()\n')
        for item in tableInfo:
            item = dict(item)
            valName = item['name']
            if 'dropped.' in valName:
                continue
            # f.write(f"    ")
            valNameArray = valName.split('_')
            if len(valNameArray) > 1:
                valName = ""
                for nameItem in valNameArray:
                    valName = valName + (nameItem[:1].upper() + nameItem[1:])
                valName = valName[:1].lower() + valName[1:]
            f.write(
                f"  model.addShow({ModelName}Model.{valName}) # {item['comment']}"
                + '\n')
            f.write('\n')
        f.write('\n')
        for item in tableInfo:
            item = dict(item)
            valName = item['name']
            # realName=valName
            if 'dropped.' in valName:
                continue
            # f.write(f"    ")
            valNameArray = valName.split('_')
            if len(valNameArray) > 1:
                valName = ""
                for nameItem in valNameArray:
                    valName = valName + (nameItem[:1].upper() + nameItem[1:])
                valName = valName[:1].lower() + valName[1:]
            dbType = item['type'].lower()
            if 'int' in dbType or 'float' in dbType or 'decimal' in dbType:
                f.write(f"  if unity.tryGetValueOfInt(kwargs,'{valName}')>0:" +
                        '\n')
                f.write(
                    f"    model.addWhere({ModelName}Model.{valName}==unity.tryGetValueOfInt(kwargs,'{valName}'))# {item['comment']}"
                    + '\n')
            elif 'timestamp' in dbType:
                f.write(f"  if '{valName}' in kwargs:" + '\n')
                f.write(
                    f"    model.addWhere({ModelName}Model.{valName}==kwargs['{valName}'])# {item['comment']}"
                    + '\n')
            else:
                f.write(
                    f"  if unity.isNoneOrEmpty(unity.tryGetValue(kwargs,'{valName}')):"
                    + '\n')
                f.write(
                    f"   model.addWhere({ModelName}Model.{valName}==unity.tryGetValue(kwargs,'{valName}')) # {item['comment']}"
                    + '\n')
            f.write('\n')
        f.write('\n')

        f.write(f' \n')
        f.write(f'  dal = DAL( {modelNameBefore}Model)  # 初始化\n')
        f.write(f'  async with dal:  # 建立链接\n')
        f.write(
            f"     return await dal.getList(model,unity.tryGetValueOfInt(kwargs,'page',0),unity.tryGetValueOfInt(kwargs,'index',0))\n"
        )
        f.write('\n')
        f.write('\n')
        f.write(f'async def update(**kwargs):\n')
        f.write(f'  """\n')
        f.write(f'  新增数据，并返回主键Id\n')
        f.write(f'  """\n')
        f.write(f'  \n')
        f.write(f'  model={modelNameBefore}Model()\n')
        f.write(f'  \n')
        for item in tableInfo:
            item = dict(item)
            valName = item['name']
            # realName=valName
            if 'dropped.' in valName or 'regclass' in item['default']:
                continue
            # f.write(f"    ")
            valNameArray = valName.split('_')
            if len(valNameArray) > 1:
                valName = ""
                for nameItem in valNameArray:
                    valName = valName + (nameItem[:1].upper() + nameItem[1:])
                valName = valName[:1].lower() + valName[1:]
            dbType = item['type'].lower()
            if 'int' in dbType or 'float' in dbType or 'decimal' in dbType:
                f.write(f"  if unity.tryGetValueOfInt(kwargs,'{valName}')>0:" +
                        '\n')
                f.write(
                    f"    model.addUpdate({ModelName}Model.{valName}==unity.tryGetValueOfInt(kwargs,'{valName}') )# {item['comment']}"
                    + '\n')
            elif 'timestamp' in dbType:
                f.write(f"  if '{valName}' in kwargs:" + '\n')
                f.write(
                    f"    model.addUpdate({ModelName}Model.{valName}==kwargs['{valName}'])# {item['comment']}"
                    + '\n')
            else:
                f.write(
                    f"  if unity.isNoneOrEmpty(unity.tryGetValue(kwargs,'{valName}')):"
                    + '\n')
                f.write(
                    f"    model.addUpdate({ModelName}Model.{valName}==unity.tryGetValue(kwargs,'{valName}')) # {item['comment']}"
                    + '\n')
            f.write('\n')

        for item in tableInfo:
            item = dict(item)
            valName = item['name']
            # realName=valName
            if 'dropped.' in valName:
                continue
            # f.write(f"    ")
            valNameArray = valName.split('_')
            if len(valNameArray) > 1:
                valName = ""
                for nameItem in valNameArray:
                    valName = valName + (nameItem[:1].upper() + nameItem[1:])
                valName = valName[:1].lower() + valName[1:]
            if 'regclass' in item['default']:
                f.write(
                    f"  model.addWhere({ModelName}Model.{valName}==unity.tryGetValueOfInt(kwargs,'{valName}')) # {item['comment']}"
                    + '\n')
                break

        f.write('\n')

        f.write(f'  dal = DAL( {modelNameBefore}Model)  # 初始化\n')
        f.write(f'  async with dal:  # 建立链接\n')
        f.write(f'     return  await dal.update(model)\n')

    print(f"数据库快捷sql{projectAccessName}生成完成...\n")


if __name__ == "__main__":
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    asyncio.run(main())
