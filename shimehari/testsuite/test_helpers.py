#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os
import shimehari
from logging import StreamHandler
from StringIO import StringIO
from shimehari.helpers import flash, getFlashedMessage
from shimehari.testsuite import ShimehariTestCase, catchWarnings, catchStdErr
from shimehari.configuration import ConfigManager, Config
from werkzeug.routing import Rule
from werkzeug.http import parse_cache_control_header, parse_options_header

testConfig = Config('development', {'AUTO_SETUP': False, 'SERVER_NAME': 'localhost', 'PREFERRED_URL_SCHEME': 'https', 'APP_DIRECTORY': 'testApp'})


def hasEncoding(name):
    try:
        import codecs
        codecs.lookup(name)
        return True
    except LookupError:
        return False


class FlashTestCase(ShimehariTestCase):
    def testFlash(self):
        app = shimehari.Shimehari(__name__)

        def index(*args, **kwargs):
            flash('ninja')
            return 'hooo'

        def getFlash(*args, **kwargs):
            msg = getFlashedMessage()
            if len(msg) > 0:
                msg = msg[0]
            else:
                msg = None
            return msg

        app.router = shimehari.Router([
            Rule('/', endpoint='index', methods=['GET']),
            Rule('/getflash', endpoint='getFlash', methods=['GET'])
        ])

        app.controllers['index'] = index
        app.controllers['getFlash'] = getFlash

        c = app.testClient()
        c.get('/')
        rv = c.get('/getflash')
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.data, 'ninja')

        rv = c.get('/getflash')
        # self.assert_(rv is None)

    def testFlashCategory(self):
        app = shimehari.Shimehari(__name__)

        def index(*args, **kwargs):
            flash('ninja', 'shinobi')
            flash('kagetora', 'sake')
            return 'flash'

        def getFlash(*args, **kwargs):
            msg = getFlashedMessage(False, ['sake'])[0]
            return msg

        app.router = shimehari.Router([
            Rule('/', endpoint='index', methods=['GET']),
            Rule('/getflash', endpoint='getFlash', methods=['GET'])
        ])

        app.controllers['index'] = index
        app.controllers['getFlash'] = getFlash

        c = app.testClient()
        c.get('/')
        rv = c.get('/getflash')
        self.assertEqual(rv.status_code, 200)
        self.assertNotEqual(rv.data, 'ninja')
        self.assertEqual(rv.data, 'kagetora')


class JSONTestCase(ShimehariTestCase):
    def testJSONBadRequests(self):
        ConfigManager.addConfig(testConfig)
        app = shimehari.Shimehari(__name__)

        def returnJSON(*args, **kwargs):
            return unicode(shimehari.request.json)
        app.router = shimehari.Router([Rule('/json', endpoint='returnJSON', methods=['POST'])])
        app.controllers['returnJSON'] = returnJSON
        c = app.testClient()
        rv = c.post('/json', data='malformed', content_type='application/json')
        self.assertEqual(rv.status_code, 400)

    def testJSONBadRequestsContentType(self):
        ConfigManager.addConfig(testConfig)
        app = shimehari.Shimehari(__name__)

        def returnJSON(*args, **kwargs):
            return unicode(shimehari.request.json)
        app.router = shimehari.Router([Rule('/json', endpoint='returnJSON', methods=['POST'])])
        app.controllers['returnJSON'] = returnJSON
        c = app.testClient()
        rv = c.post('/json', data='malformed', content_type='application/json')
        self.assertEqual(rv.status_code, 400)
        self.assertEqual(rv.mimetype, 'application/json')
        self.assert_('description' in shimehari.json.loads(rv.data))
        self.assert_('<p>' not in shimehari.json.loads(rv.data)['description'])

    def jsonBodyEncoding(self):
        ConfigManager.addConfig(testConfig)
        app = shimehari.Shimehari(__name__)

        app.testing = True

        def returnJSON(*args, **kwargs):
            return shimehari.request.json
        app.router = shimehari.Router([Rule('/json', endpoint='returnJSON', methods=['GET'])])
        app.controllers['returnJSON'] = returnJSON
        c = app.testClient()
        resp = c.get('/', data=u"はひ".encode('iso-8859-15'), content_type='application/json; charset=iso-8859-15')
        self.assertEqual(resp.data, u'はひ'.encode('utf-8'))

    def testJsoniFy(self):
        d = dict(a=23, b=42, c=[1, 2, 3])
        ConfigManager.addConfig(testConfig)
        app = shimehari.Shimehari(__name__)

        #hum
        def returnKwargs():
            return shimehari.jsonify(**d)

        def returnDict():
            return shimehari.jsonify(d)

        app.router = shimehari.Router([
            Rule('/kw', endpoint='returnKwargs', methods=['GET']),
            Rule('/dict', endpoint='returnDict', methods=['GET'])
        ])
        app.controllers['returnKwargs'] = returnKwargs
        app.controllers['returnDict'] = returnDict

        c = app.testClient()
        for url in '/kw', '/dict':
            rv = c.get(url)
            self.assertEqual(rv.mimetype, 'application/json')
            self.assertEqual(shimehari.json.loads(rv.data), d)

    def testJSONAttr(self):
        ConfigManager.addConfig(testConfig)
        app = shimehari.Shimehari(__name__)

        def returnJSON(*args, **kwargs):
            return unicode(shimehari.request.json['a'] + shimehari.request.json['b'])
        app.router = shimehari.Router([Rule('/add', endpoint='returnJSON', methods=['POST'])])
        app.controllers['returnJSON'] = returnJSON

        c = app.testClient()
        rv = c.post('/add', data=shimehari.json.dumps({'a': 1, 'b': 2}), content_type='application/json')
        self.assertEqual(rv.data, '3')

    def testTemplateEscaping(self):
        ConfigManager.addConfig(testConfig)
        app = shimehari.Shimehari(__name__)
        app.setupTemplater()
        render = shimehari.renderTemplateString
        with app.testRequestContext():
            rv = render('{{"</script>"|tojson|safe }}')
            self.assertEqual(rv, '"</script>"')
            rv = render('{{"<\0/script>"|tojson|safe }}')
            self.assertEqual(rv, '"<\\u0000/script>"')

    def testModifiedURLEncoding(self):
        class ModifiedRequest(shimehari.Request):
            url_charset = 'euc-jp'
        app = shimehari.Shimehari(__name__)
        app.requestClass = ModifiedRequest
        app.router.charset = 'euc-jp'

        def index():
            return shimehari.request.args['foo']

        app.router = shimehari.Router([Rule('/', endpoint='index', methods=['GET'])])
        app.controllers['index'] = index

        rv = app.testClient().get(u'/?foo=ほげほげ'.encode('euc-jp'))
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.data, u'ほげほげ'.encode('utf-8'))

    if not hasEncoding('euc-jp'):
        testModifiedURLEncoding = None


class SendFileTestCase(ShimehariTestCase):
    def testSendFileRegular(self):
        app = shimehari.Shimehari(__name__)
        with app.testRequestContext():
            rv = shimehari.sendFile(os.path.join(app.rootPath, 'static/index.html'))
            self.assert_(rv.direct_passthrough)
            self.assertEqual(rv.mimetype, 'text/html')
            with app.openFile('static/index.html') as f:
                self.assertEqual(rv.data, f.read())

    def testSendFileXSendFile(self):
        app = shimehari.Shimehari(__name__)
        app.useXSendFile = True
        with app.testRequestContext():
            rv = shimehari.sendFile(os.path.join(app.rootPath, 'static/index.html'))
            self.assert_(rv.direct_passthrough)
            self.assert_('x-sendfile' in rv.headers)
            self.assertEqual(rv.headers['x-sendfile'], os.path.join(app.rootPath, 'static/index.html'))
            self.assertEqual(rv.mimetype, 'text/html')

    def testSendFileObject(self):
        app = shimehari.Shimehari(__name__)
        with catchWarnings() as captured:
            with app.testRequestContext():
                f = open(os.path.join(app.rootPath, 'static/index.html'))
                rv = shimehari.sendFile(f)
                with app.openFile('static/index.html') as f:
                    self.assertEqual(rv.data, f.read())
                self.assertEqual(rv.mimetype, 'text/html')
            self.assertEqual(len(captured), 2)

        app.useXSendFile = True
        with catchWarnings() as captured:
            with app.testRequestContext():
                f = open(os.path.join(app.rootPath, 'static/index.html'))
                rv = shimehari.sendFile(f)
                self.assertEqual(rv.mimetype, 'text/html')
                self.assert_('x-sendfile' in rv.headers)
                self.assertEqual(rv.headers['x-sendfile'],
                    os.path.join(app.rootPath, 'static/index.html'))
            self.assertEqual(len(captured), 2)

        app.useXSendFile = False
        with app.testRequestContext():
            with catchWarnings() as captured:
                f = StringIO('Test')
                rv = shimehari.sendFile(f)
                self.assertEqual(rv.data, 'Test')
                self.assertEqual(rv.mimetype, 'application/octet-stream')

            self.assertEqual(len(captured), 1)
            with catchWarnings() as captured:
                f = StringIO('Test')
                rv = shimehari.sendFile(f, mimetype='text/plain')
                self.assertEqual(rv.data, 'Test')
                self.assertEqual(rv.mimetype, 'text/plain')
            self.assertEqual(len(captured), 1)

        app.useXSendFile = True
        with catchWarnings() as captured:
            with app.testRequestContext():
                f = StringIO('Test')
                rv = shimehari.sendFile(f)
                self.assert_('x-sendfile' not in rv.headers)
            self.assertEqual(len(captured), 1)

    def testAttachment(self):
        app = shimehari.Shimehari(__name__)
        with catchWarnings() as captured:
            with app.testRequestContext():
                f = open(os.path.join(app.rootPath, 'static/index.html'))
                rv = shimehari.sendFile(f, asAttachment=True)
                value, options = parse_options_header(rv.headers['Content-Disposition'])
                self.assertEqual(value, 'attachment')
            self.assertEqual(len(captured), 2)

        with app.testRequestContext():
            self.assertEqual(options['filename'], 'index.html')
            rv = shimehari.sendFile(os.path.join(app.rootPath, 'static/index.html'), asAttachment=True)
            value, options = parse_options_header(rv.headers['Content-Disposition'])
            self.assertEqual(value, 'attachment')
            self.assertEqual(options['filename'], 'index.html')

        with app.testRequestContext():
            rv = shimehari.sendFile(StringIO('Test'), asAttachment=True,
                                    attachmentFilename='index.txt', addEtags=True)
            self.assertEqual(rv.mimetype, 'text/plain')
            value, options = parse_options_header(rv.headers['Content-Disposition'])
            self.assertEqual(value, 'attachment')
            self.assertEqual(options['filename'], 'index.txt')

    def testStaticFile(self):
        ConfigManager.removeConfig('development')
        ConfigManager.addConfig(testConfig)
        app = shimehari.Shimehari(__name__)
        app.setStaticFolder('static')
        with app.testRequestContext():
            rv = app.sendStaticFile('index.html')
            cc = parse_cache_control_header(rv.headers['Cache-Control'])
            self.assertEqual(cc.max_age, 12 * 60 * 60)
            rv = shimehari.sendFile(os.path.join(app.rootPath, 'static/index.html'))
            cc = parse_cache_control_header(rv.headers['Cache-Control'])
            self.assertEqual(cc.max_age, 12 * 60 * 60)
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 3600
        with app.testRequestContext():
            rv = app.sendStaticFile('index.html')
            cc = parse_cache_control_header(rv.headers['Cache-Control'])
            self.assertEqual(cc.max_age, 3600)
            rv = shimehari.sendFile(os.path.join(app.rootPath, 'static/index.html'))
            cc = parse_cache_control_header(rv.headers['Cache-Control'])
            self.assertEqual(cc.max_age, 3600)

        class StaticFileApp(shimehari.Shimehari):
            def getSendFileMaxAge(self, filename):
                return 10
        app = StaticFileApp(__name__)
        app.setStaticFolder('static')
        with app.testRequestContext():
            rv = app.sendStaticFile('index.html')
            cc = parse_cache_control_header(rv.headers['Cache-Control'])
            self.assertEqual(cc.max_age, 10)
            rv = shimehari.sendFile(os.path.join(app.rootPath, 'static/index.html'))
            cc = parse_cache_control_header(rv.headers['Cache-Control'])
            self.assertEqual(cc.max_age, 10)


class LoggingTestCase(ShimehariTestCase):
    def testLoggerCache(self):
        app = shimehari.Shimehari(__name__)
        logger1 = app.logger
        self.assert_(app.logger is logger1)
        self.assertEqual(logger1.name, __name__)
        app.loggerName = __name__ + 'aaaa'
        self.assert_(app.logger is not logger1)

    def testDebugLog(self):
        app = shimehari.Shimehari(__name__)
        app.debug = True

        def index():
            app.logger.warning('the standard library is dead')
            app.logger.debug('this is a debug statement')
            return ''

        def exc():
            1 / 0

        app.router = shimehari.Router([
            Rule('/', endpoint='index', methods=['GET']),
            Rule('/exc', endpoint='exc', methods=['GET']),
        ])
        app.controllers['index'] = index
        app.controllers['exc'] = exc
        with app.testClient() as c:
            with catchStdErr() as err:
                c.get('/')
                out = err.getvalue()
                self.assert_('WARNING' not in out)
                self.assert_(os.path.basename(__file__.rsplit('.', 1)[0] + '.py') not in out)
                self.assert_('the standard library is dead' not in out)
                self.assert_('this is a debug statement' not in out)
            with catchStdErr() as err:
                try:
                    c.get('/exc')
                except ZeroDivisionError:
                    pass
                else:
                    self.assert_(False, 'debug log ate the exception')

    def testDebugLogOverride(self):
        app = shimehari.Shimehari(__name__)
        app.debug = True
        app.loggerName = 'shimehari_tests/testaaa'
        app.logger.level = 10
        self.assertEqual(app.logger.level, 10)

    def testExceptionLogging(self):
        out = StringIO()
        app = shimehari.Shimehari(__name__)
        app.loggerName = 'shimehariaaa'
        app.logger.addHandler(StreamHandler(out))

        def index():
            1 / 0

        app.router = shimehari.Router([Rule('/', endpoint='index', methods=['GET'])])
        app.controllers['index'] = index

        rv = app.testClient().get('/')
        self.assertEqual(rv.status_code, 500)
        self.assert_('Internal Server Error' in rv.data)

        err = out.getvalue()
        self.assert_('ZeroDivisionError: ' in err)

    def testProcessorExceptions(self):
        app = shimehari.Shimehari(__name__)

        @app.beforeRequest
        def beforeReq():
            if trigger == 'before':
                1 / 0

        @app.afterRequest
        def afterRequest(response):
            if trigger == 'after':
                1 / 0
            return response

        def index():
            return 'Foo'
        app.router = shimehari.Router([Rule('/', endpoint='index', methods=['GET'])])
        app.controllers['index'] = index

        @app.errorHandler(500)
        def internalServerError(e):
            return 'Hello Server Error', 500

        for trigger in 'before', 'after':
            rv = app.testClient().get('/')
            self.assertEqual(rv.status_code, 500)
            self.assertEqual(rv.data, 'Hello Server Error')

    def testURLForWithAnchro(self):
        app = shimehari.Shimehari(__name__)

        def index():
            return '42'
        app.router = shimehari.Router([Rule('/', endpoint='index', methods=['GET'])])
        app.controllers['index'] = index

        with app.testRequestContext():
            self.assertEqual(shimehari.urlFor('index', _anchor='x y'), '/#x%20y')


class NoImportsTestCase(ShimehariTestCase):
    def testNameWithImportError(self):
        try:
            shimehari.Shimehari('importerror')
        except NotImplementedError:
            self.fail('Shimehari(importaaaa')


def suite():
    suite = unittest.TestSuite()
    if shimehari.jsonAvailable:
        suite.addTest(unittest.makeSuite(JSONTestCase))
    suite.addTest(unittest.makeSuite(SendFileTestCase))
    suite.addTest(unittest.makeSuite(LoggingTestCase))
    suite.addTest(unittest.makeSuite(NoImportsTestCase))
    return suite
