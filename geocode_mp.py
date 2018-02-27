from multiprocessing import Process, Manager
from queue import Queue
import requests
import pandas as pd

from utils import chunkify

def _wrapper(id_val, items, function, queue):
    for j, item in enumerate(items):
        result = None

        while True:
            retries = 0
            try:
                result = function(item)
                break

            except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError):
                retries += 1
                if retries > 3:
                    break

            if result:
                queue.put(result)

            print('<Process {}> Processed {}/{} requests'.format(id_val, j, len(items)))


def dispatch_job(items, function, nproc=8):
    with Manager() as manager:
        q = manager.Queue()

        processes = []
        for i, split in enumerate(list(chunkify(items, len(items) // nproc)), 1):
            p = Process(target=_wrapper, args=(i, split, function, q))
            processes.append(p)

            p.daemon = True
            p.start()
            

        for p in processes:
            p.join()

        data = []
        while q.qsize() != 0:
            data.append(q.get())

        return data


if __name__ == '__main__':
    from geocode import addr2geo, addr2geo2, zip2geo

    s = pd.read_csv(
        'Data/us-population-by-zip-code/population_by_zip_2000.csv', usecols=['zipcode'], squeeze=True
    )
    
    data = dispatch_job(s.unique().tolist()[:10], zip2geo, nproc=3)

    print(data)
    #df_geo = pd.io.json.json_normalize(data, record_path=['places'], meta=['post code'], errors='ignore')
    #df_geo.to_csv('Data/geodata.csv')
