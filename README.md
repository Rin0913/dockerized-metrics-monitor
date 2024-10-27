# Prometheus 和 Grafana 的 Docker 容器化和基礎教學

本 REPO 採用 Prometheus v2.54.1 以及 Grafana 11.2.2，版本在 Docker Compose 是固定的，因此不會隨着官方在 DockerHub 上的更新而更新，以防止某些設定在改版後失效或甚至引發錯誤。

本 README 也是基於此版本進行介紹。

實驗環境是 Docker version 27.3.0，因此也並不保證在未來的 Docker 環境下，Docker-Compose 文件和 Docker Engine 的安裝流程不需要修正。

本 REPO 有針對 Prometheus TSDB 進行設定（在 `docker-compose.yaml` 中 Prometheus 的啓動參數中設置），資料會保存 183 天（半年）；並將資料搜集週期調整爲 5 分鐘一次。

其它詳細內容請參閱：

- [原始站點 - Prometheus 和 Grafana 的 Docker 容器化和基礎教學](https://sandb0x.tw/a/Prometheus_%E5%92%8C_Grafana_%E7%9A%84_Docker_%E5%AE%B9%E5%99%A8%E5%8C%96%E5%92%8C%E5%9F%BA%E7%A4%8E%E6%95%99%E5%AD%B8)

## Also See

- [GitHub - Dockerized-Metrics-Monitor](https://github.com/Rin0913/Dockerized-Metrics-Monitor)
- [Kubernetes 教學 第三篇（Persistent Volume 篇）- 建設 Prometheus 和 Grafana](https://sandb0x.tw/a/Kubernetes_%E6%95%99%E5%AD%B8_%E7%AC%AC%E4%B8%89%E7%AF%87%EF%BC%88Persistent_Volume_%E7%AF%87%EF%BC%89)
