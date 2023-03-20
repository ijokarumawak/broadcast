# OBS Monitor API
紆余曲折ありこの形に:
1. **NG**: ivs-monitor 内の typescript OBS web socket を呼び出して実装 -> `https://elk.cloudnativedays.jp/ivs-monitor` からアクセスすると、`ws://switcher01-internal.cloudnativedays.jp` へのセキュアじゃない接続はブラウザでブロックされる
2. **NG**: Fastapi で OBS web socket にアクセスし、結果を返す API を実装、 docker container として `https://elk.cloudnativedays.jp/obs-monitor-api` としてデプロイ -> `switcher01-internal` へのアクセスは tailscale を経由する必要がある、 [docker container として tailscale を使う](https://asselin.engineer/tailscale-docker)場合、 AUTH_KEY を tailscale の admin 権限で作成する必要がある (AUTH_KEY 発行できればこれでもよい)
3. **OK**: Fastapi で実装した obs-monitor-api を elk.cloudnativedays.jp 上のローカルプロセスとして 9000 ポートで実行、 docker container で起動している Nginx からルーティングする

## elk.cloudnativedays.jp のローカルプロセスとして API を起動する
```bash
ssh ubuntu@elk.cloudnativedays.jp
cd elk/obs-monitor-api
nohup uvicorn main:app --host 0.0.0.0 --port 9001 --reload > obs-monitor-api.log 2>&1 &
```

## ローカル端末上で API を起動する
```bash
uvicorn main:app --reload
```
