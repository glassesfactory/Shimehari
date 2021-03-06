Shimehari
=======

Shimehari is moderate framework for Python.

http://shimehari.hageee.net

inspired from Flask:: http://flask.pocoo.org

master: [![Master Build Status](https://secure.travis-ci.org/glassesfactory/Shimehari.png?branch=master)](http://travis-ci.org/glassesfactory/Shimehari)
namashibori: [![Namashibori Build Status](https://secure.travis-ci.org/glassesfactory/Shimehari.png?branch=namashibori)](http://travis-ci.org/glassesfactory/Shimehari)

What is Shimehari
---

Shimehari (しめはり)は Python 製 Web フレームワークです。

フルスタックだとゴリゴリすぎるけどマイクロフレームワークだと  
ちょっと規模が大きいかな…
という時に活躍したいモデレートフレームワークを自称しています。

wiki はこれから整備していきます...

### Shimehari がやってくれること

Shimehari はルーティングとコントローラーの枠組だけ提供します。  
Form ヘルパーや ORM 、Scaffold といった高度な機能は提供しません。


How to Install
---

from pypi
```
$ pip install Shimehari
```

or github
```
$ git clone git@github.com:glassesfactory/Shimehari.git
$ python setup.py install
```
  
  
How to use
---

アプリケーションを作成したいディレクトリで以下のコマンドを実行するだけです。

```
$ cd your_proj_directory
$ shimehari create your_app_name
$ shimehari drink
$ * Shimehari GKGK!
$ * Running on http://127.0.0.1:5959/
```

It works! and drink!
  
  
RESTful Routing  & Controller
---

Shimehari は RESTful なルーティングを推奨しています。
  
### Routing
Router に対し、Resource としてコントローラークラスを追加するだけで自動的に RESTful なアクションがルーティングされます。

```
appRoutes = Router([
	Resource(IndexController, root=True),
	Resource(FooController),
	Resource(BarController)
    ])
```

現在のルーティング状況は以下のコマンドを叩くことで確認することが出来ます。

```
$ shimehari routes
$ Your Shimehari App Current Routing.

Methods       |URL                          |Action
----------------------------------------------------------------------
GET            /                             [action => index, controller => IndexController]
POST,GET       /<int:id>                     [action => show, controller => IndexController]
```
  
### Controller

shimehari.controllers.ApplicationController を継承することで  
Resource() を使ってルーティングを拾い上げることが出来ます。
コントローラーで実装されていない RESTful アクションは自動的にルーティングの対象外となります。
  
```
from shimehari import renderTemplate
from shimehari.controllers import ApplicationController
class ExampleController(ApplicationController):
	def index(self, *args, **kwargs):
		return renderTemplate('index.html')
```

ApplicationController を自前で継承後、必要なアクションを定義するだけでなく、  
以下のコマンドを叩くことで一通りアクションが定義済みのコントローラーを生成することが出来ます。

```
$ shimehari generate controller Example
```


貢献
------------

1. フォークします
2. ブランチを作ります (`git checkout -b my_markup`)
3. 変更を行います (`git commit -am "Added Snarkdown"`)
4. ブランチにプッシュします (`git push origin my_markup`)
5.  [Pull Request] [1] を開きます
6. 〆張鶴楽しみ、待つ

  

and more...
---
より詳しい使い方や、その他の API については [Shimehari 公式サイト](http://shimehari.hageee.net) を参照してください。