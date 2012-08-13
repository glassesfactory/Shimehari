Shimehari
=======

Python Middle Framework for web.

forked from Flask:: http://flask.pocoo.org

What is Shimehari
---

Shimehari (しめはり)は Python 製 Web フレームワークです。

フルスタックだとゴリゴリすぎるけどマイクロフレームワークだと  
ちょっと規模が大きいかな…
という時に活躍したいミドルフレームワークを自称しています。

wiki はこれから整備していきます...

### Shimehari がやってくれること

Shimehari はルーティングとコントローラーの枠組だけ提供します。  
Form ヘルパーや ORM 、Scaffold といった高度な機能は提供しません。


How to Install
---

```
$ git clone git@github.com:glassesfactory/Shimehari.git
$ python setup.py install
```
  
  
How to use
---

アプリケーションを作成したいディレクトリで以下のコマンドを実行するだけです。

```
$ cd your_proj_directory
$ shimehari-sakagura.py create your_app_name
$ python ochoko.py drink
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
appRoutes = Router(
	Resource(IndexController, root=True),
	Resource(FooController),
	Resource(BarController)
)
```

現在のルーティング状況は以下のコマンドを叩くことで確認することが出来ます。

```
$ python ochoko.py routes
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
from shimehari.controllers import ApplicationController
class ExampleController(ApplicationController):
	def index(self, *args, **kwargs):
		return render_template('index.html')
```

ApplicationController を自前で継承後、必要なアクションを定義するだけでなく、  
以下のコマンドを叩くことで一通りアクションが定義済みのコントローラーを生成することが出来ます。

```
$ python ochoko.py generate Example
```
  
    
and more...
---
より詳しい使い方や、その他の API については [wiki](https://github.com/glassesfactory/Shimehari/wiki) を参照してください。
*※整備中*