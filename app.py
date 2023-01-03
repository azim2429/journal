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
   return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/hello', methods=['POST'])
def hello():
   name = request.form.get('name')

   if name:
       print('Request for hello page received with name=%s' % name)
       return render_template('hello.html', name = name)
   else:
       print('Request for hello page received with no name or blank name -- redirecting')
       return redirect(url_for('index'))


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