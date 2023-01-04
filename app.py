from datetime import datetime
from azure.cosmos import CosmosClient, PartitionKey
from flask import *;

endpoint = "https://dp420abdul.documents.azure.com:443/"
key = "S63SFJSI8GMQYbPxO21W9vL4N2D94nFr3yJwyO3ZAf8yhfzefU7XSd7RQ82c1abS5wkTEYz1O0vDACDb8Jp9sg=="

client = CosmosClient(url=endpoint, credential=key)


database = client.get_database_client('journalapp')
container = database.get_container_client('user_details')


app = Flask(__name__)

@app.route('/')
def index():
   print('Request for index page received')
   value = list(container.read_all_items(max_item_count=10))
   return render_template('index.html',value=value,len=len(value))

@app.route('/delete',methods = ['POST', 'GET'])  
def delete():  
   if request.method == 'POST':
    id = request.form.get('delete')
    userId = request.form.get('userId')
    container.delete_item(id,partition_key=userId)
    return redirect(url_for('index'))

@app.route("/upsert",methods = ['POST', 'GET'])
def upsert():
    if request.method == 'POST':
        id = request.form.get('id')
        userId = request.form.get('userId')
        item = (container.read_item(id,partition_key=userId))
        item['Name'] = request.form.get('Fname')
        item['dept'] = request.form.get('dept')
        item['notes'] = request.form.get('notes')
        container.upsert_item(body=item)
        return redirect(url_for('index'))

@app.route('/update',methods = ['POST', 'GET'])  
def update():  
   if request.method == 'POST':
    id = request.form.get('id')
    userId = request.form.get('userId')
    item = (container.read_item(id,partition_key=userId))
    print(item)
    # item['Name'] = request.form.get('Fname')
    # item['dept'] = request.form.get('dept')
    # item['notes'] = request.form.get('notes')
    # container.upsert_item(body=item)
    return render_template('update.html',item=item)

@app.route('/success',methods = ['POST', 'GET'])  
def success():  
   if request.method == 'POST':
      fname = request.form.get('Fname')
      dept = request.form.get('dept')
      notes = request.form.get('notes')
      mood = request.form.get('mood')
      userID = str(datetime.now()) + fname
      newItem = {
        "id": str(datetime.now()),
        "userId": userID,
        "Name":fname,
        "dept": dept,
        "mood": mood,
        "notes": notes
        }
      container.create_item(newItem)
      return redirect(url_for('index'))

if __name__ == '__main__':
   app.run()