from datetime import datetime
from azure.cosmos import CosmosClient, PartitionKey
from flask import *
import requests
import simplejson as json


# Secret for Cosmos DB
url_access_token = "https://login.microsoftonline.com/6f28e5b8-67fe-4207-a048-cc17b8e13499/oauth2/v2.0/token"
payload = 'grant_type=client_credentials&client_id=db3c96e7-ae46-4d9c-a65c-16078c15cb94&client_secret=en78Q~eon6EF5lgfdM2-urI5-4jns1yart.J4aj3&scope=https%3A%2F%2Fvault.azure.net%2F.default'
headers_access_token = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Cookie': 'fpc=AkJAfn7l3j1Pi9aeBcxoF6mKGKpcAgAAALvVZdsOAAAA; stsservicecookie=estsfd; x-ms-gateway-slice=estsfd'
}

response_access_token = requests.request(
    "POST", url_access_token, headers=headers_access_token, data=payload)

bearer_token = (json.loads(response_access_token.text)['access_token'])


# Connect to Cosmos Client
url_cosmos = "https://azimkeyvault.vault.azure.net/secrets/cosmoskey/877b5070a02d4be3ae6725a6ccdc3e1c?api-version=7.3"
endpoint_cosmos = "https://dp420abdul.documents.azure.com:443/"
headers_cosmos = {
    'Authorization': 'Bearer ' + bearer_token
}

response_secret = requests.request("GET", url_cosmos, headers=headers_cosmos)
cosmos_secret_key = (json.loads(response_secret.text)['value'])
client = CosmosClient(url=endpoint_cosmos, credential=cosmos_secret_key)


# Sentiment
url_sentiment = "https://sentiment-by-api-ninjas.p.rapidapi.com/v1/sentiment"
url_sentiment_key = "https://azimkeyvault.vault.azure.net/secrets/nlpkey/c66457d980e14cdd9a7b3ebe90a200b0?api-version=7.3"
headers_sentiment_key = {
    'Authorization': 'Bearer ' + bearer_token
}

response_sentiment = requests.request(
    "GET", url_sentiment_key, headers=headers_sentiment_key)
sentiment_key = (json.loads(response_sentiment.text)['value'])

headers_sentiment = {
	"X-RapidAPI-Key": sentiment_key,
	"X-RapidAPI-Host": "sentiment-by-api-ninjas.p.rapidapi.com"
}


# Read database and container
database = client.get_database_client('journalapp')
container = database.get_container_client('user_details')


app = Flask(__name__)
@app.route('/')
def index():
   value = list(container.read_all_items(max_item_count=50))
   return render_template('index.html', value=value, len=len(value))


@app.route('/delete', methods=['POST', 'GET'])
def delete():
   if request.method == 'POST':
    id = request.form.get('delete')
    userId = request.form.get('userId')
    container.delete_item(id, partition_key=userId)
    return redirect(url_for('index'))


@app.route("/upsert", methods=['POST', 'GET'])
def upsert():
    if request.method == 'POST':
        id = request.form.get('id')
        userId = request.form.get('userId')
        item = (container.read_item(id, partition_key=userId))
        item['Name'] = request.form.get('Fname')
        item['dept'] = request.form.get('dept')
        item['notes'] = request.form.get('notes')
        item['last_updated'] = str(
            datetime.now().strftime('%Y/%m/%d %I:%M:%S'))

        querystring = {"text": item['notes']}
        response = requests.request(
            "GET", url_sentiment, headers=headers_sentiment, params=querystring)
        var = (json.loads(response.text))

        if (var['sentiment'] == 'NEUTRAL'):
          item['mood'] = 'https://img.icons8.com/emoji/512/neutral-face.png'

        if (var['sentiment'] == 'POSITIVE'):
          item['mood'] = 'https://img.icons8.com/emoji/512/star-struck.png'

        if (var['sentiment'] == 'NEGATIVE'):
          item['mood'] = 'https://img.icons8.com/emoji/512/weary-face.png'

        if (var['sentiment'] == 'WEAK_NEGATIVE'):
          item['mood'] = 'https://img.icons8.com/emoji/512/pensive-face.png'

        if (var['sentiment'] == 'WEAK_POSITIVE'):
          item['mood'] = 'https://img.icons8.com/emoji/512/smiling-face-with-smiling-eyes.png'

        container.upsert_item(body=item)
        return redirect(url_for('index'))


@app.route('/update', methods=['POST', 'GET'])
def update():
   if request.method == 'POST':
    id = request.form.get('id')
    userId = request.form.get('userId')
    item = (container.read_item(id, partition_key=userId))
    return render_template('update.html', item=item)


@app.route('/success', methods=['POST', 'GET'])
def success():
   if request.method == 'POST':
      fname = request.form.get('Fname')
      dept = request.form.get('dept')
      notes = request.form.get('notes')

      querystring = {"text": notes}
      response = requests.request(
          "GET", url_sentiment, headers=headers_sentiment, params=querystring)
      var = (json.loads(response.text))

      if (dept == 'Select your Department'):
         dept = 'Other'

      if (var['sentiment'] == 'NEUTRAL'):
        mood = 'https://img.icons8.com/emoji/512/neutral-face.png'

      if (var['sentiment'] == 'POSITIVE'):
        mood = 'https://img.icons8.com/emoji/512/star-struck.png'

      if (var['sentiment'] == 'NEGATIVE'):
        mood = 'https://img.icons8.com/emoji/512/weary-face.png'

      if (var['sentiment'] == 'WEAK_NEGATIVE'):
        mood = 'https://img.icons8.com/emoji/512/pensive-face.png'

      if (var['sentiment'] == 'WEAK_POSITIVE'):
        mood = 'https://img.icons8.com/emoji/512/smiling-face-with-smiling-eyes.png'

      newItem = {
          "id": str(datetime.now()),
          "userId": fname,
          "Name": fname,
          "dept": dept,
          "notes": notes,
          "mood": mood,
          "mood_res": var['sentiment'],
          "last_updated": str(datetime.now().strftime('%Y/%m/%d %I:%M:%S'))
      }
      container.create_item(newItem)
      return redirect(url_for('index'))


if __name__ == '__main__':
   app.run()
