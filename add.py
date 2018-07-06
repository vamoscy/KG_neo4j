#连接服务器并远程操作
'''
import json
import paramiko


def connect(host):
    'this is use the paramiko connect the host,return conn'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        #        ssh.connect(host,username='root',allow_agent=True,look_for_keys=True)
        ssh.connect(host, username='', password='', allow_agent=True)
        return ssh
    except:
        return None


def command(args, outpath):
    'this is get the command the args to return the command'
    cmd = '%s %s' % (outpath, args)
    return cmd


def exec_commands(conn, cmd):
    'this is use the conn to excute the cmd and return the results of excute the command'
    stdin, stdout, stderr = conn.exec_command(cmd)
    results = stdout.read()
    return results


def excutor(host, outpath, args):
    conn = connect(host)
    if not conn:
        return [host, None]
    # exec_commands(conn,'chmod +x %s' % outpath)
    cmd = command(args, outpath)
    result = exec_commands(conn, cmd)
    result = json.dumps(result)
    return [host, result]


def copy_module(conn, inpath, outpath):
    'this is copy the module to the remote server'
    ftp = conn.open_sftp()
    ftp.put(inpath, outpath)
    ftp.close()
    return outpath


if __name__ == '__main__':
    print
    json.dumps(excutor('192.168.1.165', 'ls', ' -l'), indent=4, sort_keys=True)
    print
    copy_module(connect('192.168.1.165'), 'kel.txt', '/root/kel.1.txt')
    exec_commands(connect('192.168.1.165'), 'chmod +x %s' % '/root/kel.1.txt')
'''

#连接数据库
from neo4j.v1 import GraphDatabase
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "1234"))

#遍历文件夹，提取需要添加的品牌名
import os,shutil
from zhon.hanzi import punctuation
import re
from xpinyin import Pinyin
from PIL import Image


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
    tx.run('create (:pic{name:'  ', image_url: $image_url}) ', image_url=image_url)
    return None

def resize(file, ID, name, new_root, mwidth=40, mheight=40):
    p=Pinyin()
    image_path='/home/ftpuser/www/images/logos/' + str(ID) + '-' + p.get_pinyin(name) + '/' + file
    new_path=new_root + file
    with Image.open(image_path) as img:
        w, h = img.size
        if w <= mwidth and h <= mheight:
            print(file, 'is OK.')
        if (1.0 * w / mwidth) > (1.0 * h / mheight):
            if file.endswith('jpg') | file.endswith('jpeg') | file.endswith('JPG'):
                try:
                    scale = 1.0 * w / mwidth
                    resized = img.resize((int(w / scale), int(h / scale)), Image.ANTIALIAS)
                    resized.save(new_path, format="jpeg")
                    print(file, ' successful')
                except:
                    print(image_path,'cannot be resized')
            elif file.endswith('png') | file.endswith('PNG'):
                try:
                    scale = 1.0 * w / mwidth
                    resized = img.resize((int(w / scale), int(h / scale)), Image.ANTIALIAS)
                    resized.save(new_path, format="png")
                    print(file, ' successful')
                except:
                    print(file,'cannot be resized')
            else:
                    print(file, 'cannot be resized')
        else:
            if file.endswith('jpg') | file.endswith('jpeg') | file.endswith('JPG'):
                try:
                    scale = 1.0 * h / mheight
                    resized = img.resize((int(w / scale), int(h / scale)), Image.ANTIALIAS)
                    resized.save(new_path, format="jpeg")
                    print(file, ' successful')
                except:
                    print(file,'cannot be resized')
            elif file.endswith('png') | file.endswith('PNG'):
                try:
                    scale = 1.0 * h / mheight
                    resized = img.resize((int(w / scale), int(h / scale)), Image.ANTIALIAS)
                    resized.save(new_path, format="png")
                    print(file, ' successful')
                except:
                    print(file,'cannot be resized')
            else:
                print(file, 'cannot be resized')

def rename(file,new_root):
    print(new_root)
    old_path= os.path.join(new_root + file)
    len_new_path=len(os.listdir(new_root))
    new_name=new_root[new_root.index('-')+1:-1] + '-' + str(len_new_path) + '.' + file.split('.')[1]
    new_path=os.path.join(new_root,new_name)
    os.rename(old_path,new_path)
    return new_name

def create_rel(tx,image_url,ID):
    tx.run('match (n1:pic), (n2:brand) '
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
    for file in os.listdir(new_root):
        resize(file, ID, name, new_root)
        new_name = rename(file, new_root)
        image_url = 'http://192.168.11.172:8780//images/logos/' + str(ID) + '-' + p.get_pinyin(name) + '/' + new_name
        driver.session().write_transaction(create_image_url, image_url)
        driver.session().write_transaction(create_rel, image_url, ID)

def add_logos(rootdir):
    p=Pinyin()
    name_list=driver.session().read_transaction(get_name)
    list_dirs = os.walk(rootdir)
    for root, dirs, files in list_dirs:
        name = root.split('/')[-1].strip()
        if name != '':
            name= re.sub("[{}]+".format(punctuation), "", name)
            if name in name_list:
                print(name, 'existed')
                new_brand_question=input('create new brand with same name? y/n')
                if new_brand_question=='y' :
                    create_node_rel(root, name)
                elif new_brand_question=='n':
                    for file in os.listdir(root):
                        in_put=input(file+' add? y/n')
                        if in_put=='y' :
                            driver.session().write_transaction(create_brand_name, name)
                            ID = driver.session().read_transaction(get_id, name)
                            new_root = '/home/ftpuser/www/images/logos/' + str(ID) + '-' + p.get_pinyin(name) + '/'
                            shutil.copy(os.path.join(root,file), os.path.join(new_root, file))
                            resize(file, ID, name, new_root)
                            new_name = rename(file, new_root)
                            image_url = 'http://192.168.11.172:8780//images/logos/' + str(ID) + '-' + p.get_pinyin(name) + '/' + new_name
                            driver.session().write_transaction(create_image_url, image_url)
                            driver.session().write_transaction(create_rel, image_url, ID)
            else:
                create_node_rel(root,name)

add_logos('/home/ftpuser/www/images/add/')
