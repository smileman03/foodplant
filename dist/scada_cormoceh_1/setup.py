from distutils.core import setup
# import xml.etree.ElementTree
import py2exe
setup(windows=[{"script":"scada_cormoceh_1.py"}], options={"py2exe":{"includes":["PyQt4"],"includes":["sip"]}})