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
            name= str(ID)+ '-' + p.get_pinyin(root.split('/')[-1]) + file.split('.')[-1]
            new_root='home/ftpuser/www/images/clothing/' + p.get_pinyin(root.split('/')[-2])
            if not os.path.exists(new_root):
                os.mkdir(new_root)
            shutil.copy(os.path.join(root,file),os.path.join(new_root,name))
            image_url= 'http://192.168.11.172:8780//images/clothing/' + p.get_pinyin(root.split('/')[-2]) + '/' + name
            driver.session().write_transaction(create_image_url, root.split('/')[-1], image_url)



add_clothing('/home/ftpuser/www/images/add/')
