# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2009, 2010, 2011 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""WebStat Regression Test Suite."""

__revision__ = "$Id$"

import unittest,datetime

from invenio.config import CFG_SITE_URL, \
     CFG_WEBSESSION_DIFFERENTIATE_BETWEEN_GUESTS
from invenio.testutils import make_test_suite, run_test_suite, \
     test_web_page_content, merge_error_messages
import invenio.webstat_engine as web_eng
from invenio.dbquery import run_sql
try:
    import Levenshtein
    levenshtein_imported=True
except ImportError:
    levenshtein_imported=False

class WebStatWebPagesAvailabilityTest(unittest.TestCase):
    """Check WebStat web pages whether they are up or not."""

    def test_stats_pages_availability(self):
        """webstat - availability of /stats pages"""

        baseurl = CFG_SITE_URL + '/stats/'

        _exports = ['', 'collection_population', 'search_frequency',
                    'search_type_distribution', 'download_frequency']

        error_messages = []
        if CFG_WEBSESSION_DIFFERENTIATE_BETWEEN_GUESTS:
            for url in [baseurl + page for page in _exports]:
                error_messages.extend(test_web_page_content(url))
        for url in [baseurl + page for page in _exports]:
            error_messages.extend(test_web_page_content(url, username='admin'))
        if error_messages:
            self.fail(merge_error_messages(error_messages))
        return
    
class WebStatFrustrationDetectionTest(unittest.TestCase):
    """Check WebStat's frustration detection routines"""
    
    def setUp(self):
        """initialize test data"""
        #Session Format: (ip,searches,end_time,start_time,referrer,[(query1,time1),(query2,time2)])
        self.frustrated_session=eval("""('128.141.46.33', 63, datetime.datetime(2011, 7, 12, 16, 41, 46), datetime.datetime(2011, 7, 12, 16, 23, 43), 'http://inspirebeta.net/search?ln=en&ln=en&p=find+a+b+ratra+and+collection%3Acore&action_search=Search&sf=&so=d&rm=citation&rg=25&sc=0&of=hb', [('find j phys.rev.d', datetime.datetime(2011, 7, 12, 16, 23, 43)), ('find j phys.rev.d*', datetime.datetime(2011, 7, 12, 16, 23, 55)), ('find j phys.rev.,d*', datetime.datetime(2011, 7, 12, 16, 24, 9)), ('find j phys.rev. d*', datetime.datetime(2011, 7, 12, 16, 24, 16)), ('find j phys.rev. d', datetime.datetime(2011, 7, 12, 16, 24, 19)), ('find j phys.rev.d*', datetime.datetime(2011, 7, 12, 16, 24, 31)), ('find j phys.rev.d54*', datetime.datetime(2011, 7, 12, 16, 24, 39)), ('find j phys.rev.,d54', datetime.datetime(2011, 7, 12, 16, 24, 50)), ('find j phys.rev.,d*', datetime.datetime(2011, 7, 12, 16, 24, 54)), ('find journal phys.rev.,d*', datetime.datetime(2011, 7, 12, 16, 25, 5)), ('find journal phys.rev.', datetime.datetime(2011, 7, 12, 16, 25, 10)), ('find journal phys.rev.,d*', datetime.datetime(2011, 7, 12, 16, 25, 21)), ('find journal phys.rev.', datetime.datetime(2011, 7, 12, 16, 25, 24)), ('find date 2010 journal "phys.rev. d*"', datetime.datetime(2011, 7, 12, 16, 25, 42)), ('find date 2010 and  journal "phys.rev. d*"', datetime.datetime(2011, 7, 12, 16, 25, 47)), ('find j "phys.rev.lett.,105*"', datetime.datetime(2011, 7, 12, 16, 26, 7)), ('find j "phys.rev. d*"', datetime.datetime(2011, 7, 12, 16, 26, 20)), ('find j "phys.rev.d*"', datetime.datetime(2011, 7, 12, 16, 26, 23)), ('find j "phys.rev.d*" and date 2010', datetime.datetime(2011, 7, 12, 16, 26, 31)), ('find j "phys.rev.d*" and year 2010', datetime.datetime(2011, 7, 12, 16, 26, 35)), ('find j "phys.rev.d*" and date 2010', datetime.datetime(2011, 7, 12, 16, 26, 43)), ('find j phys.rev.d* and date 2010', datetime.datetime(2011, 7, 12, 16, 26, 57)), ('find j phys.rev.,d* and date 2010', datetime.datetime(2011, 7, 12, 16, 27, 9)), ('find j "phys.rev.,d*" and date 2010', datetime.datetime(2011, 7, 12, 16, 27, 16)), ('find j "phys.rev.,d*"', datetime.datetime(2011, 7, 12, 16, 27, 19)), ('find j "phys.rev.d*" and date 2010', datetime.datetime(2011, 7, 12, 16, 27, 30)), ('find j "phys.rev.d*"', datetime.datetime(2011, 7, 12, 16, 27, 34)), ('journal:phys.rev.d*', datetime.datetime(2011, 7, 12, 16, 27, 54)), ('journal:phys.rev.,d*', datetime.datetime(2011, 7, 12, 16, 27, 58)), ('journal:"phys.rev.,d*"', datetime.datetime(2011, 7, 12, 16, 28, 8)), ('journal:"phys.rev.d*" year:2010', datetime.datetime(2011, 7, 12, 16, 28, 34)), ('journal:"phys.rev. d*" year:2010', datetime.datetime(2011, 7, 12, 16, 29, 7)), ('journal:"phys.rev.,d*" year:2010', datetime.datetime(2011, 7, 12, 16, 29, 14)), ('journal:"phys.rev.,d" year:2010', datetime.datetime(2011, 7, 12, 16, 29, 55)), ('journal:phys.rev. year:2010', datetime.datetime(2011, 7, 12, 16, 30, 6)), ('journal:phys.rev. year:2010 volume:"d*"', datetime.datetime(2011, 7, 12, 16, 30, 24)), ('journal:phys.rev.,d*', datetime.datetime(2011, 7, 12, 16, 31, 7)), ('journal:"phys.rev.,d7*"', datetime.datetime(2011, 7, 12, 16, 31, 21)), ('journal:"phys.rev.,d7*" date:2010', datetime.datetime(2011, 7, 12, 16, 31, 35)), ('journal:"phys.rev.,d8*" date:2010', datetime.datetime(2011, 7, 12, 16, 31, 58)), ('journal:"phys.rev.,d8*" year:2010', datetime.datetime(2011, 7, 12, 16, 32, 16)), ('journal:"phys.rev.,d8*" year:2010 primarch:astro-ph', datetime.datetime(2011, 7, 12, 16, 32, 35)), ('journal:"phys.rev.,d8*" year:2010 reportnumber:astro-ph', datetime.datetime(2011, 7, 12, 16, 34, 42)), ('journal:"phys.rev.,d8*" year:2010 reportnumber:"astro-ph*"', datetime.datetime(2011, 7, 12, 16, 34, 56)), ('journal:"phys.rev.,d8*" year:2010 035:astro-ph', datetime.datetime(2011, 7, 12, 16, 33, 25)), ('find journal "phys.rev.,d8*" and year 2010 and reportnumber "astro-ph*"', datetime.datetime(2011, 7, 12, 16, 35, 27)), ('find journal "phys.rev.,d8*" and year 2010 and primarch "astro-ph*"', datetime.datetime(2011, 7, 12, 16, 35, 36)), ('find journal "phys.rev.,d8*" and year 2010 and primarch "astro-ph.he"', datetime.datetime(2011, 7, 12, 16, 36, 7)), ('find journal "phys.rev.,d8*" and year 2010 and primarch astro-ph.he', datetime.datetime(2011, 7, 12, 16, 36, 19)), ('find journal "phys.rev.,d8*" and year 2010 and primarch astro-ph.co', datetime.datetime(2011, 7, 12, 16, 36, 23)), ('find journal "phys.rev.,d8*" and year 2010 and primarch astro-ph', datetime.datetime(2011, 7, 12, 16, 36, 39)), ('find journal phys.rev. and year 2010 and primarch astro-ph', datetime.datetime(2011, 7, 12, 16, 36, 52)), ('find journal phys.rev. and year 2010', datetime.datetime(2011, 7, 12, 16, 37, 5)), ('find journal phys.rev. and year 2010', datetime.datetime(2011, 7, 12, 16, 37, 8)), ('find journal phys.rev. and jy 2010', datetime.datetime(2011, 7, 12, 16, 37, 17)), ('find journal phys.rev. and jy 2010 and primarch astro-ph', datetime.datetime(2011, 7, 12, 16, 37, 34)), ('find journal phys.rev. and jy 2010 and primarch astro-ph*', datetime.datetime(2011, 7, 12, 16, 37, 58)), ('find journal phys.rev. and jy 2010 and primarch astro-ph.*', datetime.datetime(2011, 7, 12, 16, 38, 6)), ('find journal phys.rev. and jy 2010 and primarch astro-ph.* not primarch astro-ph.he', datetime.datetime(2011, 7, 12, 16, 38, 42)), ('find journal phys.rev. and jy 2010 and primarch astro-ph.* not primarch astro-ph.he not primarch astro-ph.co', datetime.datetime(2011, 7, 12, 16, 38, 58)), ('find journal phys.rev. and jy 2010 and primarch astro-ph.* not primarch astro-ph.he not primarch astro-ph.co', datetime.datetime(2011, 7, 12, 16, 40, 39)), ('find journal phys.rev. and jy 2010 and primarch astro-ph.* not primarch astro-ph.he not primarch astro-ph.co', datetime.datetime(2011, 7, 12, 16, 40, 58)), ('find journal phys.rev. and jy 2010 and primarch astro-ph.* not archive astro-ph.he not archive astro-ph.co', datetime.datetime(2011, 7, 12, 16, 41, 46))])""")
        
        self.sessions_list=eval("""[('83.35.85.227',1, datetime.datetime(2011, 7, 12, 20, 12, 44), datetime.datetime(2011, 7, 12, 20, 12, 44), '-', [('cardiac and pericardial fistula associated with esophageal or gastric neoplasms a literature review', datetime.datetime(2011, 7, 12, 20, 12, 44))]), ('150.70.75.34', 1, datetime.datetime(2011, 7, 12, 14, 28, 1), datetime.datetime(2011, 7, 12, 14, 28, 1), '-', [('a kluson, j', datetime.datetime(2011, 7, 12, 14, 28, 1))]), ('149.132.24.42', 1, datetime.datetime(2011, 7, 12, 10, 16, 40), datetime.datetime(2011, 7, 12, 10, 16, 40), 'http://inspirebeta.net/', [('find a tomasiello', datetime.datetime(2011, 7, 12, 10, 16, 40))]), ('94.79.189.167', 2, datetime.datetime(2011, 7, 12, 23, 44, 3), datetime.datetime(2011, 7, 12, 23, 43, 56), 'http://inspirebeta.net/author/Hollands,+Stefan', [('author:s.hollands.1 ', datetime.datetime(2011, 7, 12, 23, 43, 56)), ('author:s.hollands.1', datetime.datetime(2011, 7, 12, 23, 44, 3))]), ('82.130.72.88', 1, datetime.datetime(2011, 7, 12, 15, 34, 46), datetime.datetime(2011, 7, 12, 15, 34, 46), 'http://inspirebeta.net/', [('f a runkel and a watts', datetime.datetime(2011, 7, 12, 15, 34, 46))]), ('163.10.1.11', 6, datetime.datetime(2011, 7, 12, 23, 33, 43), datetime.datetime(2011, 7, 12, 23, 32, 34), 'http://inspirebeta.net/', [('periodic boundary conditions', datetime.datetime(2011, 7, 12, 23, 32, 34)), ('periodic boundary conditions quantum field theory', datetime.datetime(2011, 7, 12, 23, 33, 8)), ('periodic boundary conditions quantum field theory', datetime.datetime(2011, 7, 12, 23, 33, 18)), ('periodic boundary conditions quantum field theory', datetime.datetime(2011, 7, 12, 23, 33, 31)), ('periodic boundary conditions quantum field theory', datetime.datetime(2011, 7, 12, 23, 33, 38)), ('periodic boundary conditions quantum field theory', datetime.datetime(2011, 7, 12, 23, 33, 43))]), ('149.169.140.105', 2, datetime.datetime(2011, 7, 12, 22, 16, 30), datetime.datetime(2011, 7, 12, 22, 16, 18), 'http://inspirebeta.net/', [('find a m suzuki', datetime.datetime(2011, 7, 12, 22, 16, 18)), ('find a m suzuki', datetime.datetime(2011, 7, 12, 22, 16, 30))]), ('210.147.144.202', 2, datetime.datetime(2011, 7, 12, 15, 39, 48), datetime.datetime(2011, 7, 12, 15, 39, 39), 'http://inspirebeta.net/', [('find a senatore', datetime.datetime(2011, 7, 12, 15, 39, 39)), ('find a senatore', datetime.datetime(2011, 7, 12, 15, 39, 48))]), ('198.129.217.23', 2, datetime.datetime(2011, 7, 12, 22, 28, 37), datetime.datetime(2011, 7, 12, 22, 28, 22), 'http://inspirebeta.net/', [('fin a cranmer', datetime.datetime(2011, 7, 12, 22, 28, 22)), ('fin a cranmer and not cn atlas', datetime.datetime(2011, 7, 12, 22, 28, 37))]), ('131.111.17.77', 2, datetime.datetime(2011, 7, 12, 12, 13, 55), datetime.datetime(2011, 7, 12, 12, 13, 50), 'http://inspirebeta.net/', [('allanach', datetime.datetime(2011, 7, 12, 12, 13, 50)), ('allanach', datetime.datetime(2011, 7, 12, 12, 13, 55))]), ('128.131.48.155', 13, datetime.datetime(2011, 7, 12, 10, 12, 55), datetime.datetime(2011, 7, 12, 10, 5, 27), '-', [('find a buesser,k', datetime.datetime(2011, 7, 12, 10, 5, 27)), ('find a de roeck,a', datetime.datetime(2011, 7, 12, 10, 6, 53)), ('find a heinemann,b', datetime.datetime(2011, 7, 12, 10, 8, 1)), ('find a desch,k', datetime.datetime(2011, 7, 12, 10, 8, 37)), ('find a dissertori,g', datetime.datetime(2011, 7, 12, 10, 8, 50)), ('find a jakobs,k', datetime.datetime(2011, 7, 12, 10, 9, 7)), ('find a monig,k', datetime.datetime(2011, 7, 12, 10, 9, 20)), ('find a muller,t', datetime.datetime(2011, 7, 12, 10, 9, 38)), ('find a paus,m', datetime.datetime(2011, 7, 12, 10, 10, 31)), ('find a pauss,f', datetime.datetime(2011, 7, 12, 10, 11)), ('find a rembser,c', datetime.datetime(2011, 7, 12, 10, 11, 15)), ('find a simon,f', datetime.datetime(2011, 7, 12, 10, 11, 39)), ('find a schulz-coulon', datetime.datetime(2011, 7, 12, 10, 12, 55))]), ('128.131.48.157', 1, datetime.datetime(2011, 7, 12, 15, 39, 51), datetime.datetime(2011, 7, 12, 15, 39, 51), 'http://inspirebeta.net/', [('broderick prakash lattimer', datetime.datetime(2011, 7, 12, 15, 39, 51))]), ('146.155.47.206', 1, datetime.datetime(2011, 7, 12, 19, 29, 47), datetime.datetime(2011, 7, 12, 19, 29, 47), 'http://inspirebeta.net/', [('a troncoso and martinez', datetime.datetime(2011, 7, 12, 19, 29, 47))]), ('131.169.210.50', 2, datetime.datetime(2011, 7, 12, 18, 58, 51), datetime.datetime(2011, 7, 12, 18, 55, 33), 'http://inspirebeta.net/search?ln=en&ln=en&p=find+a+kalaydzhyan&action_search=Search&sf=&so=d&rm=&rg=25&sc=0&of=hb', [('find a kerbikov', datetime.datetime(2011, 7, 12, 18, 55, 33)), ('find a andreichikov, m', datetime.datetime(2011, 7, 12, 18, 58, 51))]), ('72.33.156.44', 4, datetime.datetime(2011, 7, 12, 17, 24, 45), datetime.datetime(2011, 7, 12, 17, 21, 33), 'http://inspirebeta.net/', [('find a francis petriello', datetime.datetime(2011, 7, 12, 17, 21, 33)), ('find a frank petriello', datetime.datetime(2011, 7, 12, 17, 22, 3)), ('find a frank petriello', datetime.datetime(2011, 7, 12, 17, 23, 9)), ('find a frank petriello and k resummation', datetime.datetime(2011, 7, 12, 17, 24, 45))])]""")
                           
    def test_frustration_algorithm(self):
        """webstat - frustration detection algorithm"""
        res=web_eng.checkSessionFrustrated(self.sessions_list[0])
        res2=web_eng.checkSessionFrustrated(self.frustrated_session)
        if res==0:
            if res2==32 or not levenshtein_imported:
                return
            else:
                self.fail("Could not detect frustration"+str(res2))
        else:
            self.fail("Detected frustration in bad context")
    
    def test_session_construction(self):
        """webstat - construction of sessions"""
        res=web_eng.processSessionData(self.sessions_list)
        if res==(15,6,(0,0,1,0,0)):
            return
        else:
            self.fail("Could not process session data appropriately")

TEST_SUITE = make_test_suite(WebStatWebPagesAvailabilityTest, WebStatFrustrationDetectionTest)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE, warn_user=True)
