#连接数据库
from neo4j.v1 import GraphDatabase
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "1234"))

#遍历文件夹，提取需要添加的品牌名
import os,shutil
from zhon.hanzi import punctuation
import re
from xpinyin import Pinyin


def get_name(tx):
    name_list = []
    for record in tx.run("MATCH (n:brand) "
                         "RETURN n.name "):
        name_list.append(record["n.name"])
    return name_list

def create_brand_name(tx,name):
    tx.run('create (:brand{name: $name}) ', name=name)
    return None

def get_id(tx,name):
    id_list=[]
    for record in tx.run("match (n:brand{name: $name}) return ID(n), n.name ", name=name):
        id_list.append(record["ID(n)"])
        return id_list

def create_image_url(tx,image_url):
    tx.run('create (:logo{name: '  ', image_url: $image_url}) ', image_url=image_url)
    return None


def rename(file,new_root):
    print(new_root)
    old_path= os.path.join(new_root + file)
    len_new_path=len(os.listdir(new_root))
    new_name=new_root[new_root.index('-')+1:-1] + '-' + str(len_new_path) + '.' + file.split('.')[1]
    new_path=os.path.join(new_root,new_name)
    os.rename(old_path,new_path)
    return new_name

def create_rel(tx,image_url,ID):
    tx.run('match (n1:logo), (n2:brand) '
           'where n1.image_url= $image_url and ID(n2)= toInt($ID) '
           'create (n2)-[r:logo_is]->(n1) ', image_url=image_url, ID=ID)
    return None


def create_node_rel(root,name):
    p=Pinyin()
    ID_old = driver.session().read_transaction(get_id, name)
    driver.session().write_transaction(create_brand_name, name)
    ID_new = driver.session().read_transaction(get_id, name)
    ID=''
    if len(ID_new)==1:
        ID=ID_new[0]
    else:
        for i in ID_new:
            if i not in ID_old:
                ID=i
    new_root = '/home/ftpuser/www/images/logos/' + str(ID) + '-' + p.get_pinyin(name) + '/'
    os.mkdir(new_root)
    for file in os.listdir(root):
        shutil.copy(os.path.join(root,file), os.path.join(new_root, file))
        new_name = rename(file, new_root)
        image_url = 'http://192.168.11.172:8780//images/logos/' + str(ID) + '-' + p.get_pinyin(name) + '/' + new_name
        driver.session().write_transaction(create_image_url, image_url)
        driver.session().write_transaction(create_rel, image_url, ID)


def add_logos(rootdir):
    p=Pinyin()
    name_list=driver.session().read_transaction(get_name)
    list_dirs = os.walk(rootdir)
    existed= []
    for root, dirs, files in os.walk('/home/ftpuser/www/images/logos/'):
        if len(os.listdir(root)) != 0:
            existed.append(root.split('/')[-1])
    for root, dirs, files in list_dirs:
        name = root.split('/')[-1].strip()
        if name != '':
            name= re.sub("[{}]+".format(punctuation), "", name)
            if name in name_list:
                ID = driver.session().read_transaction(get_id, name)
                full_name= str(ID) + '-' + p.get_pinyin(name)
                if full_name in existed:
                    print(name, 'existed')
                    for file in os.listdir(root):
                        in_put=input(file+' add? y/n')
                        if in_put=='y' :
                            driver.session().write_transaction(create_brand_name, name)
                            ID = driver.session().read_transaction(get_id, name)
                            new_root = '/home/ftpuser/www/images/logos/' + str(ID) + '-' + p.get_pinyin(name) + '/'
                            shutil.copy(os.path.join(root,file), os.path.join(new_root, file))
                            new_name = rename(file, new_root)
                            image_url = 'http://192.168.11.172:8780//images/logos/' + str(ID) + '-' + p.get_pinyin(name) + '/' + new_name
                            driver.session().write_transaction(create_image_url, image_url)
                            driver.session().write_transaction(create_rel, image_url, ID)
                else:
                    ID = driver.session().read_transaction(get_id, name)
                    new_root='/home/ftpuser/www/images/logos/' + str(ID) + '-' + p.get_pinyin(name) + '/'
                    os.mkdir(new_root)
                    for file in os.listdir(root):
                        shutil.copy(os.path.join(root, file), os.path.join(new_root, file))
                        new_name = rename(file, new_root)
                        image_url = 'http://192.168.11.172:8780//images/logos/' + str(ID) + '-' + p.get_pinyin(
                            name) + '/' + new_name
                        driver.session().write_transaction(create_image_url, image_url)
                        driver.session().write_transaction(create_rel, image_url, ID)
            else:
                create_node_rel(root,name)

def create_domain(tx,brand, sub_class):
    tx.run('merge (n1:brand), (n2:sub_class) '
           'where n1.name= $brand and n2.name= $sub_class '
           'create (n1)-[r:涉及领域]->(n2) ', brand=brand, sub_class=sub_class)
    return None

def update_domain(file):
    try:
        fopen=open(file)
        fopen.readline()
        for line in fopen:
            line.strip().split(',')
            driver.session().write_transaction(line[0], line[1])
        print('New infomation has been added')
    except:
        print('No domain information updated')

add_logos('/home/ftpuser/www/images/add/')
update_domain('/home/ftpuser/www/images/add/rel.csv')
