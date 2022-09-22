import asyncio
import os
from datetime import datetime
from typing import final
from unicodedata import name
from elasticsearch import AsyncElasticsearch
from elasticsearch import ApiError
from elasticsearch import ConnectionError
from elasticsearch.helpers import async_bulk
from monitoring.ObsMonitor import ObsMonitor
import json

CLOUD_ID = os.environ.get("ES_CLOUD_ID")
ES_HOSTS = os.environ.get("ES_HOSTS")
API_KEY = os.environ["ES_API_KEY"]

HOSTS = os.environ["WSHOSTS"]
PORT = os.environ["WSPORT"]
PASS = os.environ["WSPASS"]

# TODO: Subscribe inputVolumeMeter https://github.com/obsproject/obs-websocket/blob/master/docs/generated/protocol.md#eventsubscriptioninputvolumemeters
# TODO: How about implementing this as an Integration? It has to start with a metricbeat module, then an integration package. Takes too much time.
monitors = [ObsMonitor(host.strip(), PORT, PASS) for host in HOSTS.split(',')]
if CLOUD_ID:
    es = AsyncElasticsearch(cloud_id=CLOUD_ID, api_key=API_KEY)
elif ES_HOSTS:
    es = AsyncElasticsearch(hosts=ES_HOSTS, api_key=API_KEY)
else:
    raise Exception('Either ES_CLOUD_ID or ES_HOSTS is required.')

tasks = []

datastream = 'metrics-obs.{}-{}'


def addMetadata(doc, dataset, namespace, i=None):
    doc['_index'] = datastream.format(dataset, namespace)
    doc['_op_type'] = 'create'
    doc['@timestamp'] = datetime.utcnow().isoformat()
    doc['data_stream'] = {}
    doc['data_stream']['dataset'] = dataset
    doc['data_stream']['namespace'] = namespace
    if i is not None:
        doc['i'] = i
    return doc


def addLatestMetadata(doc, namespace):
    doc['_index'] = 'obs.latest-' + namespace
    doc['_id'] = doc['host']['hostname']
    doc['@timestamp'] = datetime.utcnow().isoformat()
    doc['data_stream'] = {}
    doc['data_stream']['namespace'] = namespace
    return doc


# https://stackoverflow.com/questions/37512182/how-can-i-periodically-execute-a-function-with-asyncio
async def repeat(interval, func, *args, **kwargs):
    """Run func every interval seconds.

    If func has not finished before *interval*, will run again
    immediately when the previous iteration finished.

    *args and **kwargs are passed as the arguments to func.
    """
    while True:
        await asyncio.gather(
            func(*args, **kwargs),
            asyncio.sleep(interval),
        )


async def getMetrics(monitor, namespace):
    stats = addMetadata(await monitor.getStats(), 'stats', namespace)
    rawInputs = await monitor.getInputs()
    actions = []

    screenshot = next(filter(lambda input: input['sourceActive']['videoActive']
                      and input['sourceActive']['videoShowing'], rawInputs), None)
    if screenshot is not None:
        # Copy the input to avoid bulk action metadata conflict
        actions.append(addLatestMetadata(screenshot.copy(), namespace))

    inputs = [addMetadata(x, 'inputs', namespace, i)
              for i, x in enumerate(rawInputs)]
    outputs = [addMetadata(x, 'outputs', namespace, i) for i, x in enumerate(await monitor.getOutputs())]

    actions += [stats] + inputs + outputs

    try:
        await async_bulk(es, actions)
    except (ConnectionError, ApiError) as e:
        print('Elasticsearch data ingestion failed.')
        print(e)


async def main():
    for monitor in monitors:
        await monitor.connect()

        namespace = 'staging'

        task = asyncio.ensure_future(
            repeat(10, getMetrics, monitor, namespace))
        tasks.append(task)

    await asyncio.gather(*tasks)


async def close():
    for monitor in monitors:
        await monitor.disconnect()
    await es.close()


loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(main())
except KeyboardInterrupt:
    for task in tasks:
        task.cancel()
finally:
    loop.run_until_complete(close())
    loop.close()

