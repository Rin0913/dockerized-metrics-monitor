# metrics-filter

修改 `sample.config`，設定其中參數：
- `TARGET`：目標 Exporter，例如如果你的 exporter 是 `http://localhost:9090/metrics`，請填入 `http://localhost:9090`；
- `PORT`：服務要開啓的 Port，預設爲 8000。

之後將需要的關鍵字放入 `whitelist.txt`，程式會自動篩選掉不包含關鍵字的 metrics。關鍵字一行一個，越是精準，篩選效果越好。

---

使用方式：

如果想使用 `sample.conf` 來的設定檔來開啓 metric-filter，請執行以下指令（你可以在同一臺主機上開啓多個 instance）：
```
python3 main.py -c sample.conf
```

透過 `http://{server-ip}:{port}/{path}` 來取得 metrics 資料，其中的 {path} 是你原本在 exporter 上使用的 ULR path。

例如如果 exporter 是 `https://localhost:9090/metrics`，並且將服務架設在 `192.168.1.1` 的 8000 port 上，則透過 `http://192.168.1.1:8000/metrics` 來取得過濾後的資料。
