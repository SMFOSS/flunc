from twill.namespaces import get_twill_glocals 
from twill.commands import get_browser
from twill.errors import TwillAssertionError
from twill.errors import TwillException
from flunc import options
from logging import log_error, log_warn
from lxml.etree import XPathEvalError
import lxml.html
import re

__all__ = ['run_xpath', 'find_in_xpath']


def run_xpath(xpath):
    _, twill_locals = get_twill_glocals()
    browser = get_browser()
    html = browser.get_html()
    tree = lxml.html.document_fromstring(html)

    # XXX this raises an error if the xpath is bad
    # should we catch it more gracefully and print some kind of error message
    # in flunc to make it more obvious?
    try:
        results = tree.xpath(xpath)
    except XPathEvalError:
        err_msg = "Invalid xpath expression: '%s'" % xpath
        log_error(err_msg)
        raise TwillException(err_msg)

    #XXX we aggregate all the values together and warn when there is more than
    #one result
    if results:
        if len(results) > 1:
            log_warn("xpath '%s' found multiple results: using all of them")
        result = '\n'.join(lxml.html.tostring(r) for r in results)
    else:
        log_error("xpath '%s' found no results")
        result = ''
    twill_locals['__xpath_result__'] = result

#XXX add in argument to pass in flags?
def find_in_xpath(what):
    _, twill_locals = get_twill_glocals()
    xpath_result = twill_locals.get('__xpath_result__')
    assert xpath_result is not None, \
           'Running find_in_xpath without first calling run_xpath'

    regexp = re.compile(what)
    m = regexp.search(xpath_result)
    if not m:
        raise TwillAssertionError("no match to '%s' in '%s'" %
                                  (what, xpath_result))

    if m.groups():
        match_str = m.group(1)
    else:
        match_str = m.group(0)
    twill_locals['__match__'] = match_str

#XXX add a notfind?
