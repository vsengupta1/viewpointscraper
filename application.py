from bs4 import BeautifulSoup
from flask import Flask, jsonify, request
from threading import Thread
import requests
import re


## mapping candidates to their id
candidates = candidates = [
    {'name': 'donald-trump', 'id': '15723', 'urlAdd': '/platform' , 'race': 'president'},
    {'name': 'kamala-harris', 'id': '120012', 'urlAdd': '/issues/', 'race': 'president' },

    ## Washington Governor 
    {'name': 'bob-ferguson', 'id': '95581', 'urlAdd': '/issues', 'race' : 'governor'},
    {'name': 'dave-reichert', 'id': '51346', 'urlAdd': '/issues/', 'race' : 'governor'},

    ## Indiana Governor 
    {'name': 'jennifer-mccormick', 'id': '175286', 'urlAdd': '/issues', 'race': 'governor'},
    {'name': 'mike-braun', 'id': '148564', 'urlAdd': '/issues', 'race': 'governor'},

    ## Supreme Court 
    {'name': 'dave-larson', 'id': '175627', 'urlAdd': '', 'race': 'supreme-court'},
    {'name': 'sal-mungia', 'id': '217452', 'urlAdd': '/issues/', 'race': 'supreme-court'},

    ## Delaware Governer 
    {'name': 'matt-meyer', 'id': '187275', 'urlAdd': '/vision-of-delaware/', 'race': 'governor'},
    {'name': 'mike-ramone', 'id': '17267', 'urlAdd': '/issues', 'race':'governor'},
    
    ## Montana Governor
    {'name': 'greg-gianforte', 'id': '168594', 'urlAdd':'/Priorities/', 'race': 'governor'}, 
    {'name': 'ryan-busse', 'id': '215485', 'urlAdd': '/issues/', 'race': 'governor'} 
]

candidate_id_map = {
    candidate['name']: {
        'id': candidate['id'],
        'urlAdd': candidate['urlAdd']
    } 
    for candidate in candidates
}

def find_campaign_website(name): 

    cand = candidate_id_map.get(name)

    if not cand:
        return None
    
    print(cand)
    id = cand['id']

    url = f'https://justfacts.votesmart.org/candidate/biography/{id}/{name}'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    ## Find campaign website 
    campaign_link = soup.find('a', string='Campaign Website')
    # Extract the URL from the href attribute
    if campaign_link:
        campaign_url = campaign_link['href']
        return(campaign_url)
    else:
        return None

app = Flask(__name__)

def scrape_website(camp_url):
    res = requests.get(camp_url)
    soup = BeautifulSoup(res.text, 'html.parser')
    return soup.get_text(separator='\n', strip=True)

@app.route('/scrape', methods=['GET'])
## example would be GET /scrape?url=https://www.kamalaharris.org/
def scrape():    
    camp_url = request.args.get('url')
    if not camp_url:
        return jsonify({'error': 'URL parameter is required'}), 400

    campaign_html = scrape_website(camp_url)
    if campaign_html:
        return jsonify({'campaign': campaign_html})
    else:
        return jsonify({'error': 'Error scraping the website'}), 500


@app.route('/campaignURL', methods=['GET'])
## example would be GET /campaignURL?name=kamala-harris
def get_campaign_url():
    print("HERE")
    candidate_name = request.args.get('name')
    if not candidate_name:
        return jsonify({'error': 'Name parameter is required'}), 400

    campaign_url = find_campaign_website(candidate_name)
        
    if campaign_url:
        return jsonify({'campaign_url': campaign_url})
    else:
        return jsonify({'error': 'Campaign URL not found'}), 404


@app.route('/campaign', methods=['GET'])
## example would be GET /campaign?name=kamala-harris
def get_campaign():
    candidate_name = request.args.get('name')
    if not candidate_name:
        return jsonify({'error': 'Name parameter is required'}), 400
 
    campaign_url = find_campaign_website(candidate_name)
       
    if not campaign_url:
        return jsonify({'error': 'Campaign URL not found'}), 404
   
    ##scrape the website
    real_url = campaign_url + candidate_id_map[candidate_name]['urlAdd']
    campaign_html = scrape_website(real_url)
    if campaign_html:
        return jsonify({'campaign': campaign_html})
    else:
        return jsonify({'error': 'Error scraping the website'}), 500



if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8000))  # Azure sets PORT
    app.run(host='0.0.0.0', port=port, debug=True)
