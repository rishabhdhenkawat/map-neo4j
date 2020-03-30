import json
from py2neo import Graph

db = Graph('http://45.55.182.50:7474/')

db.run("CREATE INDEX ON :Business(id)")
db.run("CREATE INDEX ON :Category(name)")


create_business_query = '''
// MERGE ON categories
MERGE (b:Business {id: {business_id}})
ON CREATE SET b.name = {name}, 
	b.latitude = {latitude}, 
	b.longitude = {longitude},
	b.stars = {stars}, 
	b.review_count = {review_count}
WITH b
UNWIND {categories} AS category
MERGE (c:Category {name: category})
MERGE (b)-[:IS_IN]->(c)
'''

merge_category_query = '''
MATCH (b:Business {id: {business_id}})
MERGE (c:Category {name: {category}})
CREATE UNIQUE (c)<-[:IS_IN]-(b)
'''



print("Beginning business batch")
with open('data/yelp_academic_dataset_business.json', 'r') as f:
	tx = db.begin()
	count = 0
	for b in (json.loads(l) for l in f):
		tx.run(create_business_query, b)
		count += 1
		if count >= 10000:
			tx.commit()
			tx = db.begin()
			print("Committing transaction")
			count = 0
	if count > 0:
		tx.commit()
		print("Committing transaction")


## Create spatial layer:
# CALL spatial.createPointLayer('scdemo');

## Add nodes to spatial layer:
# MATCH (b:Business)
# WHERE NOT exists((b)-[:RTREE_METADATA]->())
# WITH b LIMIT 10000
# WITH collect(b) AS businesses
# CALL spatial.addNodes('scdemo', businesses) YIELD node
# RETURN count(*)
