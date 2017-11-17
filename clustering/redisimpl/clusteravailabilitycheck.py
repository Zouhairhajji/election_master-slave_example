
import redis
import threading
import logging
import time
import json

from threading import Timer

logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=logging.DEBUG)

class ClusterAvailabilityCheck(threading.Thread):

    def __init__(self, redis, server_id, url, _queue_, presence_interval):

        threading.Thread.__init__(self)
        self.redis = redis
        self.server_id = server_id
        self.channel_name = "cluster_management_channel"
        self._queue_ = _queue_
        self.presence_interval = presence_interval
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe(self.channel_name)
        self.bootstrap = True
        self.servers = dict()
        self.ordinal = -1
        self.cluster_availability = None
        self.server_url = url

        self.timer = Timer(2*self.presence_interval, self.end_of_bootstrap )
        self.timer.start()
        self.otherserverstatus=dict()

    def end_of_bootstrap(self):
        self.bootstrap = False;
        max_ordinal = -1
        for ordinal in self.servers.keys() :
            if ordinal > max_ordinal :
                max_ordinal = ordinal

        if -1 == max_ordinal :
            self.ordinal = 0
            logging.info("%s is master", self.server_id)

        else :
            #logging.info("max_ordinal = %s", max_ordinal)
            self.ordinal = 1 + max_ordinal
            logging.info("%s is backup", self.server_id)

        if self.cluster_availability :
            self.cluster_availability.set_ordinal(self.ordinal)
            self.cluster_availability.publishClusterPresence()

    def set_cluster_availability(self, cluster_availability):
        self.cluster_availability = cluster_availability



    def is_master(self):

        if self.bootstrap :
            return False

        if self.ordinal == 0 :
            return True

        for ordinal in self.servers.keys():
            if self.ordinal > ordinal :
                return False

        return True

    def get_instance_urls(self):
        urls = list()
        for ordinal in self.servers.keys():
            status = self.servers[ordinal]
            logging.info("%s", status)
            urls.append(status['url'])
        return urls

    def get_master_url(self):
        _ordinal_ = -1
        for ordinal in self.servers.keys():
            if ordinal == self.ordinal :
                continue

            if _ordinal_ == -1 :
                _ordinal_ = ordinal
            else :
                if ordinal < _ordinal_ :
                    _ordinal_ = ordinal

        status = self.servers[_ordinal_]
        return status['url'];


    def run(self):

        #logging.info("Cluster availability check thread routine running.")

        while True :
            message = self.pubsub.get_message()
            if message :
                # logging.info("RECEIVED = %s", message)
                if message['data'] == 1 :
                    None
                else :
                    status = json.loads(message['data'])
                    if self.server_id == status['id'] :
                        #logging.info("From Myself = %s", status['id'])
                        None
                    self.otherserverstatus[status['ordinal']]=status['timestamp_epoch']
                    print(str(self.otherserverstatus))
                    logging.info("server id = [%s] ordinal = [%d] on cluster", status['id'], status['ordinal'])
                    self.servers[status['ordinal']] = status
                    self.check_master_die()


                    #if _status_['id'] == self.server_id :
                    #    logging.info("Server ID = %s (myself)", _status_['id'])

                #if _status_['id'] == self.server_id :
                #    logging.info("RECEIVED = %s (MYSELF)", message)
                time.sleep(0.5)


        #for item in self.pubsub.listen():
        #    logging.info("%s", item)

    def check_master_die(self):
        if self.ordinal == 0 :
            return

        for ordinal,timestamp in self.otherserverstatus.items():
            #print self.cluster_availability
            if(timestamp+self.presence_interval<time.time()):


                if(ordinal +1 == self.ordinal) :
                    logging.info("server has ordinal [%d] dies, i toke his place", ordinal)
                    self.cluster_availability.set_ordinal(ordinal)

                    self.ordinal = ordinal

                    self.otherserverstatus[ordinal] = self.otherserverstatus[self.ordinal]
                    del self.otherserverstatus[self.ordinal]

                    self.servers[ordinal] = self.servers[self.ordinal]
                    del self.servers[self.ordinal]


                    self.cluster_availability.publishClusterPresence()


                    if(self.is_master()) :
                        logging.info("i toke the ordinal [%d] and i'm the master now", ordinal)
                    else :
                        logging.info("i toke the ordinal [%d] and i'm still a slave", ordinal)
                return