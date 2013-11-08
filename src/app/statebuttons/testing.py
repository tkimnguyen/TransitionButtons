from plone.app.testing import TEST_USER_NAME, PLONE_FIXTURE, login, \
    IntegrationTesting, PloneSandboxLayer, applyProfile, setRoles, \
    TEST_USER_ID, TEST_USER_PASSWORD

from plone.app.testing import FunctionalTesting, pushGlobalRegistry, popGlobalRegistry, TEST_USER_NAME

from Products.CMFCore.utils import getToolByName
from plone.testing.z2 import Browser
from Products.Five.browser import BrowserView as View
from zope.viewlet.interfaces import IViewletManager
from app.statebuttons.browser.viewlets import ButtonViewlet
from zope.component import queryMultiAdapter

from plone.testing import z2
import unittest2 as unittest
from zope.configuration import xmlconfig


class AppstatebuttonsLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)



class StatebuttonsFixture(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import app.statebuttons
        xmlconfig.file('configure.zcml',
            app.statebuttons, context=configurationContext)
        self.loadZCML(package=app.statebuttons)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'app.statebuttons:default')
        setRoles(portal, TEST_USER_ID, ['Manager'])
        import transaction
        transaction.commit()
        login(portal, TEST_USER_NAME)


STATEBUTTONS_FIXTURE = StatebuttonsFixture()
APP_STATEBUTTONS_FUNCTIONAL_TESTING = FunctionalTesting(
                        bases=(STATEBUTTONS_FIXTURE,),
                        name="AppstatebuttonsLayer:Functional"
)

APP_STATEBUTTONS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(STATEBUTTONS_FIXTURE,),
    name="AppstatebuttonsLayer:Integration"
)

class BaseTest(unittest.TestCase):

    def setUp(self):
        portal = self.layer['portal']
        app = self.layer['app']

        self.browser = Browser(app)
        self.browser.handleErrors = False

        self.browser.addHeader('Authorization', 'Basic %s:%s' % (TEST_USER_NAME, TEST_USER_PASSWORD,))

        memTool = getToolByName(portal, 'portal_membership')
        self.member = memTool.getMemberById(TEST_USER_ID)
        self.member.setMemberProperties(mapping={'buttonsEnabled': True})


        portal.invokeFactory('Folder', 'f1', title=u"Folder 1")
        f1 = portal['f1']
        f1.invokeFactory('Document', 'd1', title=u"Document 1")
        self.doc = f1['d1']

        request = self.layer['request']
        view = View(self.doc, request)

        wfTool = getToolByName(portal, 'portal_workflow')
        wfTool.setDefaultChain('simple_publication_workflow')

        self.buttonViewlet = ButtonViewlet(self.doc, request, view)

        import transaction
        transaction.commit()



        pushGlobalRegistry(portal)

    def tearDown(self):
        portal = self.layer['portal']
        popGlobalRegistry(portal)

    def getControlPanel(self):
        request = self.layer['request']
        request.set('URL', "http://nohost/plone/@@button-settings")

        self.browser.open(request.URL)


