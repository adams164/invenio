#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################################################################
"""Get N most recent public items from a set of feeds; format and dump them."""

try:
    import feedparser
except ImportError:
    print "Please install the Python feedparser library."
import sys
import codecs
import optparse

from invenio.dbquery import run_sql


FEEDS = [
         ("http://invenio-software.org/query?status=assigned&status=in_work&status=infoneeded&status=infoneeded_new&status=new&changetime=30daysago..&keywords=~INSPIRE+NEWS&format=rss&col=id&col=summary&col=status&col=type&col=priority&col=milestone&col=component&order=priority", "Current Work"),
         #("http://invenio-software.org/query?status=assigned&status=in_merge&status=in_work&status=new&keywords=INSPIRE+NEWS&format=rss&col=id&col=summary&col=owner&col=type&col=priority&col=milestone&col=component&order=priority", "Current Work"),
         #("http://invenio-software.org/query?status=assigned&status=in_work&status=infoneeded&status=infoneeded_new&status=new&keywords=INSPIRE+NEWS&format=rss&order=priority", "Current Work"),
         #("http://cdswaredev.cern.ch/invenio/report/1?format=rss&USER=anonymous", "Current Work"),
         #("http://cdswaredev.cern.ch/invenio/query?status=closed&format=rss&order=priority&resolution=fixed", "Recently Finished Work"),
         #("http://invenio-software.org/query?status=closed&status=in_merge&keywords=INSPIRE+NEWS&format=rss&order=priority", "Recently Finished Work"),
         ("http://invenio-software.org/query?status=closed&status=in_merge&changetime=30daysago..&keywords=~NEWS&format=rss&col=id&col=summary&col=status&col=type&col=priority&col=milestone&col=component&order=priority", "Recently Finished Work"),
        ]

def configOptParse():
    parser = optparse.OptionParser(usage = "%prog [options] [-o outfile]")
    parser.add_option('-n', '--number', dest="number", action="store", type="int", metavar="N",
                      default=6, help="Get N most recent public LJ posts.  Defaults to 6")
    parser.add_option('-u', '--uname', dest="uname", action="store", metavar="UNAME", default='anonymous',
                      help="Substituted for UNAME into the resource URL.  Defaults to anonymous")
    parser.add_option('-r', '--resource', dest="url", action="store", metavar="URL",
                      default='http://cdswaredev.cern.ch/invenio/report/1?format=rss&USER=UNAME',
                      help="Updates from URL (Token UNAME substituted for value of -u). Defaults to http://cdswaredev.cern.ch/invenio/report/1?format=rss&USER=UNAME")
    parser.add_option('-o', '--outfile', dest="outfile", action="store", metavar="FILE", default=None,
                      help="Output to FILE.  - writes to stdout.  Defaults to no output")
    parser.add_option('-d', '--dbwrite', dest="dbwrite", action="store_true", default=False,
                      help="Write feed data into the MySQL instance. Defaults to off.")
    options, args = parser.parse_args()
    return parser, options, args

def postGenerator(url, max, filter = lambda x: x):
    count = 0
    date = ''
    for post in feedparser.parse(url).entries:
        if count == max: break
        if filter(post.title):
            count += 1
            try:
                date = post.published[:19]
            except AttributeError:
                date = "%d-%02d-%02d %02d:%02d" % post.updated_parsed[0:5]
            try:
                title = post.title.decode('utf-8')
            except UnicodeEncodeError:
                title = post.title
            yield date, title, post.link

def filters(msg):
    """Stub function to (later) enable filtering of the entries displayed.

    Multiple kinds of filtering can be done by making this a logical and of
    several additional filter functions.
    """
    return True

def outputGenerator(header, input):
    yield u"<td class=\"bugboxtd\">\n<ul class=\"activity\"><h3 id=\"bugblog\">"+header+"</h3>\n"
    for date, title, link in input:
        yield u"\n        <li><a href=\"%s\">%s</a>: %s</li>" % (link, title, date)
    yield u'\n       </ul>\n      </td>'


if __name__ == "__main__":

    parser, options, args = configOptParse()
    out = sys.stdout

    if (len(sys.argv) == 0) or ((options.outfile == None) and (options.dbwrite == False)):
        parser.print_help()
        sys.exit()
    if options.outfile:
        if options.outfile != '-':
            out = codecs.open(options.outfile, 'w', 'utf-8')

    portalbox_content = u"<div id=\"bugbox\" class=\"portalboxbody\">\n"
    portalbox_content += " <table class=\"bugboxtable\">\n"
    portalbox_content += "  <tr>"
    for feed in FEEDS:
        url = feed[0]
        title = feed[1]
        for line in outputGenerator(title,
                                    sorted(postGenerator(url.replace('UNAME', options.uname),
                                                         options.number,
                                                         filter=filters),
                                           reverse=True),
                                    ):
            portalbox_content += line
    portalbox_content += "</tr>\n"
    portalbox_content += " </table>\n</div>"

    # Make adjustment to Invenio database
    if options.dbwrite:
        run_sql("UPDATE portalbox SET body=%s WHERE id=3", (portalbox_content,))
    # output snippets to requested file
    if options.outfile:
        out.write(portalbox_content)

    # close any working files
    outname = out.name
    if outname != '<stdout>':
        out.close()

