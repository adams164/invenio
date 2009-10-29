## This file is part of CDS Invenio.
## Copyright (C) 2002, 2003, 2004, 2005, 2006, 2007, 2008 CERN.
##
## CDS Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## CDS Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with CDS Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

# pylint: disable-msg=C0103
"""CDS Invenio BibEdit Engine."""

__revision__ = "$Id"

from invenio.bibedit_config import CFG_BIBEDIT_AJAX_RESULT_CODES, \
    CFG_BIBEDIT_JS_CHECK_SCROLL_INTERVAL, CFG_BIBEDIT_JS_HASH_CHECK_INTERVAL, \
    CFG_BIBEDIT_JS_CLONED_RECORD_COLOR, \
    CFG_BIBEDIT_JS_CLONED_RECORD_COLOR_FADE_DURATION, \
    CFG_BIBEDIT_JS_NEW_ADD_FIELD_FORM_COLOR, \
    CFG_BIBEDIT_JS_NEW_ADD_FIELD_FORM_COLOR_FADE_DURATION, \
    CFG_BIBEDIT_JS_NEW_CONTENT_COLOR, \
    CFG_BIBEDIT_JS_NEW_CONTENT_COLOR_FADE_DURATION, \
    CFG_BIBEDIT_JS_NEW_CONTENT_HIGHLIGHT_DELAY, \
    CFG_BIBEDIT_JS_STATUS_ERROR_TIME, CFG_BIBEDIT_JS_STATUS_INFO_TIME, \
    CFG_BIBEDIT_JS_TICKET_REFRESH_DELAY, CFG_BIBEDIT_MAX_SEARCH_RESULTS, \
    CFG_BIBEDIT_TAG_FORMAT, CFG_BIBEDIT_AUTOSUGGEST_TAGS, \
    CFG_BIBEDIT_AUTOCOMPLETE_TAGS_KBS, CFG_BIBEDIT_KEYWORD_TAXONOMY, \
    CFG_BIBEDIT_KEYWORD_TAG, CFG_BIBEDIT_KEYWORD_RDFLABEL
from invenio.bibedit_dblayer import get_name_tags_all, reserve_record_id
from invenio.bibedit_utils import cache_exists, cache_expired, \
    create_cache_file, delete_cache_file, get_bibrecord, \
    get_cache_file_contents, get_cache_mtime, get_record_templates, \
    get_record_template, latest_record_revision, record_locked_by_other_user, \
    record_locked_by_queue, save_xml_record, touch_cache_file, \
    update_cache_file_contents
from invenio.bibrecord import create_record, print_rec, record_add_field, \
    record_add_subfield_into, record_delete_field, \
    record_delete_subfield_from, record_modify_controlfield, \
    record_modify_subfield, record_move_subfield, record_move_fields, record_get_field_values
from invenio.config import CFG_BIBEDIT_PROTECTED_FIELDS, CFG_CERN_SITE, \
    CFG_SITE_URL
from invenio.search_engine import record_exists, search_pattern
from invenio.webuser import session_param_get, session_param_set
from invenio.bibcatalog import bibcatalog_system
from invenio.bibknowledge import get_kbd_values_for_bibedit, get_kbr_values, \
     get_kbt_items_for_bibedit #autosuggest

import invenio.template

bibedit_templates = invenio.template.load('bibedit')

def perform_request_init():
    """Handle the initial request by adding menu and JavaScript to the page."""
    errors   = []
    warnings = []
    body = ''

    # Add script data.
    record_templates = get_record_templates()
    record_templates.sort()
    tag_names = get_name_tags_all()
    protected_fields = ['001']
    protected_fields.extend(CFG_BIBEDIT_PROTECTED_FIELDS.split(','))
    history_url = '"' + CFG_SITE_URL + '/admin/bibedit/bibeditadmin.py/history"'
    cern_site = 'false'
    if CFG_CERN_SITE:
        cern_site = 'true'
    data = {'gRECORD_TEMPLATES': record_templates,
            'gTAG_NAMES': tag_names,
            'gPROTECTED_FIELDS': protected_fields,
            'gSITE_URL': '"' + CFG_SITE_URL + '"',
            'gHISTORY_URL': history_url,
            'gCERN_SITE': cern_site,
            'gHASH_CHECK_INTERVAL': CFG_BIBEDIT_JS_HASH_CHECK_INTERVAL,
            'gCHECK_SCROLL_INTERVAL': CFG_BIBEDIT_JS_CHECK_SCROLL_INTERVAL,
            'gSTATUS_ERROR_TIME': CFG_BIBEDIT_JS_STATUS_ERROR_TIME,
            'gSTATUS_INFO_TIME': CFG_BIBEDIT_JS_STATUS_INFO_TIME,
            'gCLONED_RECORD_COLOR':
                '"' + CFG_BIBEDIT_JS_CLONED_RECORD_COLOR + '"',
            'gCLONED_RECORD_COLOR_FADE_DURATION':
                CFG_BIBEDIT_JS_CLONED_RECORD_COLOR_FADE_DURATION,
            'gNEW_ADD_FIELD_FORM_COLOR':
                '"' + CFG_BIBEDIT_JS_NEW_ADD_FIELD_FORM_COLOR + '"',
            'gNEW_ADD_FIELD_FORM_COLOR_FADE_DURATION':
                CFG_BIBEDIT_JS_NEW_ADD_FIELD_FORM_COLOR_FADE_DURATION,
            'gNEW_CONTENT_COLOR': '"' + CFG_BIBEDIT_JS_NEW_CONTENT_COLOR + '"',
            'gNEW_CONTENT_COLOR_FADE_DURATION':
                CFG_BIBEDIT_JS_NEW_CONTENT_COLOR_FADE_DURATION,
            'gNEW_CONTENT_HIGHLIGHT_DELAY':
                CFG_BIBEDIT_JS_NEW_CONTENT_HIGHLIGHT_DELAY,
            'gTICKET_REFRESH_DELAY': CFG_BIBEDIT_JS_TICKET_REFRESH_DELAY,
            'gRESULT_CODES': CFG_BIBEDIT_AJAX_RESULT_CODES,
            'gAUTOSUGGEST_TAGS' : CFG_BIBEDIT_AUTOSUGGEST_TAGS,
            'gAUTOCOMPLETE_TAGS' : CFG_BIBEDIT_AUTOCOMPLETE_TAGS_KBS.keys(),
            'gKEYWORD_TAG' : '"' + CFG_BIBEDIT_KEYWORD_TAG  + '"'
            }
    body += '<script type="text/javascript">\n'
    for key in data:
        body += '    var %s = %s;\n' % (key, data[key])
    body += '    </script>\n'

    # Add scripts (the ordering is NOT irrelevant).
    scripts = ['jquery.min.js', 'effects.core.min.js',
               'effects.highlight.min.js', 'jquery.autogrow.js',
               'jquery.jeditable.mini.js', 'jquery.hotkeys.min.js', 'json2.js',
               'bibedit_display.js', 'bibedit_engine.js', 'bibedit_keys.js',
               'bibedit_menu.js']

    for script in scripts:
        body += '    <script type="text/javascript" src="%s/js/%s">' \
            '</script>\n' % (CFG_SITE_URL, script)

    # Build page structure and menu.
    body += bibedit_templates.menu()
    body += '    <div id="bibEditContent"></div>\n'

    return body, errors, warnings

def perform_request_newticket(recid, uid):
    """create a new ticket with this record's number
    @param recid: record id
    @param uid: user id
    @return: (error_msg, url)

    """
    t_id = bibcatalog_system.ticket_submit(uid, "", recid, "")
    t_url = ""
    errmsg = ""
    if t_id:
        #get the ticket's URL
        t_url = bibcatalog_system.ticket_get_attribute(uid, t_id, 'url_modify')
    else:
        errmsg = "ticket_submit failed"
    return (errmsg, t_url)

def perform_request_ajax(req, recid, uid, data):
    """Handle Ajax requests by redirecting to appropriate function."""
    response = {}
    request_type = data['requestType']

    # Call function based on request type.
    if request_type == 'searchForRecord':
        # Search request.
        response.update(perform_request_search(data))
    elif request_type in ['changeTagFormat']:
        # User related requests.
        response.update(perform_request_user(req, request_type, recid, data))
    elif request_type in ('getRecord', 'submit', 'cancel', 'newRecord',
        'deleteRecord', 'deleteRecordCache', 'prepareRecordMerge'):
        # 'Major' record related requests.
        response.update(perform_request_record(req, request_type, recid, uid,
                                               data))
    elif request_type in ('addField', 'addSubfields', 'modifyContent',
                          'moveSubfield', 'deleteFields', 'moveField',
                          'autosuggest', 'autocomplete', 'autokeyword'):
        # Record updates.
        response.update(perform_request_update_record(
                request_type, recid, uid, data))

    elif request_type in ('getTickets'):
        # BibCatalog requests.
        response.update(perform_request_bibcatalog(request_type, recid, uid))

    return response

def perform_request_search(data):
    """Handle search requests."""
    response = {}
    searchType = data['searchType']
    searchPattern = data['searchPattern']
    if searchType == 'anywhere':
        pattern = searchPattern
    else:
        pattern = searchType + ':' + searchPattern
    result_set = list(search_pattern(p=pattern))
    response['resultCode'] = 1
    response['resultSet'] = result_set[0:CFG_BIBEDIT_MAX_SEARCH_RESULTS]
    return response

def perform_request_user(req, request_type, recid, data):
    """Handle user related requests."""
    response = {}
    if request_type == 'changeTagFormat':
        try:
            tagformat_settings = session_param_get(req, 'bibedit_tagformat')
        except KeyError:
            tagformat_settings = {}
        tagformat_settings[recid] = data['tagFormat']
        session_param_set(req, 'bibedit_tagformat', tagformat_settings)
        response['resultCode'] = 2
    return response

def perform_request_record(req, request_type, recid, uid, data):
    """Handle 'major' record related requests like fetching, submitting or
    deleting a record, cancel editing or preparing a record for merging.

    """
    response = {}

    if request_type == 'newRecord':
        # Create a new record.
        new_recid = reserve_record_id()
        new_type = data['newType']
        if new_type == 'empty':
            # Create a new empty record.
            create_cache_file(recid, uid)
            response['resultCode'], response['newRecID'] = 6, new_recid

        elif new_type == 'template':
            # Create a new record from XML record template.
            template_filename = data['templateFilename']
            template = get_record_template(template_filename)
            if not template:
                response['resultCode']  = 108
            else:
                record = create_record(template)[0]
                if not record:
                    response['resultCode']  = 109
                else:
                    record_add_field(record, '001',
                                     controlfield_value=str(new_recid))
                    create_cache_file(new_recid, uid, record, True)
                    response['resultCode'], response['newRecID']  = 7, new_recid

        elif new_type == 'clone':
            # Clone an existing record (from the users cache).
            existing_cache = cache_exists(recid, uid)
            if existing_cache:
                record = get_cache_file_contents(recid, uid)[2]
            else:
                # Cache missing. Fall back to using original version.
                record = get_bibrecord(recid)
            record_delete_field(record, '001')
            record_add_field(record, '001', controlfield_value=str(new_recid))
            create_cache_file(new_recid, uid, record, True)
            response['resultCode'], response['newRecID'] = 8, new_recid

    elif request_type == 'getRecord':
        # Fetch the record. Possible error situations:
        # - Non-existing record
        # - Deleted record
        # - Record locked by other user
        # - Record locked by queue
        # A cache file will be created if it does not exist.
        # If the cache is outdated (i.e., not based on the latest DB revision),
        # cacheOutdated will be set to True in the response.
        record_status = record_exists(recid)
        existing_cache = cache_exists(recid, uid)
        if record_status == 0:
            response['resultCode'] = 102
        elif record_status == -1:
            response['resultCode'] = 103
        elif not existing_cache and record_locked_by_other_user(recid, uid):
            response['resultCode'] = 104
        elif existing_cache and cache_expired(recid, uid) and \
                record_locked_by_other_user(recid, uid):
            response['resultCode'] = 104
        elif record_locked_by_queue(recid):
            response['resultCode'] = 105
        else:
            if data.get('deleteRecordCache'):
                delete_cache_file(recid, uid)
                existing_cache = False
            if not existing_cache:
                record_revision, record = create_cache_file(recid, uid)
                mtime = get_cache_mtime(recid, uid)
                cache_dirty = False
            else:
                cache_dirty, record_revision, record = \
                    get_cache_file_contents(recid, uid)
                touch_cache_file(recid, uid)
                mtime = get_cache_mtime(recid, uid)
                if not latest_record_revision(recid, record_revision):
                    response['cacheOutdated'] = True
            if data['clonedRecord']:
                response['resultCode'] = 9
            else:
                response['resultCode'] = 3
            response['cacheDirty'], response['record'], \
                response['cacheMTime'] = cache_dirty, record, mtime
            # Set tag format from user's session settings.
            try:
                tagformat_settings = session_param_get(req, 'bibedit_tagformat')
                tagformat = tagformat_settings[recid]
            except KeyError:
                tagformat = CFG_BIBEDIT_TAG_FORMAT
            response['tagFormat'] = tagformat

    elif request_type == 'submit':
        # Submit the record. Possible error situations:
        # - Missing cache file
        # - Cache file modified in other editor
        # - Record locked by other user
        # - Record locked by queue
        # - Invalid XML characters
        # If the cache is outdated cacheOutdated will be set to True in the
        # response.
        if not cache_exists(recid, uid):
            response['resultCode'] = 106
        elif not get_cache_mtime(recid, uid) == data['cacheMTime']:
            response['resultCode'] = 107
        elif cache_expired(recid, uid) and \
                record_locked_by_other_user(recid, uid):
            response['resultCode'] = 104
        elif record_locked_by_queue(recid):
            response['resultCode'] = 105
        else:
            record_revision, record = get_cache_file_contents(recid, uid)[1:]
            xml_record = print_rec(record)
            record, status_code, list_of_errors = create_record(xml_record)
            if status_code == 0:
                response['resultCode'], response['errors'] = 110, \
                    list_of_errors
            elif not data['force'] and \
                    not latest_record_revision(recid, record_revision):
                response['cacheOutdated'] = True
            else:
                save_xml_record(recid, uid)
                response['resultCode'] = 4

    elif request_type == 'cancel':
        # Cancel editing by deleting the cache file. Possible error situations:
        # - Cache file modified in other editor
        if cache_exists(recid, uid):
            if get_cache_mtime(recid, uid) == data['cacheMTime']:
                delete_cache_file(recid, uid)
                response['resultCode'] = 5
            else:
                response['resultCode'] = 107
        else:
            response['resultCode'] = 5

    elif request_type == 'deleteRecord':
        # Submit the record. Possible error situations:
        # - Record locked by other user
        # - Record locked by queue
        # As the user is requesting deletion we proceed even if the cache file
        # is missing and we don't check if the cache is outdated or has
        # been modified in another editor.
        existing_cache = cache_exists(recid, uid)
        if existing_cache and cache_expired(recid, uid) and \
                record_locked_by_other_user(recid, uid):
            response['resultCode'] = 104
        elif record_locked_by_queue(recid):
            response['resultCode'] = 105
        else:
            if not existing_cache:
                record_revision, record = create_cache_file(recid, uid)
            else:
                record_revision, record = get_cache_file_contents(
                    recid, uid)[1:]
            record_add_field(record, '980', ' ', ' ', '', [('c', 'DELETED')])
            update_cache_file_contents(recid, uid, record_revision, record)
            save_xml_record(recid, uid)
            response['resultCode'] = 10

    elif request_type == 'deleteRecordCache':
        # Delete the cache file. Ignore the request if the cache has been
        # modified in another editor.
        if cache_exists(recid, uid) and get_cache_mtime(recid, uid) == \
                data['cacheMTime']:
            delete_cache_file(recid, uid)
        response['resultCode'] = 11

    elif request_type == 'prepareRecordMerge':
        # We want to merge the cache with the current DB version of the record,
        # so prepare an XML file from the file cache, to be used by BibMerge.
        # Possible error situations:
        # - Missing cache file
        # - Record locked by other user
        # - Record locked by queue
        # We don't check if cache is outdated (a likely scenario for this
        # request) or if it has been modified in another editor.
        if not cache_exists(recid, uid):
            response['resultCode'] = 106
        elif cache_expired(recid, uid) and \
                record_locked_by_other_user(recid, uid):
            response['resultCode'] = 104
        elif record_locked_by_queue(recid):
            response['resultCode'] = 105
        else:
            save_xml_record(recid, uid, to_upload=False, to_merge=True)
            response['resultCode'] = 12

    return response

def perform_request_update_record(request_type, recid, uid, data):
    """Handle record update requests like adding, modifying, moving or deleting
    of fields or subfields. Possible common error situations:
    - Missing cache file
    - Cache file modified in other editor

    """
    response = {}

    if not cache_exists(recid, uid):
        response['resultCode'] = 106
    elif not get_cache_mtime(recid, uid) == data['cacheMTime']:
        response['resultCode'] = 100
        #107!
    else:
        record_revision, record = get_cache_file_contents(recid, uid)[1:]
        field_position_local = data.get('fieldPosition')
        if field_position_local is not None:
            field_position_local = int(field_position_local)

        if request_type == 'addField':
            if data['controlfield']:
                record_add_field(record, data['tag'],
                                 controlfield_value=data['value'])
                response['resultCode'] = 20
            else:
                record_add_field(record, data['tag'], data['ind1'],
                                 data['ind2'], subfields=data['subfields'],
                                 field_position_local=field_position_local)
                response['resultCode'] = 21

        elif request_type == 'addSubfields':
            subfields = data['subfields']
            for subfield in subfields:
                record_add_subfield_into(record, data['tag'], subfield[0],
                    subfield[1], subfield_position=None,
                    field_position_local=field_position_local)
            if len(subfields) == 1:
                response['resultCode'] = 22
            else:
                response['resultCode'] = 23

        elif request_type == 'modifyContent':
            if data['subfieldIndex'] != None:
                record_modify_subfield(record, data['tag'],
                    data['subfieldCode'], data['value'],
                    int(data['subfieldIndex']),
                    field_position_local=field_position_local)
            else:
                record_modify_controlfield(record, data['tag'], data['value'],
                    field_position_local=field_position_local)
            response['resultCode'] = 24

        elif request_type == 'moveSubfield':
            record_move_subfield(record, data['tag'],
                int(data['subfieldIndex']), int(data['newSubfieldIndex']),
                field_position_local=field_position_local)
            response['resultCode'] = 25

        elif request_type == 'moveField':
            if data['direction'] == 'up':
                final_position_local = field_position_local-1
            else: # direction is 'down'
                final_position_local = field_position_local+1
            record_move_fields(record, data['tag'], [field_position_local],
                final_position_local)
            response['resultCode'] = 32

        elif request_type == 'deleteFields':
            to_delete = data['toDelete']
            deleted_fields = 0
            deleted_subfields = 0
            for tag in to_delete:
                for field_position_local in to_delete[tag]:
                    if not to_delete[tag][field_position_local]:
                        # No subfields specified - delete entire field.
                        record_delete_field(record, tag,
                            field_position_local=int(field_position_local))
                        deleted_fields += 1
                    else:
                        for subfield_position in \
                                to_delete[tag][field_position_local][::-1]:
                            # Delete subfields in reverse order (to keep the
                            # indexing correct).
                            record_delete_subfield_from(record, tag,
                                int(subfield_position),
                                field_position_local=int(field_position_local))
                            deleted_subfields += 1
            if deleted_fields == 1 and deleted_subfields == 0:
                response['resultCode'] = 26
            elif deleted_fields and deleted_subfields == 0:
                response['resultCode'] = 27
            elif deleted_subfields == 1 and deleted_fields == 0:
                response['resultCode'] = 28
            elif deleted_subfields and deleted_fields == 0:
                response['resultCode'] = 29
            else:
                response['resultCode'] = 30

        elif (request_type == 'autosuggest' or \
              request_type == 'autocomplete' or \
              request_type == 'autokeyword' ):
            # get the values based on which one needs to search
            searchby = data['value']
            #we check if the data is properly defined
            fulltag = ''
            if data.has_key('maintag') and data.has_key('subtag1') and \
               data.has_key('subtag2') and data.has_key('subfieldcode'):
                maintag = data['maintag']
                subtag1 = data['subtag1']
                subtag2 = data['subtag2']
                u_subtag1 = subtag1
                u_subtag2 = subtag2
                if (not subtag1) or (subtag1 == ' '):
                    u_subtag1 = '_'
                if (not subtag2) or (subtag2 == ' '):
                    u_subtag2 = '_'
                subfieldcode = data['subfieldcode']
                fulltag = maintag+u_subtag1+u_subtag2+subfieldcode
            if (request_type == 'autokeyword'):
                #call the keyword-form-ontology function
                if fulltag and searchby:
                    items = get_kbt_items_for_bibedit(CFG_BIBEDIT_KEYWORD_TAXONOMY, \
                            CFG_BIBEDIT_KEYWORD_RDFLABEL, searchby)
                    response['autokeyword'] = items
            if (request_type == 'autosuggest'):
                #call knowledge base function to put the suggestions in an array..
                if fulltag and searchby and len(searchby) > 3:
                    suggest_values = get_kbd_values_for_bibedit(fulltag, "", searchby)
                    #remove ..
                    new_suggest_vals = []
                    for sugg in suggest_values:
                        if sugg.startswith(searchby):
                            new_suggest_vals.append(sugg)
                    response['autosuggest'] = new_suggest_vals
            if (request_type == 'autocomplete'):
                #call the values function with the correct kb_name
                if CFG_BIBEDIT_AUTOCOMPLETE_TAGS_KBS.has_key(fulltag):
                    kbname = CFG_BIBEDIT_AUTOCOMPLETE_TAGS_KBS[fulltag]
                    #check if the seachby field has semicolons. Take all
                    #the semicolon-separated items..
                    items = []
                    vals = []
                    if searchby:
                        if searchby.rfind(';'):
                            items = searchby.split(';')
                        else:
                            items = [searchby.strip()]
                    for item in items:
                        item = item.strip()
                        kbrvals = get_kbr_values(kbname, item, 'e') #we want an exact match
                        if kbrvals and kbrvals[0]: #add the found val into vals
                            vals.extend(kbrvals[0])
                    #check that the values are not already contained in other
                    #instances of this field
                    record_revision, record = get_cache_file_contents(recid, uid)[1:]
                    xml_rec = print_rec(record)
                    record, status_code, dummy_errors = create_record(xml_rec)
                    existing_values = []
                    if (status_code != 0):
                        existing_values = record_get_field_values(record,
                                                                  maintag,
                                                                  subtag1,
                                                                  subtag2,
                                                                  subfieldcode)
                    #get the new values.. i.e. vals not in existing
                    new_vals = vals
                    for val in new_vals:
                        if val in existing_values:
                            new_vals.remove(val)
                    response['autocomplete'] = new_vals
            response['resultCode'] = 33

        response['cacheMTime'], response['cacheDirty'] = \
            update_cache_file_contents(recid, uid, record_revision, record), \
            True

    return response

def perform_request_bibcatalog(request_type, recid, uid):
    """Handle request to BibCatalog (RT).

    """
    response = {}

    if request_type == 'getTickets':
        # Insert the ticket data in the response, if possible
        if uid:
            bibcat_resp = bibcatalog_system.check_system(uid)
            if bibcat_resp == "":
                tickets_found = bibcatalog_system.ticket_search(uid,
                                 status=['new', 'open'], recordid=recid)
                t_url_str = '' #put ticket urls here,
                               #formatted for HTML display
                for t_id in tickets_found:
                    ticket_info = bibcatalog_system.ticket_get_info(uid,
                                   t_id, ['url_display', 'url_close'])
                    t_url = ticket_info['url_display']
                    t_close_url = ticket_info['url_close']
                    #format..
                    t_url_str += "#"+str(t_id)+'<a href="'+t_url+'">[read]</a> '
                    t_url_str += '<a href="'+t_close_url+'">[close]</a><br/>'
                #put ticket header and tickets links in the box
                t_url_str = "<strong>Tickets</strong><br/>"+t_url_str
                t_url_str += "<br/>"+'<a href="new_ticket?recid='
                t_url_str += str(recid)+'>[new ticket]<a>'
                response['tickets'] = t_url_str
                #add a new ticket link
            else:
                #put something in the tickets container, for debug
                response['tickets'] = "<!--"+bibcat_resp+"-->"
        response['resultCode'] = 31

    return response
