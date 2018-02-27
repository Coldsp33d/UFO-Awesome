from multiprocessing import Process, Manager
from queue import Queue
import requests
import pandas as pd
import time
import sys

from utils import chunkify

def _wrapper(id_val, items, function, queue, sleep):
    for j, item in enumerate(items, 1):
        result = None
        while True:
            retries = 0
            time.sleep(sleep)

            try:
                result = function(item); break
            except (IndexError, requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError):
                retries += 1
                if retries >= 3:
                    break

        if result:
            queue.put((item, result))

        print('<Process {:2d}>\tProcessed {}/{} requests'.format(id_val, j, len(items)))

    print('<Process {:2d}>\tCompleted'.format(id_val))


def dispatch_job(items, function, nproc=8, sleep=0):
    with Manager() as manager:
        q = manager.Queue()

        processes = []
        for i, split in enumerate(list(chunkify(items, len(items) // nproc)), 1):
            p = Process(target=_wrapper, args=(i, split, function, q, sleep))
            processes.append(p)

            p.daemon = True
            p.start()
            

        for p in processes:
            p.join()

        data = []
        while q.qsize() != 0:
            data.append(q.get())

        return dict(data)


if __name__ == '__main__':
    import random
    import json

    import geocode

    from geocode import addr2geo3, zip2geo, coordinates
    from geocode import coordinates, zipcodes
    
    # --- geocoding zipcodes --- #
    s = pd.read_csv(
        'Data/us-population-by-zip-code/population_by_zip_2000.csv', usecols=['zipcode'], squeeze=True
    )
    
    v = [i for i in s.unique().tolist() if i not in zipcodes]
    random.shuffle(v)

    data = dispatch_job(v, zip2geo, nproc=8, sleep=.33)
    data.update(zipcodes)
    
    json.dump(data, open('Data/zipcodes.json', 'w'))
    # df_geo = pd.io.json.json_normalize(data, record_path=['places'], meta=['post code'], errors='ignore')
    # df_geo.to_csv('Data/geodata.csv')
    

    '''
    # ---- geocoding human readable addresses --- #
    mun = json.load(open('Data/municipalities.json'))
    v = [i for i in mun if i not in coordinates]
    random.shuffle(v)

    data = dispatch_job(v, addr2geo3, nproc=8, sleep=.33)
    data.update(coordinates)

    json.dump(data, open('Data/coordinates.json', 'w'))
    '''

