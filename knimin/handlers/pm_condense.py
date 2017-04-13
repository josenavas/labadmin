# -----------------------------------------------------------------------------
# Copyright (c) 2014--, The LabAdmin Development Team.
#
# Distributed under the terms of the BSD 3-clause License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------

from tornado.web import authenticated

from knimin.handlers.base import BaseHandler
from knimin.handlers.access_decorators import set_access
from knimin import db


@set_access(['Admin'])
class PMCondensePlatesHandler(BaseHandler):
    @authenticated
    def get(self):
        dna_plates = db.get_dna_plate_list()
        for plate in dna_plates:
            plate['date'] = plate['date'].isoformat()

        self.render("pm_condense.html",
                    plates=dna_plates,
                    robots=db.get_property_options("processing_robot"))

    @authenticated
    def post(self):
        pass
