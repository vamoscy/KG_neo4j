#连接数据库
from neo4j.v1 import GraphDatabase
driver = GraphDatabase.driver("bolt://localhost:7688", auth=("neo4j", "1234"))

#遍历文件夹，提取需要添加的品牌名
import os,shutil
from xpinyin import Pinyin

def get_id(tx,name):
    for record in tx.run("MATCH (n:细节{name: $name}) RETURN ID(n) ", name=name):
        ID= record["ID(n)"]
        return ID

def create_image_url(tx, name, image_url):
    tx.run("MERGE (n:细节{name: $name}) "
           "ON MATCH SET n.image_url= $image_url ", name=name, image_url=image_url)
    return None

def add_clothing(rootdir):
    p=Pinyin()
    list_dirs = os.walk(rootdir)
    for root, dirs, files in list_dirs:
        for file in files:
            ID = driver.session().read_transaction(get_id, root.split('/')[-1])
            name= str(ID)+ '-' + p.get_pinyin(root.split('/')[-1]) + '.' + file.split('.')[-1]
            new_root='home/ftpuser/www/images/clothing/' + p.get_pinyin(root.split('/')[-2])
            if not os.path.exists(new_root):
                os.mkdir(new_root)
                print('done')
            shutil.copy(os.path.join(root,file),os.path.join(new_root,name))
            image_url= 'http://192.168.11.172:8780//images/clothing/' + p.get_pinyin(root.split('/')[-2]) + '/' + name
            driver.session().write_transaction(create_image_url, root.split('/')[-1], image_url)

def create_clothes_type(tx, clothes_type):
    tx.run("MERGE (n:服饰名称{name: $clothes_type}) ", clothes_type=clothes_type)
    return None

def create_subclass(tx, sub_class):
    tx.run("MERGE (n:细分类{name: $sub_class}) ", sub_class=sub_class)
    return None

def create_detail(tx, detail):
    tx.run("MERGE (n:细节{name: $detail}) ", detail=detail)
    return None

def create_rel(tx, start, end):
    tx.run("MATCH (from:细分类{name: $start}),(to:服饰名称{name: $end}) "
           "MERGE (from)-[:适用于]->(to) ", start=start, end=end)
    return None

def create_rel1(tx, start, end):
    tx.run("MATCH (from:细节{name: $start}),(to:细分类{name: $end}) "
           "MERGE (from)-[:属于]->(to) ", start=start, end=end)
    return None

def create_rel2(tx, start, end):
    tx.run("MATCH (from:服饰名称{name: $start}),(to:大类{name: $end}) "
           "MERGE (from)-[:见于]->(to) ", start=start, end=end)
    return None

def add_node(rootdir):
    list_dirs=os.walk(rootdir)
    for root, dirs, files in list_dirs:
        for file in files:
            clothes_type= file[:-4]
            driver.session().write_transaction(create_clothes_type, clothes_type)
            driver.session().write_transaction(create_rel2, clothes_type, '女装')
            fopen=open(os.path.join(root,file), 'r')
            for line in fopen:
                line=line.strip().split(',')
                if line[0] != '品牌':
                    driver.session().write_transaction(create_subclass, line[0])
                    driver.session().write_transaction(create_rel, line[0], clothes_type)
                    if line[1] != '其它' and line[1] != '其他':
                        driver.session().write_transaction(create_detail, line[1])
                        driver.session().write_transaction(create_rel1, line[1], line[0])



add_node('/home/ftpuser/www/images/add/')
#add_clothing('/home/ftpuser/www/images/add/')
