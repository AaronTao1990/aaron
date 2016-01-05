from pymongo import Connection

class MongoUtil(object):
    '''util to manage mongo connection and mongo opperations'''

    def __init__(self, host, db, coll):
        conn = Connection(host)
        self.db = conn[db]
        self.coll = self.db[coll]

    def find_all(self, query, limit):
        for item in self.coll.find(query).limit(limit):
            yield item

    def find_one(self, query):
        return self.coll.find_one(query)

    def save(self, item):
        self.coll.save(item)

    def exists(self, query):
        for item in self.coll.find(query):
            return True
        return False

    def remove(self, query):
        self.coll.remove(query)

def load_keywords(filename):
    import json
    with open(filename, 'r') as f:
        for line in f.readlines():
            line = line.strip()
            item = None
            try:
                item = json.loads(line)
            except Exception:
                print 'invalid line : %s' % line
                continue
            yield item

def main():
    filename = 'wechat_list.txt'
    mongo_util = MongoUtil('10.111.0.28,10.111.0.29,10.111.0.38', 'wemedia', 'wemedia')
    for item in load_keywords(filename):
        mongo_util.save(item)

if __name__ == '__main__':
    main()
