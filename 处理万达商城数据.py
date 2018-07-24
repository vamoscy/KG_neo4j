fopen=open('help.csv', 'r')
fcheck=open('sub_class.csv', 'r')
fcheck.readline()
sub_class=[]
for line in fcheck:
    line.strip().split(',')
    sub_class.append(line[0])
fopen.readline()
name=[]
for line in fopen:
    line=line.strip().split(',')
    name.append(line[1])
    
    
    
    
    
    
    
from neo4j.v1 import GraphDatabase
driver = GraphDatabase.driver("bolt://192.168.11.172:7687", auth=("neo4j", "1234"))


def create_brand_name(tx,name,other_name):
    tx.run('MERGE (n:brand{name: $name}) '
           'ON MATCH SET n.other_name= $other_name '
           'ON CREATE SET n.name= $name, n.other_name= $other_name ', name=name, other_name=other_name)
    return None

def create_sub_class(tx,name):
    tx.run('MERGE (:sub_class{name: $name}) ', name=name)
    return None

def create_rel(tx, brand, sub_class):
    tx.run('MATCH (from:brand{name: $brand}),(to:sub_class{name: $sub_class}) '
           'MERGE (from)-[:涉及领域]->(to) ', brand=brand, sub_class=sub_class)

fopen=open('wanda.csv', 'r', encoding='utf-8')
i=0
for line in fopen:
    line=line.strip().split(',')
    driver.session().write_transaction(create_brand_name,line[0],line[1])
    driver.session().write_transaction(create_sub_class,line[2])
    driver.session().write_transaction(create_rel, line[0],line[2])
    i=i+1
    print(i,'brands added')
