0.1.8
=======
:release date: 2012-10-12

Feature
----------
* アラートや成功表示など、リクエストごとに揮発してくれる flash を追加しました。
* static ディレクトリを複数設定できるようにしました。

Bugs fixed
----------
* SecureCookie 周りの細かいバグを取りました。
* リファクタリングや import を整理


0.1.7
=======
:release date: 2012-09-28
 
Bugs fixed
----------
* リソースのネストがうまく行かなくなってしまっていた問題を修正。

0.1.6
=======
:release date: 2012-09-26
 
Feature
----------
* generate command でファイル名にサブディレクトリが含まれていた場合対応するようにしました。
* 各コマンドの usage を追加。
 
 
Bugs fixed
----------
* 静的ファイルの扱いがうまくいっていなかった問題を修正。
* SimpleCacheStore で保持期限が切れたキャッシュが消去されない問題を解決。
* pep8 に最適化
 


0.1.5
=======
:release date: 2012-09-19

Feature
----------
* キャッシュ機能を追加。対応しているキャッシュストアはメモリ、Memcached、FileSystem、Redis です。
* ConfigManager.getConfig した際、environ の指定がなければ現在の environ を取得し返すように。
* コントローラーディレクトリ内でサブディレクトリが作られていた場合、ディレクトリ構造を URL に反映するように。 config['CONTROLLER_AUTO_NAMESPACE'] の値を変更することで有効/無効を切り替えられます。
* Resource に prefix を追加。prefix が指定されていた場合、 ルート直下(/) に必ず指定した prefix が指定されるようになります。
* routing.Group を追加。Group に追加された Resource または Rule に対し任意の URL ディレクトリ階層を追加します。
* Resource.addRule を追加。
* shimehari checkconfig コマンドを追加。現在有効なコンフィグをコンソール上で確認できます。


Bugs fixed
----------
* shared モジュール内、メッソド名がおかしかったものを修正。
* 0.1.4 までに追加された機能、修正されたものに対しテストが通らなくなっていた問題を修正。

0.1.4
=======
:release date: 2012-08-29

*【重要】コマンドラインツールを変更しました。*

Feature
----------
* shimehari-sakagura.py, ochoko.py から shimehari コマンドのみに統一。
* テンプレートエンジンのセットアップタイミングを変更。
* カスタムロガー を app 付属からスタンドアロンで使えるように
* logging を外部ログファイルとして出力できるようにオプションを追加。

Bugs fixed
----------
* templater にオプションが渡せなかった問題を修正。



0.1.3
=======
:release date: 2012-08-21

* ソースコード内のヒントを修正

Bugs fixed
----------
* jinja2 templater にアプリケーションディレクトリの情報が渡せなかったバグを修正。


0.1.2
=======
:release date: 2012-08-20

細かなバグ修正

0.1.01
=======
:release date: 2012-08-20

Bugs fixed
----------
* セットアップ時に出る警告などを出ないように修正。


0.1
=======
:release date: 2012-08-19

とりあえずリリース

