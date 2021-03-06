# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2011 CERN.
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
'''
bibauthorid_module_topcites
    Meant for calculating probabilities of a virtual author and a real author
    being the same based on their citations on a particular paper.
'''
from bibauthorid_utils import get_field_values_on_condition
from bibauthorid_realauthor_utils import set_realauthor_data
from bibauthorid_realauthor_utils import get_realauthor_data
from bibauthorid_virtualauthor_utils import get_virtualauthor_records
from math import sqrt
import bibauthorid_config as bconfig


# NAME: Defines the name of the module for display purposes. [A-Za-z0-9 \-_]
MODULE_NAME = "Topcite Comparison"
# OPERATOR: Defines the operator to use for the final computation [+|*]
MODULE_OPERATOR = "+"
# WEIGHT: Defines the weight of this module for the final computation [0..1]
MODULE_WEIGHT = 1.0


def get_information_from_dataset(va_id, ra_id= -1):
    '''
    Retrieves information about the citations
    of a virtual author from the data set.

    In dependency of the real author ID, the information will be written to the
    real author holding this ID. If the real author ID should be the default
    '-1', a list with all the data will be returned.

    @param va_id: Virtual author ID to get the information from
    @type va_id: int
    @param ra_id: Real author ID to set information for.
    @type ra_id: int

    @return: True, if ra_id is set OR A list of the data
    @rtype: True if ra_id > -1 or list of strings
    '''
    va_data = get_virtualauthor_records(va_id)
    authorname_id = -1
    bibrec_id = ""

    for va_data_item in va_data:
        if va_data_item['tag'] == "bibrec_id":
            bibrec_id = va_data_item['value']
        elif va_data_item['tag'] == "orig_authorname_id":
            authorname_id = va_data_item['value']

    bconfig.LOGGER.info("| Reading citation info for va %s: %s recid %s"
                  % (va_id, authorname_id, bibrec_id))

    cites = get_field_values_on_condition(bibrec_id, 'cites')

    if ra_id > -1:
        if cites:
            for cite in cites:
                set_realauthor_data(ra_id, "outgoing_citation", "%s" % (cite))

        return True
    else:
        return cites


def compare_va_to_ra(va_id, ra_id):
    '''
    Compares the data of a virtual author with all the data of
    a real author.

    @param va_id: Virtual author ID
    @type va_id: int
    @param ra_id: Real author ID
    @type ra_id: int

    @return: the probability of the virtual author belonging to the real author
    @rtype: float
    '''
    bconfig.LOGGER.info("|-> Start of citation comparison (va %s : ra %s)"
                  % (va_id, ra_id))

    ra_cites = get_realauthor_data(ra_id, "outgoing_citation")

    try:
        ra_cites_set = set([int(row['value']) for row in ra_cites])
    except ValueError:
        bconfig.LOGGER.exception("A str to int conversion error occured"
                                 "while processing the cites list.")
        return 0.0

    try:
        ra_topcites_set = set([int(row['value']) for row in ra_cites
                               if row['va_count'] > 1])
    except ValueError:
        bconfig.LOGGER.exception("A str to int conversion error occured"
                                 "while processing the topcites list.")
        return 0.0

    va_cites_set = set(get_information_from_dataset(va_id))
    va_cites_len = len(va_cites_set)

    if (not ra_cites) and (not va_cites_len):
        bconfig.LOGGER.info("|-> End of cite comparison (Sets empty)")
        return 0.0

    total_parity = len(ra_cites_set.intersection(va_cites_set))
    total_union = len(ra_cites_set.union(va_cites_set))
    topcite_parity = len(ra_topcites_set.intersection(va_cites_set))
    jaccard_similarity = 0.0
    va_to_ra_topcites_ratio = 0.0

    if total_union > 0.0:
        jaccard_similarity = float(total_parity) / float(total_union)

    if va_cites_len > 0.0:
        va_to_ra_topcites_ratio = float(topcite_parity) / float(va_cites_len)

    certainty = max(jaccard_similarity, va_to_ra_topcites_ratio)

    if certainty > 0.14:
        certainty = sqrt(certainty) + 0.1
    else:
        certainty = 0.0

    if jaccard_similarity >= va_to_ra_topcites_ratio:
        bconfig.LOGGER.info("|--> Found %s matching cites out of %s "
                            "on the paper. Result: %s%% similarity"
                            % (total_parity, va_cites_len, certainty))
    else:
        bconfig.LOGGER.info("|--> Found %s matching top cites out of %s "
                            "on the paper. Result: %s%% similarity"
                            % (topcite_parity, va_cites_len, certainty))

    return min(certainty, 1.0)
