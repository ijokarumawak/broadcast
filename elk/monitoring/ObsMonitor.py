import simpleobsws
import asyncio


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

    async def getInputs(self):
        videoSettings = None
        request = simpleobsws.Request('GetVideoSettings')
        ret = await self.ws.call(request)
        if ret.ok():
            videoSettings = ret.responseData

            inputs = []
            request = simpleobsws.Request('GetInputList')
            ret = await self.ws.call(request)

            if ret.ok():
                for input in ret.responseData['inputs']:
                    input['host'] = {'hostname': self.host}
                    inputName = input['inputName']
                    inputs.append(input)
                    request = simpleobsws.Request('GetInputVolume', requestData={
                                                  'inputName': inputName})
                    ret = await self.ws.call(request)
                    if ret.ok():
                        input['volume'] = ret.responseData

                    request = simpleobsws.Request('GetInputAudioBalance', requestData={
                                                  'inputName': inputName})
                    ret = await self.ws.call(request)
                    if ret.ok():
                        input['audioBalance'] = ret.responseData

                    request = simpleobsws.Request('GetSourceActive', requestData={
                                                  'sourceName': inputName})
                    ret = await self.ws.call(request)
                    if ret.ok():
                        input['sourceActive'] = ret.responseData
                        imageWidth = videoSettings['outputWidth'] / 8
                        imageHeight = videoSettings['outputHeight'] / 8
                        if input['sourceActive']['videoActive'] and input['sourceActive']['videoShowing']:
                            request = simpleobsws.Request('GetSourceScreenshot', requestData={
                                'sourceName': inputName,
                                'imageFormat': 'jpeg',
                                'imageWidth': imageWidth,
                                'imageHeight': imageHeight,
                                'imageCompressionQuality': 10})
                            ret = await self.ws.call(request)
                            if ret.ok():
                                input['screenshot'] = ret.responseData
                                input['screenshot']['width'] = imageWidth
                                input['screenshot']['height'] = imageHeight

        return inputs

    async def getOutputs(self):
        outputs = []
        request = simpleobsws.Request('GetOutputList')
        ret = await self.ws.call(request)
        if ret.ok():
            for output in ret.responseData['outputs']:
                output['host'] = {'hostname': self.host}
                outputName = output['outputName']
                outputs.append(output)
                request = simpleobsws.Request('GetOutputStatus', requestData={
                                              'outputName': outputName})
                ret = await self.ws.call(request)
                if ret.ok():
                    output['status'] = ret.responseData

                request = simpleobsws.Request('GetOutputSettings', requestData={
                                              'outputName': outputName})
                ret = await self.ws.call(request)
                if ret.ok():
                    output['settings'] = ret.responseData
        return outputs

