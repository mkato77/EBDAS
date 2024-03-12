# EBDAS

第13回 科学の甲子園の事前公開競技「バルーンフェスタ in つくば」で使用する、気球の各種データ測定・記録用Pythonソフトウェア

![image](https://github.com/mkato77/EBDAS/assets/80267487/6e28b832-e8f9-492c-933c-9024775d6a21)

(画像は開発中のものです)

## 特徴
- 計測キットとの通信
- 計測データの取得
- 測定データの表形式表示
- 測定データのグラフ表示
- 測定データの記録
- 測定データのSQLite, CSV形式保存
- 機体管理
- Fletを用いたMaterial DesignのUI

## おすすめ: [EBDASビューアー](https://github.com/mkato77/EBDAS-Viewer)
"EBDAS" で記録したデータを表示するためのWebアプリケーションです。各記録を横断的に比較することができ、自動でグラフを描画します。

- アクセス: [https://ebdas-viewer.pages.dev/](https://ebdas-viewer.pages.dev/)
- GitHubレポジトリ: [https://github.com/mkato77/EBDAS-Viewer](https://github.com/mkato77/EBDAS-Viewer)


## ビルド済みWindowsソフトウェア(.exe)
ビルド済みソフトウェア(.exe)は[リリース](https://github.com/mkato77/EBDAS/releases)で使用できます。ZIPファイルを解凍してご利用ください。
Linux版, Mac版につきましては、動作確認をしておりません。

## 使用方法
### ソフトを起動
.exeまたは.pyを実行してください。

### ファイル>ディレクトリ選択から、データの保存に用いるフォルダを選択
専用の新しいフォルダを用意してください。

> [!IMPORTANT]
> フォルダを選択後、ソフトウェアが上手く動作しない場合があります。これはバグですが、まだ修正されていません。ソフトウェアを再起動すると直りますので、暫定的にそうしてください。

### 接続先を設定
ESP32S3のURLを設定してください。(詳細は、事前公開競技の資料を参照してください。)

> [!NOTE]
> ESP32S3にホスト名が設定されていない場合(初期のプログラム)、mDNSでアクセスできません。 `WiFi.setHostname` を用いて、ホスト名を設定してください。[参照記事](https://qiita.com/Kurogara/items/059f13ef4fc0c0f40cd9)

### ESP32S3側のコードを修正
EBDASでデータを処理できるように、ESP32S3から送信するデータの形式を変更します。

事前公開競技資料別紙にあるコードを掲載してよいか不明であるため、修正した箇所のみ提示します。

#### HTTPヘッダ
```
void handleRoot() {
  server.sendContent("HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\n");
  // server.sendContent("<html><body><tt>");
```

#### 1行目のデータ
```
  server.sendContent("time[sec], temperature[degC], pressure[hPa], humidity[%], altitude[m], a0, a1, a2, a3\n");
```

#### 2行目以降のデータ
```
      sprintf(string0, "%.2f, %.1f, %.1f, %.1f, %.1f, %.1f, %.1f, %.1f, %.1f\n",
        ftime, temperature, pressure/100.f, humidity, altitude,
        temperature0, temperature1, temperature2, temperature3);
```

### 接続開始ボタンを押す
ESP32S3との接続が開始します。

> [!CAUTION]
> 測定データの記録時は、「リアルタイム描画」をOFFにしてから接続開始してください。matplotlibの描画処理が複数回行われることで、動作が不安定になり、受信に遅延が生じる可能性があるためです。

### 「記録する」タブで測定データを記録
「ヒートガンON」「ヒートガンOFF」「着地」のタイミングに合わせてボタンを押すことで、データが記録されます。

保存したデータは、[EBDASビューアー](https://github.com/mkato77/EBDAS-Viewer)で表示できます。

## 開発
### 要件
- Python 3.7 またはそれ以降
- pip
- flet
- matplotlib
- numpy
- requests
- pyperclip
- pyinstaller
- japanize_matplotlib

必要なパッケージをインストールするには、以下のコマンドを実行してください：

```
pip install -r requirements.txt
```

### 使用方法
#### アプリの実行
`flet` コマンドを用いてアプリを実行します：

```
flet run [app_directory] (アプリの実行)
```

または、Pythonコードを直接実行します。

```
python main.py
```

#### 模擬ローカルウェブサーバを使う
ESP32S3からのデータ送信を模したローカルウェブサーバを使用することができます。

```
python server.py
```

を実行し `http://localhost:8756/` にアクセスします。

アプリ内の 編集>測定キット接続設定 から `http://localhost:8756` を設定することで、ソフトウェアの動作を確認することができます。

デフォルトのポート番号は 8756 です。ポート番号を変更したい場合は `server.py` ファイルで変更してください。

## ライセンス
本ソフトウェアは競技終了まで非公開とします。貢献者(チームメンバー、顧問教員、その他)には、競技終了まで守秘義務があります。
このレポジトリは、競技終了後に公開します。

## 補足
このソフトウェアは、限られた準備期間の中で、試行錯誤を繰り返しながら製作されました。そのため、一部のコードが見づらい場合があります。ご了承ください。
