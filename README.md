# 基於 Prometheus 和 Grafana 的基礎資源數據蒐集監控系統的 Docker 模板

本 REPO 採用 Prometheus v2.54.1 以及 Grafana 11.2.2，版本在 Docker Compose 是固定的，因此不會隨着官方在 DockerHub 上的更新而更新，以防止某些設定在改版後失效或甚至引發錯誤。

本 README 也是基於此版本進行介紹。

實驗環境是 Docker version 27.3.0，因此也並不保證在未來的 Docker 環境下，Docker-Compose 文件和 Docker Engine 的安裝流程不需要修正。

本 REPO 有針對 Prometheus TSDB 進行設定，資料會保存 183 天（半年）；並將資料搜集週期調整爲 5 分鐘一次。

## Prerequisite

需要安裝以下程式：
1. Docker 和 Docker Compose；
2. Make。

以 Debian 12 爲例，以下爲當下官網提供的標準安裝流程（2024/10/06）：

```sh
###### Docker Engine

# Remove conflicting packages:
for pkg in docker.io docker-doc docker-compose podman-docker containerd runc; do sudo apt-get remove $pkg; done

# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

# Install the docker packages:
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

###### Other Softwares
sudo apt-get update
sudo apt-get install make


###### Check
docker -v
make -v | grep Make
```

## 基本操作

```
sudo make up        # 在背景開啓服務（關閉 Terminal 不會導致程式結束）
sudo make down      # 關閉服務
sudo make restart   # 重啓服務
```

## 基本設定 Grafana

### 連上 Grafana

假設機器 IP 是 192.168.1.1，則你可以透過 http://192.168.1.1:3000 連上 Grafana。

### 登入 Grafana

被指定的預設帳號密碼皆爲 admin/admin，第一次登入之後即會跳轉到改密碼的界面。

### 設定該使用者

改完密碼或是跳過此環節，進入主頁面之後，點擊右上角的使用者頭像，會展開一個選單，點擊 Profile，則可以進入帳號設定頁面。

在帳號設定頁面，Profile 區塊可以設定該帳號的 Email 和使用者名稱；Preferences 區塊可以設定要亮色還是暗色主題，以及語言，支持簡體中文。設定完成後保存生效。

### 增加其它使用者

之後看左上角 Grafana 圖標下方，有個三條線的菜單選項，點擊即可縮放選單，點擊其中的 Administration，其中有 Users and access 的選項，在裏面可以設定 Users，遂可以新增、刪除使用者。

還有着串接 AD/LDAP 的功能，不過那需要比較複雜的額外設定，並且還需要解決 LDAP 與 Grafana 之間 TLS 憑證信任問題（倘若是自簽 CA），因此這邊不追述。

### 串接 Prometheus 資料

在點擊 Administration 之前，你應該會看到菜單選項存在一個 Connections，其中包含細項 Data Sources，點下去之後就可以新增 Data Source。

我們選擇 Prometheus，進入到初始設定頁面後稍微往下滑，會在第二個設定區塊看到 Connection，在 Prometheus server URL 欄位中填入 `http://192.168.1.1:9090`，這邊假設你的服務是建在 192.168.1.1 這臺機器，正如前面連線 Grafana 一樣。

之後滑到最下面，點擊藍色的 Save & Test，如果跳出綠色的 Successfully queried the Prometheus API 字樣，就代表成功串接並且已保存次 Data Source，此時可以離開此頁面了。

## 基本設定 Prometheus

修改 `prometheus.yml` 可以修改基本設定。

例如修改 `scrape_interval: 5m` 就可以將資料搜集週期改的更長或更短。

### 連上 Prometheus

正如之前的 IP 假設，我們可以嘗試在瀏覽器訪問 `http://192.168.1.1:9090`，此時應該可以看到 Prometheus 的界面。

但在他的 Web GUI 上面，我們並沒辦法測試任何東西，僅能做檢查。

### 檢查 Prometheus 狀態

在上方暗色 NavBar 中，有個 Status 的下拉式選單：
1. 點擊 Command-Line Flags，我們能看到 Prometheus 程式開啓時候的啓動參數。
2. 點擊 Configuration，我們能看到同這個 README 文件的目錄下經過 Prometheus 解析過的 `prometheus.yml` 設定檔。
3. 點擊 Targets，我們能看到 Prometheus 正在蒐集哪些 Exporters 發出的 Metrics，以及那些 Exporters 的狀態。

而點擊 NavBar 中的 Graph，我們可以在其中輸入 PromQL（Prometheus 的查詢語法），即可測試是否有正確收集到的資料，以及確認 PromQL 的正確性。

### 增加 Target

增加 Target，即是增加被監控的 Exporter。

最基礎的情況是，直接修改 `prometheus.yml`，並加入以下資訊，之後修正縮排：

```yaml
- job_name: '{your-target, e.g. ElasticNode1}'
  static_configs:
    - targets: ['{export-for-your-target, e.g. 192.168.1.2:9100}']
```

在這種情況，它就會去自動抓 `192.168.1.2:9100/metrics`，但有些 exporter 的輸出路徑不是 metrics 或是不直接是 metrics，此時可能就要新增其它參數。

在你使用 PVE-exporter 監控 `192.168.2.1` 的 PVE，並且將之架設在 `192.168.1.3` 的時候，你可能就會新增以下的設定，它會自動去抓 `192.168.1.3:9221/pve`。

```yaml
- job_name: 'pve-Node1'
  metrics_path: /pve
  params:
    target: ['192.168.2.1']
  static_configs:
    - targets: ['192.168.1.3:9221']
```

如果還有其它更複雜的情況，請參考該 Exporter 的範例教學，或是 Prometheus 的 [Configuration Docs](https://prometheus.io/docs/prometheus/latest/configuration/configuration/)。

在修改完 `prometheus.yml` 後，請重啓服務：`sudo make restart`。

## 正式使用 Prometheus 和 Grafana

### 新增 Grafana Dashboard

對於自定義 Dashboard，這部分內容太多，恕我不能詳寫；而基礎內容，網路上又出現太多，恕我不贅述。此處列出一些：
- [Grafana 操作手冊](https://hackmd.io/@KenLiang/grafana-tutorials)：基本上對於如何創建 Dashboard 描述的很詳細，只是他使用的 Data Source 是 MySQL，因此他輸入的查詢語法會和我們預期使用的不一樣。
- [Grafana 新增圖表](https://hackmd.io/@xsggt/rJgE7iSRD)：基本上對於設定 Dashboard 描述的也很詳細，尤其是在設定各種細節，包含顏色、顯示效果等，然而他使用 InfluxDB，因此查詢語法也和我們用的不同。

而許多開發者都會爲某些特定 Exporter 或特定監控場景（例如監控某個資料庫）特製 Dashboard，並且把它開源到網路上，你可以在 [Grafana Dashboards 官網](https://grafana.com/grafana/dashboards/) 下載並且在 Grafana 中引入他。

### 新增 Alerting Rule

#### Alert 的基本設定（1. Enter alert rule name & 5. Add annotations）

你可以設定 Alert 的名字，和他觸發時候的通知內容，以及他的註解。

#### Alert 的觸發（2. Define query and alert condition）

在點擊左上角三條線選單之後，可以看到有一項是 Alerting，其中又有 Alert rules 的細項，點擊後進入 Alert rules 頁面。

在該界面，我們可以點擊 New alert rule 來新增警報規則，基本上每一條規則都由兩種元素定義：
1. Query：由 Data Source 下查詢語句得來，例如從 Prometheus 下 PromQL 得來；你會給這個 Query 的結果一個名字，例如 A、B，以及 C，此 alert rule 共 3 個 Query。
2. Expression：由每個 Expression 去進行單個計算，例如我們可以定義一個 D，其值爲 A + B；再定義一個 E，其值爲 min(C, D)。

其中一種特別的 Expression 叫做 Threshold，他是一個簡單的布林判斷，例如定義 X，值爲 E > 100；但重點是你可以選定一個 Threshold 爲該 alert rule 的觸發條件：意思是經過次次查詢和層層運算，我們得到了 A、B、C，再得到了 D、E、最後得到了 X，我們用 X 是否爲 1 來決定要不要觸發這個 alert。

#### Alert 的評估（3. Set evaluation behavior）

基本上我們需要去創建 Folder 和 Evaluation Group 來歸納 Alert。其中 Folder 沒什麼好說的，基本上就是類似文件分類。
而 Evaluation Group 決定了，你的這個 Alert Rule 多久會被檢查一次，例如如果你選擇 10m，那麼它就會固定 10 分鐘檢查一次你上面的觸發條件。
在這一大項的最後一點還定義了 Pending period，就是說這個情況要持續多久，才要被通報，例如如果你選擇 5m，那麼如果它只發生了 4 分鐘就結束了，那麼它一樣不會被觸發；而如果你選擇 None，就代表一旦條件成立，馬上觸發。

#### Alert 的處理（4. Configure labels and notifications）

基本上你可以爲你的 Alert 增加一些標籤（Label），來方便你搜索、分類、或甚至無視某部分的 Alert，這部分不細談。
第二個設定才是比較重要，就是選擇通知，基本上有兩種模式：
1. 直接選擇要通知誰，你可以創建一個 Contact Point，可以粗淺理解成一個 Mailing List，然後你選擇通知某個 Contact Point 即可。
2. 採用 Notification Policy，基本上 Notification Policies 是個樹狀結構，由 Alert 的 Labels 進行分流，某個 Policy 會有對應的 Contact Point 和 Label Match 的條件，要滿足 Label Match 的條件，他才會觸發這個 Policy 以及嘗試觸發他的 Child Policy。也因此 Notification Policy 可以做到系統化、精緻的 Alert 通知分流。

## 備份、轉移、刪庫

所有的資料都存放在 `prometheus-data` 和 `grafana-data`，只要把這兩個目錄轉移走，再另一臺主機再 clone 一次本 REPO，再將 COPY 過來的目錄放入本 REPO clone 後的目錄，就可以轉移成功了。不過爲了避免資料受損，請確保轉移前有安全的關閉這兩個服務：`sudo make down`。

同理，刪除 `prometheus-data` 和 `grafana-data` 就可以刪除所有資料，再恢復 `prometheus.yml`，基本上就徹底還原了。

## 未來可以做的東西

- Kubernetes：更好的 HA、負載平衡，以及其它 Features
- Prometheus 的 Authentication
- Prometheus 和 Grafana 的 TLS
- 自定義 Exporters：爲自己的重要服務撰寫特定功能的 Exporters，例如撰寫一個 Web Server 各個 Status Code 累計次數的 Exporters，或是網路 RTT 的測量。
- Exporters 和 Prometheus 之間的安全網路：例如使用 VPN、VLAN。
- Grafana IaC：基本上 Grafana 的 Dashboard 都是由 JSON 保存的，因此如果可以動態產生 JSON，我們是可以動態產生 Dashboard 的。
- Data Filter：寫個 Web，能夠在被訪問的時候，去蒐集對應 Exporter 的資料，並且通過白名單 filter 掉無用資訊，以減少資料量。
- Grafana RBAC：利用 RBAC 來限制每位使用者，因此可以開放給各個系所或單位查看與他們相關的資訊、警告。
- AIOps：將 Prometheus 搜集到的資料餵給 AI，來分析異常和判斷增長。

## Also See

- [GitHub REPO - Metrics-Monitor-Docker-Template](https://github.com/Rin0913/Metrics-Monitor-Docker-Template)
- [Kubernetes 教學 第三篇（Persistent Volume 篇）- 建設 Prometheus 和 Grafana](https://sandb0x.tw/a/Kubernetes_%E6%95%99%E5%AD%B8_%E7%AC%AC%E4%B8%89%E7%AF%87%EF%BC%88Persistent_Volume_%E7%AF%87%EF%BC%89)
