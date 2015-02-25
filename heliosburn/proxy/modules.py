import io
from zope.interface import implements
from zope.interface import Interface
from twisted.plugin import IPlugin
from twisted.plugin import getPlugins
from twisted.python import log


"""
Simple Interface to handling proxy requests and responses via class instances.
To use, make a new class that inherits ProxyModuleBase. Each context
represents a step in the proxy request or client response process.

"""


class IModule(Interface):
    """
    Module interface defined for proxy modules.

    .run() is called in every (defined) context.

    Currently implemented contexts:
        'request'
        'response'
    """

    def get_name(self):
        """
        Returns the unique name of the module

        @rtype: C{string}
        """

        return self.name

    def onRequest(self, **keywords):
        """
        Called by .run() when instantiated with a run_context that includes
        'request'.
        """

    def onStatus(self, **keywords):
        """
        Called by .run() when instantiated with a run_context that includes
        'status'.
        """

    def onResponse(self, **keywords):
        """
        Called by .run() when instantiated with a run_context that includes
        'response'.
        """

    def reset(self, **keywords):
        """
        If the module maintains state, this method is called to reset
        the current state of the module

        """

    def run(self, **keywords):
        """
        Called by run_modules() after a module has been loaded (instantiated).
        if a given (predefined) context is listed in 'run_contexts', the
        respective method is called.
        """


class AbstractModule(object):
    implements(IPlugin, IModule)

    """
    Base class used to implement a twisted plugin based IModule interface.

    .run() is called in every (defined) context.

    Currently implemented contexts:
        'request'
        'response'
    """

    def __init__(self, run_contexts=[], context=None,
                 request_object=None):
        """
        Initialization of a proxy module instance
        """

        self.name = "Interface Module"
        self.log = log
        self.run_contexts = run_contexts
        self.context = context
        self.request_object = request_object

    def get_name(self):
        """
        Returns the name of the module
        """

        return self.name

    def onRequest(self, **keywords):
        """
        Called by .run() when instantiated with a run_context that includes
        'request'.
        """
        self.log.msg("Request: %s" % keywords)

    def onStatus(self, **keywords):
        """
        Called by .run() when instantiated with a run_context that includes
        'status'.
        """
        self.log.msg("Status: %s" % keywords)

    def onResponse(self, **keywords):
        """
        Called by .run() when instantiated with a run_context that includes
        'response'.
        """
        self.log.msg("Response: %s" % keywords)

    def reset(self, **keywords):
        """
        If the module maintains state, this method is called to reset
        the current state of the module
        """
        self.log.msg("Response: %s" % keywords)

    def run(self, **keywords):
        """
        Called by run_modules() after a module has been loaded (instantiated).
        if a given (predefined) context is listed in 'run_contexts', the
        respective method is called.
        """
        options = {
            'request': self.onRequest,
            'status': self.onStatus,
            'response': self.onResponse,
        }
        if self.context in self.run_contexts:
            options[self.context](**keywords)
        else:
            self.log.msg("not my turn yet")

    def getProtocol(self):
        if self.context in ['request', 'response']:
            return self.request_object.clientproto
        else:
            raise Exception('Invalid context')

    def setProtocol(self, protocol):
        if self.context in ['request', 'response']:
            self.request_object.clientproto = protocol
        else:
            raise Exception('Invalid context')

    def getMethod(self):
        if self.context in ['request', 'response']:
            return self.request_object.method
        else:
            raise Exception('Invalid context')

    def setMethod(self, method):
        if self.context in ['request']:
            self.request_object.method = method
        else:
            raise Exception('Invalid context')

    def getURI(self):
        if self.context in ['request', 'response']:
            return self.request_object.uri
        else:
            raise Exception('Invalid context')

    def setURI(self, uri):
        if self.context in ['request']:
            self.request_object.uri = uri
        else:
            raise Exception('Invalid context')

    def getStatusCode(self):
        if self.context in ['response']:
            return self.request_object.code
        else:
            raise Exception('Invalid context')

    def setStatusCode(self, status_code):
        if self.context in ['response']:
            self.request_object.code = status_code
        else:
            raise Exception('Invalid context')

    def getStatusDescription(self):
        if self.context in ['response']:
            return self.request_object.code_message
        else:
            raise Exception('Invalid context')

    def setStatusDescription(self, status_description):
        if self.context in ['response']:
            self.request_object.code_message = status_description
        else:
            raise Exception('Invalid context')

    def getAllHeaders(self):
        if self.context == 'request':
            return self.request_object.requestHeaders.getAllRawHeaders()
        elif self.context == 'response':
            return self.request_object.responseHeaders.getAllRawHeaders()
        else:
            raise Exception('Invalid context')

    def hasHeader(self, name):
        if self.context == 'request':
            return self.request_object.requestHeaders.hasHeader(name)
        elif self.context == 'response':
            return self.request_object.responseHeaders.hasHeader(name)
        else:
            raise Exception('Invalid context')

    def getHeader(self, name):
        if self.context == 'request':
            return self.request_object.requestHeaders.getRawHeaders(name)
        elif self.context == 'response':
            return self.request_object.responseHeaders.getRawHeaders(name)
        else:
            raise Exception('Invalid context')

    def removeHeader(self, name):
        if self.context == 'request':
            return self.request_object.requestHeaders.removeHeader(name)
        elif self.context == 'response':
            return self.request_object.responseHeaders.removeHeader(name)
        else:
            raise Exception('Invalid context')

    def setHeader(self, name, value):
        if self.context == 'request':
            return self.request_object.requestHeaders.setRawHeaders(name,
                                                                    [value])
        elif self.context == 'response':
            return self.request_object.responseHeaders.setRawHeaders(name,
                                                                     [value])
        else:
            raise Exception('Invalid context')

    def getContent(self):
        if self.context in ['request', 'response']:
            if self.context == 'request':
                return self.request_object.content.getvalue()
            elif self.context == 'response':
                return self.request_object.response_content.getvalue()
        else:
            raise Exception('Invalid context')

    def setContent(self, content):
        if self.context in ['request', 'response']:
            self.setHeader('Content-Length', str(len(content)))
            self.request_object.content = io.BytesIO(content)
        else:
            raise Exception('Invalid context')


class Registry(object):

    def __init__(self, modules_list):
        self.modules_list = modules_list
        self.modules = {}
        for module in getPlugins(IModule, "plugins"):
            self.modules[module.name] = module

        print (getPlugins(IModule, "plugins"))
        print (self.modules)

    def _get_class(self, mod_dict):
        """
        Simple function which returns a class dynamically
        when passed a dictionary containing the appropriate
        information about a proxy module

        """
        log.msg("mod_dict: %s" % mod_dict)
        module_path = mod_dict['path']
        class_name = mod_dict['name']
        try:
            module = __import__(module_path, fromlist=[class_name])
        except ImportError:
            raise ValueError("Module '%s' could not be imported" %
                             (module_path,))

        try:
            class_ = getattr(module, class_name)
        except AttributeError:
            raise ValueError("Module '%s' has no class '%s'" % (module_path,
                                                                class_name,))
        return class_

    def run_plugins(self, context, request_object=None):

        """
        Runs all proxy modules in the order specified in config.yaml

        """
#       for module_dict in self.modules:
#           class_ = self._get_class(module_dict)
#           instance_ = class_(context=context,
#                              request_object=request_object,
#                              run_contexts=module_dict['run_contexts'])
#           instance_.run(**module_dict['kwargs'])

