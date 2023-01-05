from datetime import datetime
from azure.cosmos import CosmosClient, PartitionKey
from flask import *;
import requests
import simplejson as json




endpoint = "https://dp420abdul.documents.azure.com:443/"
key = "S63SFJSI8GMQYbPxO21W9vL4N2D94nFr3yJwyO3ZAf8yhfzefU7XSd7RQ82c1abS5wkTEYz1O0vDACDb8Jp9sg=="
url = "https://sentiment-by-api-ninjas.p.rapidapi.com/v1/sentiment"

client = CosmosClient(url=endpoint, credential=key)

headers = {
	"X-RapidAPI-Key": "9912cc18d7mshba16d59b04a871bp1584a1jsne756fb362b2c",
	"X-RapidAPI-Host": "sentiment-by-api-ninjas.p.rapidapi.com"
}


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

        querystring = {"text":item['notes']}
        response = requests.request("GET", url, headers=headers, params=querystring)
        var = (json.loads(response.text))

        if(var['sentiment']=='NEUTRAL'):
          item['mood'] = 'https://img.icons8.com/emoji/512/neutral-face.png'
      
        if(var['sentiment']=='POSITIVE'):
          item['mood'] = 'https://img.icons8.com/emoji/512/star-struck.png'

        if(var['sentiment']=='NEGATIVE'):
          item['mood'] = 'https://img.icons8.com/emoji/512/weary-face.png'

        if(var['sentiment']=='WEAK_NEGATIVE'):
          item['mood'] = 'https://img.icons8.com/emoji/512/pensive-face.png'
      
        if(var['sentiment']=='WEAK_POSITIVE'):
          item['mood'] = 'https://img.icons8.com/emoji/512/smiling-face-with-smiling-eyes.png'

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
      userID = str(datetime.now()) + fname

      querystring = {"text":notes}
      response = requests.request("GET", url, headers=headers, params=querystring)
      var = (json.loads(response.text))

      if(dept == 'Select your Department'):
         dept = 'Other'

      if(var['sentiment']=='NEUTRAL'):
        mood = 'https://img.icons8.com/emoji/512/neutral-face.png'
      
      if(var['sentiment']=='POSITIVE'):
        mood = 'https://img.icons8.com/emoji/512/star-struck.png'

      if(var['sentiment']=='NEGATIVE'):
        mood = 'https://img.icons8.com/emoji/512/weary-face.png'

      if(var['sentiment']=='WEAK_NEGATIVE'):
        mood = 'https://img.icons8.com/emoji/512/pensive-face.png'
      
      if(var['sentiment']=='WEAK_POSITIVE'):
        mood = 'https://img.icons8.com/emoji/512/smiling-face-with-smiling-eyes.png'

      newItem = {
        "id": str(datetime.now()),
        "userId": userID,
        "Name":fname,
        "dept": dept,
        "notes": notes,
        "mood":mood,
        "mood_res":var['sentiment']
        }
      container.create_item(newItem)
      return redirect(url_for('index'))

if __name__ == '__main__':
   app.run()