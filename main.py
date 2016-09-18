#!/usr/bin/env python3.4
# Encoding: Utf-8
import random
from collections import OrderedDict, deque
import keys  # create a keys.py file with your twitter tokens if you want to run your own instance !
import logging
from TwitterAPI import TwitterAPI, TwitterRequestError

logging.basicConfig(filename="/tmp/coffebot.log", level=logging.INFO)

intro = [("How about a","?"), ("Why not try the","?"), ("Try a","!"), ("Check out a","!"), ("Nothing like a",".")]
multi = ["","Single", "Double", "Tripple", "Quad"]
size = ["Short", "Tall", "Grande", "Venti® Hot", "Venti® Cold", "Trenta® Cold"]
coffee = ["Espresso", "Espresso Macchiato", "Espresso con Panna", "Caffe Americano", "Cappuccino", "Caffe Latte", "Vanilla Latte", "Caramel Macchiato", "Chocolate Mocha", "White Caffe Mocha", "Frappuccino", "Ristretto", "Chai Tea Latte"]
attribute = ["","Non-Fat", "Iced", "Sugar Free", "Venti", "Soy", "No Foam", "Tripple", "Half Sweet", "Decaf", "Half-Caff" , "Quad", "One-Pump", "Skinny", "Sugar-Free Syrup", "Light Ice", "No Whip", "Dolce Soy"]
syrup_type = ["","With Extra Hot", " And Non-Fat", " On Half-Sweet", " Add One-Pump", "Add Ten-Pump", "And 4-Pump"]
syrup = ["", "Caramel", "Hazelnut", "Cinnamon"]
appendition = ["" ,"And Extra Shot", " Plus Extra Whip", "With An Extra Shot And Cream", "At 120 Degrees", "With Extra Whipped Cream and Chocolate Sauce"]

def order():
    order = OrderedDict()
    order[random.choice(multi)] = True
    for i in range(random.randint(0,5)):
        order[random.choice(attribute)] = True
    order[random.choice(size)] = True
    order[random.choice(coffee)] = True
    order[random.choice(syrup_type)] = True
    order[random.choice(syrup)] = True
    for i in range(random.randint(0,2)):
        order[random.choice(appendition)] = True
    return " ".join(" ".join(order.keys()).split())

def make_tweet(username):
    while True:
        a, b = random.choice(intro)
        o = u"@"+username+" "+a+" "+order()+" "+b
        if len(o) < 140:
            return o

logging.info("Connecting to Twitter API")
api = TwitterAPI(keys.consumer_key, keys.consumer_secret, keys.access_token_key, keys.access_token_secret)
bot = api.request('account/verify_credentials').json()["screen_name"]
msgs = deque(maxlen=1000)  # we keep the last 1000 messages and do not reply to those again
logging.info("Connected")

try:
    for msg in api.request('user', {'replies': 'all'}):
        logging.info("New event")
        logging.debug(msg)
        if "text" in msg:
            logging.info("Event is Tweet")
            id = msg["id"]
            other = msg["user"]["screen_name"]
            to = msg["in_reply_to_screen_name"]
            toid = msg["in_reply_to_status_id"]
            logging.debug(other+" : "+msg["text"])
            if other == bot:
                logging.info("My own tweet")
                msgs.append(id)
            if to == bot and not other == bot and not toid in msgs:
                logging.info("Replying to tweet directed to me !")
                api.request('friendships/create', {'screen_name': other})
                t = make_tweet(other)
                r = api.request('statuses/update', {'in_reply_to_status_id': id, 'status': t})
                logging.info("replied to {} with status {}".format(other, r.status_code))
                msgs.append(id)
            elif bot in msg["text"] and not other == bot:
                logging.info("Was mentioned ! Like or Retweet maybe ?")
                api.request('friendships/create', {'screen_name': other})  #friend them all !
                if random.choice([True,False]):
                    api.request('favorites/create', {'id': id})
                if random.randint(0,10) == 3:  # 1 in 10 chance for retweet
                    api.request('statuses/retweet/:id', {'id': id})
except TwitterRequestError as e:
    logging.exception(e)
