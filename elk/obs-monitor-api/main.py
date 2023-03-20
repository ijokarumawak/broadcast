from fastapi import FastAPI
import yaml
import simpleobsws

config = None
obs = {}

with open('config.yml', 'r') as file:
  config = yaml.safe_load(file)
  print(config)

class ObsMonitor:
    def __init__(self, host, port, password) -> None:
        parameters = simpleobsws.IdentificationParameters(
            ignoreNonFatalRequestChecks=False)
        self.host = host
        self.ws = simpleobsws.WebSocketClient(
            url=f'ws://{host}:{port}', password=password, identification_parameters=parameters)

    async def connect(self):
        await self.ws.connect()
        # Wait for the identification handshake to complete
        await self.ws.wait_until_identified()

    async def disconnect(self):
        await self.ws.disconnect()

    async def getStats(self):
        stats = {}
        request = simpleobsws.Request('GetStats')
        ret = await self.ws.call(request)
        if ret.ok():
            stats = ret.responseData
            stats['host'] = {'hostname': self.host}

        request = simpleobsws.Request('GetStreamStatus')
        ret = await self.ws.call(request)
        if ret.ok():
            stats['streamStatus'] = ret.responseData

        return stats

    async def getMediaProgress(self):
        request = simpleobsws.Request('GetInputList', {'inputKind': 'vlc_source'})
        ret = await self.ws.call(request)
        if ret.ok():
          input_list = ret.responseData
          for input in input_list['inputs']:
            print('input {}'.format(input))
            request = simpleobsws.Request('GetMediaInputStatus', {'inputName': input['inputName']})
            ret = await self.ws.call(request)
            if ret.ok():
              media = ret.responseData
              if media['mediaState'] == 'OBS_MEDIA_STATE_PLAYING' and media['mediaDuration'] > 0:
                media['inputName'] = input['inputName']
                return media

        return {}



app = FastAPI()


@app.on_event('startup')
async def startup():
  for track in config['tracks']:
    obs_config = track['obs']
    obs_monitor = ObsMonitor(host=obs_config['host'], port=obs_config['port'], password=obs_config['password'])
    obs[track['name']] = obs_monitor
    print('Connecting to OBS for track {}. {}'.format(track['name'], obs_monitor))
    await obs_monitor.connect()
    print('Connected to OBS for track {}. {}'.format(track['name'], obs_monitor))


@app.get("/")
async def root():
  return {'message': 'hello'}

@app.get("/stats/{track_name}")
async def get_track_stats(track_name: str):
  return await obs[track_name].getStats()

@app.get("/media-progress/{track_name}")
async def get_media_progress(track_name: str):
  input_list = await obs[track_name].getMediaProgress()
  return input_list
