#!/usr/bin/env python
"""
An example consumer that uses a greenlet pool to accept incoming market
messages. This example offers a high degree of concurrency.
"""
import zlib
import simplejson
import gevent
from gevent.pool import Pool
from gevent import monkey; gevent.monkey.patch_all()
from gevent import Timeout
import zmq
import MySQLdb as mdb
import locale
import pika
import datetime
import ConfigParser

locale.setlocale(locale.LC_ALL, 'en_US.utf8')


#.eve.creds contains the following values
#dbServer
#dbUser
#dbPassword
#database

insertData     = []
config_file = '.eve.creds'
execfile(config_file)

# The maximum number of greenlet workers in the greenlet pool. This is not one
# per processor, a decent machine can support hundreds or thousands of greenlets.
# I recommend setting this to the maximum number of connections your database
# backend can accept, if you must open one connection per save op.
MAX_NUM_POOL_WORKERS = 20

def main():
  """
  The main flow of the application.
  """
  context = zmq.Context()
  subscriber = context.socket(zmq.SUB)

  # Connect to the first publicly available relay.
  subscriber.connect('tcp://relay-us-central-1.eve-emdr.com:8050')
  # Disable filtering.
  subscriber.setsockopt(zmq.SUBSCRIBE, "")

  # We use a greenlet pool to cap the number of workers at a reasonable level.
  greenlet_pool = Pool(size=MAX_NUM_POOL_WORKERS)

  print("Worker pool size: %d" % greenlet_pool.size)

  while True:
    # Since subscriber.recv() blocks when no messages are available,
    # this loop stays under control. If something is available and the
    # greenlet pool has greenlets available for use, work gets done.
    greenlet_pool.spawn(worker, subscriber.recv())


def worker(job_json):
  insertData     = []

  """
  For every incoming message, this worker function is called. Be extremely
  careful not to do anything CPU-intensive here, or you will see blocking.
  Sockets are async under gevent, so those are fair game.
  """
  # Receive raw market JSON strings.
  market_json = zlib.decompress(job_json)
  # Un-serialize the JSON data to a Python dict.
  market_data = simplejson.loads(market_json)
  # Save to your choice of DB here.


  if market_data['resultType'] == 'orders':

  #get userID out of uploadKeys, not neccesarily trustworthy, but something
    for item in market_data['uploadKeys']:
      if not item.get('key') == "0":
        userID = item.get('key')
        name = item.get('name')


    generatorName = market_data['generator']['name']
    generatorVersion = market_data['generator']['version']


    for item in market_data['rowsets']:
      for row in item['rows']:
        #we're only storing jita data for now
        if row[10] == 30000142:

          price = int(row[0] * 100)
#          print row[7]

          #append to bulk mysql import object          
          insertData.append({"orderID": row[3], "userID": userID, "name": name, "generatorName": generatorName, "price": price, "volRemaining": row[1], "volEntered": row[4], "minVolume": row[5], "issueDate": row[7], "duration": row[8], "stationID": row[9], "generatedAt": item['generatedAt'], "typeID": item['typeID'], "bid": row[6]})

          if len(insertData) > 49:
            con = mdb.connect(dbServer , dbUser, dbPassword, database);
            cur = con.cursor()
            cur.execute('SET autocommit = 0')

            for entry in insertData:


              if entry['bid'] == True:
                statement = """INSERT INTO jita_buy_orders( 
                                                           orderID,
                                                           userID,
                                                           name,
                                                           generatorName,
                                                           price,
                                                           volRemaining,
                                                           volEntered,
                                                           minVolume,
                                                           issueDate,
                                                           duration,
                                                           stationID,
                                                           generatedAt,
                                                           typeID
                                                          )
                            VALUES (
                                    "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s" 
                                   )ON DUPLICATE KEY UPDATE volRemaining = %s"""%(
                                                          entry['orderID'],
                                                          entry['userID'],
                                                          entry['name'],
                                                          entry['generatorName'],
                                                          entry['price'],
                                                          entry['volRemaining'],
                                                          entry['volEntered'],
                                                          entry['minVolume'],
                                                          entry['issueDate'],
                                                          entry['duration'],
                                                          entry['stationID'],
                                                          entry['generatedAt'],
                                                          entry['typeID'],
                                                          entry['volRemaining']
                                                         )

              if entry['bid'] == False:
                statement = """INSERT INTO jita_sell_orders(
                                                           orderID,
                                                           userID,
                                                           name,
                                                           generatorName,
                                                           price,
                                                           volRemaining,
                                                           volEntered,
                                                           minVolume,
                                                           issueDate,
                                                           duration,
                                                           stationID,
                                                           generatedAt,
                                                           typeID
                                                          )
                            VALUES (
                                    "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s"
                                   )ON DUPLICATE KEY UPDATE volRemaining = %s"""%(

                                                          entry['orderID'],
                                                          entry['userID'],
                                                          entry['name'],
                                                          entry['generatorName'],
                                                          entry['price'],
                                                          entry['volRemaining'],
                                                          entry['volEntered'],
                                                          entry['minVolume'],
                                                          entry['issueDate'],
                                                          entry['duration'],
                                                          entry['stationID'],
                                                          entry['generatedAt'],
                                                          entry['typeID'],
                                                          entry['volRemaining']
                                                         )


#              print statement
              cur.execute(statement)
            
            con.commit()
            con.close()
            insertData = []


if __name__ == '__main__':
    main()

