from multiprocessing import Process, Manager
from queue import Queue
import requests
import pandas as pd
import time

from utils import chunkify

def _wrapper(id_val, items, function, queue, sleep):
    for j, item in enumerate(items, 1):
        result = None

        try:
            result = function(item)

        except (IndexError, requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError, KeyboardInterrupt) as e:
            if isinstance(e, KeyboardInterrupt):
                return

        if result:
            queue.put((item, result))

        print('<Process {}>\tProcessed {}/{} requests'.format(id_val, j, len(items)))


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
    from geocode import addr2geo3, zip2geo, coordinates
    import json

    '''
    s = pd.read_csv(
        'Data/us-population-by-zip-code/population_by_zip_2000.csv', usecols=['zipcode'], squeeze=True
    )
    
    data = dispatch_job(s.unique().tolist()[:10], zip2geo, nproc=3)

    df_geo = pd.io.json.json_normalize(data, record_path=['places'], meta=['post code'], errors='ignore')
    df_geo.to_csv('Data/geodata.csv')
    '''
    from geocode import coordinates

    mun = json.load(open('Data/municipalities.json'))
    data = dispatch_job([i for i in mun if i not in coordinates][:500], addr2geo3, nproc=50, sleep=0)
    print(data)
    json.dump(data, open('Data/coordinates.json', 'w'))

