import requests, json, time, shutil, os, textwrap, uuid
from bs4 import BeautifulSoup
from PIL import Image, ImageOps, ImageDraw, ImageFont

def get_blog_data(limit, line_len):
    black_list_autor = []
    black_list_content = []
    
    url = "https://quotes15.p.rapidapi.com/quotes/random/"
    querystring = {"language_code":"de"}
    headers = {
        "X-RapidAPI-Host": "quotes15.p.rapidapi.com",
        "X-RapidAPI-Key": ""
    }

    while True:
        blog_data = []
        
        try:
            response = requests.request("GET", url, headers=headers, params=querystring)
            #print(response.text)
        except:
            print("no connection to tagrget server")
            time.sleep(2)
            continue
        
        json_quotes = json.loads(response.text)
        #print(json_quotes)

        try:
            x = json_quotes["content"]
        except KeyError:
            #print(x)
            print("fail")
            time.sleep(1.2)
            continue
        
        if json_quotes["originator"]["name"] in black_list_autor:
            continue
        if json_quotes["content"].lower() in black_list_content:
            continue

        quotes_content = json_quotes["content"]
        if(len(quotes_content) >= limit):
            print("text over limit: "+str(len(quotes_content))+"/"+str(limit))
            time.sleep(1.6)
            continue
        else:
            print(len(quotes_content))

        request_autor_html = requests.get(json_quotes["originator"]["url"])
        soup = BeautifulSoup(request_autor_html.text, "html.parser")
        inputTags = soup.findAll(attrs={"class" : "mx-auto d-block"})
        autor_img_url = str(inputTags).split('src="')
        try:
            autor_img_url = "https://beruhmte-zitate.de"+str(autor_img_url[1][:-16])
        except:
            continue     
        
        blog_data.append(True)
        blog_data.append(json_quotes["id"])
        blog_data.append(textwrap.fill(json_quotes["content"], width=line_len, break_long_words=True, replace_whitespace=False))
        blog_data.append(json_quotes["originator"]["name"])
        blog_data.append(json_quotes["originator"]["url"])
        blog_data.append(autor_img_url)

        return blog_data


while True:
    blog_post_data = get_blog_data(180, 19)
    #print(blog_post_data)

    image_url = blog_post_data[5]
    filename = image_url.split("/")[-1]
    r = requests.get(image_url, stream = True)
    r.raw.decode_content = True
    with open(filename,'wb') as f:
        shutil.copyfileobj(r.raw, f)

    im = Image.open(filename)
    os.remove(filename) 
    autor_size = 840
    im = im.resize((autor_size,autor_size));
    bigsize = (im.size[0] * 3, im.size[1] * 3)
    mask = Image.new('L', bigsize, 0)
    draw = ImageDraw.Draw(mask) 
    draw.ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(im.size, Image.ANTIALIAS)
    im.putalpha(mask)

    output = ImageOps.fit(im, mask.size, centering=(0.5, 0.5))
    output.putalpha(mask)
    #output.save('output.png')

    background = Image.open('blanc.png')
    try: #ValueError: bad transparency mask
        background.paste(im, (550, 129), im)
    except:
        continue
    
    #autor
    draw = ImageDraw.Draw(background)
    font = ImageFont.truetype("NuosuSIL-Regular.ttf", 70)
    draw.text((100, 150),blog_post_data[3],(52, 152, 219),font=font)

    #autor text
    font = ImageFont.truetype("NuosuSIL-Regular.ttf", 45)
    draw.text((100, 300),blog_post_data[2],(0, 0, 0),font=font)

    background.save("result/"+str(uuid.uuid4())+'.png')
