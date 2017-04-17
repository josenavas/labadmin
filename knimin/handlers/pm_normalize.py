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
class PMNormalizeHandler(BaseHandler):
    @authenticated
    def get(self):
        plate_id = self.get_argument('plate')

        plate = db.read_shotgun_plate(plate_id)
        plate['created_on'] = plate['created_on'].isoformat(sep=' ')

        condensed = plate['condensed_plates']
        plate['condensed_plates'] = []
        for pid, pos in condensed:
            p = db.read_dna_plate(pid)
            p['created_on'] = p['created_on'].isoformat(sep=' ')
            plate['condensed_plates'].append((pos, p))

        self.render("pm_normalize.html", plate=plate)

    @authenticated
    def post(self):
        input_vol = self.get_argument("pm-volume")
        input_dna = self.get_argument("pm-dna-input")
        upload_type = self.get_argument("upload-select")

        print input_vol
        print input_dna

        if upload_type == 'Single file':
            print self.request.files
            qubit_assay = self.request.files['single-plate-fp'][0]['body']
            print qubit_assay
            # TODO: process single file
        else:
            # TODO: process four files
            qubit_assay_0 = self.request.files['plate-0-fp'][0]['body']
            qubit_assay_1 = self.request.files['plate-1-fp'][0]['body']
            qubit_assay_2 = self.request.files['plate-2-fp'][0]['body']
            qubit_assay_3 = self.request.files['plate-3-fp'][0]['body']
            print qubit_assay_0
            print qubit_assay_1
            print qubit_assay_2
            print qubit_assay_3

        # dna_loaded = self.get_argument('dna-loaded')
        # p1_file = self.request.files['plate-1-file'][0]['body']
        # p2_file = self.request.files['plate-2-file'][0]['body']
        # p3_file = self.request.files['plate-3-file'][0]['body']
        # p4_file = self.request.files['plate-4-file'][0]['body']
        # col_1_file = self.request.files['col-1-file'][0]['body']

        # db.normalize_shotgun_plate(dna_loaded, p1_file, p2_file, p3_file,
        #                            p4_file, col_1_file)
