# -----------------------------------------------------------------------------
# Copyright (c) 2014--, The LabAdmin Development Team.
#
# Distributed under the terms of the BSD 3-clause License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------

from tornado.web import authenticated
from tornado.escape import json_decode

from knimin.lib.parse import parse_plate_reader_output
from knimin.handlers.base import BaseHandler
from knimin.handlers.access_decorators import set_access
from knimin import db


def _get_targeted_plates(plates_arg):
    all_plates = []
    plates = []
    for plate in db.get_targeted_plate_list():
        plate['date'] = plate['date'].isoformat()
        all_plates.append(plate)
        if plate['id'] in plates_arg:
            plates.append(plate)

    return all_plates, plates


@set_access(['Admin'])
class PMTargetedConcentrationHandler(BaseHandler):
    @authenticated
    def get(self):
        plates_arg = map(int, self.get_arguments('plate'))
        all_plates, plates = _get_targeted_plates(plates_arg)

        self.render("pm_targeted_concentration.html", all_plates=all_plates,
                    plates=plates)

    @authenticated
    def post(self):
        plates = self.get_arguments('plate')

        file_contents = self.request.files['plate-reader-fp'][0]['body']
        plate_reader_data = parse_plate_reader_output(file_contents)

        for p, d in zip(plates, [plate_reader_data]):
            print "db.write_targeted_plate_concentration(p, d)"

        self.redirect(
            "/pm_targeted_concentration_check/?%s"
            % "&".join(["plate=%s" % pid for pid in plates]))


@set_access(['Admin'])
class PMTargetedConcentrationCheckHandler(BaseHandler):
    @authenticated
    def get(self):
        plates_arg = map(int, self.get_arguments('plate'))
        _, plates = _get_targeted_plates(plates_arg)

        import numpy as np

        v = np.around(
           np.random.rand(8, 12) * 10, decimals=3).tolist()
        plates = [
            {'id': 1, 'name': 'Test plate', 'email': 'test',
             'dna_plate_id': 1, 'primer_plate_id': 1,
             'master_mix_lot': '14459', 'robot': 'ROBE',
             'tm300_8_tool': '208484Z', 'tm50_8_tool': '108364Z',
             'water_lot': 'RNBD9959',
             'raw_concentration': np.around(
                np.random.rand(8, 12), decimals=3).tolist(),
             'mod_concentration': None,
             'rows': 8, 'cols': 12,
             'blanks': [['BLANK', 0, 0], ['BLANK', 0, 3],
                        ['BLANK', 1, 0], ['BLANK', 1, 3],
                        ['BLANK', 2, 0], ['BLANK', 2, 3],
                        ['BLANK', 3, 0], ['BLANK', 3, 3],
                        ['BLANK', 4, 0], ['BLANK', 4, 3],
                        ['BLANK', 5, 0], ['BLANK', 5, 3],
                        ['BLANK', 6, 0], ['BLANK', 6, 3],
                        ['BLANK', 7, 0], ['BLANK', 7, 3]]},
            {'id': 2, 'name': 'Test plate 2', 'email': 'test',
             'dna_plate_id': 2, 'primer_plate_id': 1,
             'master_mix_lot': '14459', 'robot': 'ROBE',
             'tm300_8_tool': '208484Z', 'tm50_8_tool': '108364Z',
             'water_lot': 'RNBD9959',
             'raw_concentration': v,
             'mod_concentration': None,
             'rows': 8, 'cols': 12,
             'blanks': [['BLANK', 0, 0], ['BLANK', 0, 3],
                        ['BLANK', 1, 0], ['BLANK', 1, 3],
                        ['BLANK', 2, 0], ['BLANK', 2, 3],
                        ['BLANK', 3, 0], ['BLANK', 3, 3],
                        ['BLANK', 4, 0], ['BLANK', 4, 3],
                        ['BLANK', 5, 0], ['BLANK', 5, 3],
                        ['BLANK', 6, 0], ['BLANK', 6, 3],
                        ['BLANK', 7, 0], ['BLANK', 7, 3]]}]

        self.render("pm_targeted_concentration_check.html", plates=plates)

    @authenticated
    def post(self):
        plates = json_decode(self.get_argument('plates'))
        print plates
