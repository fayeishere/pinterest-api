from flask import Flask, render_template, request, flash, jsonify
import urllib3
from bs4 import BeautifulSoup
 
app = Flask(__name__) 

@app.route('/')
def home():
  return render_template('home.html')

@app.route('/pinterestfeed/meta/<new_subject>', methods=['GET', 'POST'])
def pin(new_subject):
  http = urllib3.PoolManager()

  subject_request = http.request('GET', 'http://pinterest.com/search/pins/?q=' + new_subject)

  # TODO TRYING TO FIGURE OUT HOW TO REQUEST INFINITE SCROLLING FOR SEARCH

  # pin_request = http.request('GET', "http://pinterest.com/resource/SearchResource/get/?source_url=%2Fsearch%2Fpins%2F%3Fq%3Dcoke&data=%7B%22options%22%3A%7B%22query%22%3A%22coke%22%2C%22bookmarks%22%3A%5B%22b28yNXxmMGVmZDA5YjA5Yjk5NDIxZjgzODZjNDRkZWEzNTRhZmIyZDRjZjE3ZWY4YmRmMWE4NmVhZGQwNDg1NTNmOTAw%22%5D%2C%22show_scope_selector%22%3Anull%2C%22scope%22%3A%22pins%22%7D%2C%22context%22%3A%7B%22app_version%22%3A%22041600b%22%7D%2C%22module%22%3A%7B%22name%22%3A%22GridItems%22%2C%22options%22%3A%7B%22scrollable%22%3Atrue%2C%22show_grid_footer%22%3Atrue%2C%22centered%22%3Atrue%2C%22reflow_all%22%3Atrue%2C%22virtualize%22%3Atrue%2C%22item_options%22%3A%7B%22show_pinner%22%3Atrue%2C%22show_pinned_from%22%3Afalse%2C%22show_board%22%3Atrue%7D%2C%22layout%22%3A%22variable_height%22%7D%7D%2C%22append%22%3Atrue%2C%22error_strategy%22%3A1%7D&_=1378489310943")
  soup = BeautifulSoup(subject_request.data)

  main_dict = {}
  descr_dict = {}
  pin_dict = {}
  social_dict = {}
  origin_dict = {}

  def scrapeLink():
    # Get the pin id
    anchors = soup.find_all('a', class_='pinImageWrapper')
    i = 0
    for anchor in anchors:
      # time.sleep(2) # delays for seconds
      new_pin_id_link = anchor.get('href')
      new_pin_id = new_pin_id_link[5:len(new_pin_id_link)-1]
      pin_dict[i] = new_pin_id
      i += 1
  # return new_pin_id

  # Get meta info: description, social stats, hash tags
  def scrapeMeta():
    divs = soup.find_all('div', class_='pinMeta')
    count = 0
    counter = 0
    for div in divs:
      # try to get a description which may include a hashtag
      try:
        new_pin_description = div.select('p')
        try:
          new_description = new_pin_description[0].string.strip()
        except:
          try:
            new_description = new_pin_description[0].get_text(strip=True)
            hash_link = div.select('p a')
            # TODO WE ARE DOING NOTHING WITH HASH which is okay
            hash_pin = hash_link[0].string.strip()
          except:
            new_description = "Some kind of nonsense is happening"
      except:
        new_description = "NO description"
      descr_dict[count] = new_description
      # try to get social stats: repins, likes, comments
      social_list = []
      try:
        pin_society = div.find_all('div', class_='pinSocialMeta')
        pin_social = pin_society[0].select('a')

        for social in pin_social:
          pin_social_num = social.select('em')

          pin_socialTest = str(pin_social_num)

          social_list.append(''.join(filter(lambda x: x.isdigit(), pin_socialTest)))
        print "END of trying"
      except:
        social_list.append("No Social Data Available")
      social_dict[count] = social_list
      print social_dict[count]
      print count
      main_dict[count] = [pin_dict[count], descr_dict[count], social_dict[count]]
      count += 1
      print "END OF THE SHOW..."

  api_dict = main_dict
  meta = [
      api_dict
  ]

  scrapeLink()
  scrapeMeta()
  return jsonify( { 'meta': meta})

@app.route('/pinterestfeed/origin/<pin_id>', methods = ['GET'])
def origin(pin_id):
  http = urllib3.PoolManager()
  # Take our pin id and call its focus page to get the image's origin
  pin_request = http.request('GET', 'http://pinterest.com/pin/' + pin_id)
  pin_soup = BeautifulSoup(pin_request.data)
  # Find and isolate origin link
  pin_source = pin_soup.find_all("div", class_='sourceFlagWrapper')
  for origin in pin_source:
    try:
      origin_link = origin.select('a')
      origin_pin = origin_link[0].get('href')
    except:
      origin_pin = "Uploaded To Pinterest"
  pin_origin = [
        {
            "pin_origin": origin_pin
        }
  ]

  return jsonify( { 'pin_origin': pin_origin})

 
if __name__ == '__main__':
  app.run(debug=True)