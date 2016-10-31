# -*- coding: utf-8 -*-
from unittest import main
from random import choice
from string import ascii_letters

from tornado.escape import url_escape

from knimin import db
from knimin.tests.tornado_test_base import TestHandlerBase
from knimin.handlers.barcode_util import BarcodeUtilHelper


class TestBarcodeUtil(TestHandlerBase):
    def setUp(self):
        self.ag_good = '000001018'
        self.ag_enviro = '000009460'
        self.ag_handout = '000022146'
        self.ag_unassigned = '000022640'
        self.not_ag = '000006155'
        self.not_logged = '000001137'

        self.data = {
            'barcode': self.ag_good,
            'login_email': 'REMOVED',
            'email_type': '1',
            'sample_site': 'Stool',
            'login_user': 'REMOVED',
            'other_text': 'REMOVED',
            'sample_date': '2013-04-18',
            'sample_time': '06:50:00',
            'postmark_date': '',
            'scan_date': '10/25/2015',
            'sent_date': '',
            'sequencing_status': 'SUCCESS',
            'bstatus': 'Recieved',
            'project': 'American Gut Project',
            'obsolete_status': 'N',
            'parent_project': 'American Gut',
            'biomass_remaining': 'Unknown',
        }

        self.data_not_logged = {
            'barcode': self.not_logged,
            'login_email': 'REMOVED',
            'email_type': 0}

        super(TestBarcodeUtil, self).setUp()

    def test_get_not_logged_in(self):
        db.alter_access_levels('test', [3])
        response = self.get('/barcode_util/')
        self.assertEqual(response.code, 200)
        self.assertTrue(
            response.effective_url.endswith('?next=%2Fbarcode_util%2F'))

    def test_get_not_authed(self):
        self.mock_login()
        response = self.get('/barcode_util/')
        self.assertEqual(response.code, 403)

    def test_get(self):
        self.mock_login()
        db.alter_access_levels('test', [3])
        response = self.get('/barcode_util/')
        self.assertEqual(response.code, 200)
        self.assertIn(
            '<input id="barcode" name="barcode" type="text" '
            'onclick="this.select()" />',
            response.body)

        self.assertNotIn('<option value="American Gut Project">'
                         'American Gut Project</option>',
                         response.body)

    def test_get_ag_barcode(self):
        self.mock_login()
        db.alter_access_levels('test', [3])
        response = self.get('/barcode_util/', {'barcode': self.ag_good})
        self.assertEqual(response.code, 200)
        self.assertIn(
            '<input id="barcode" name="barcode" type="text" '
            'onclick="this.select()" />',
            response.body)

        self.assertIn('<input class="checkbox" type="checkbox" name='
                      '"sample_issue" id="overloaded" value="overloaded" }/>',
                      response.body)

        self.assertIn('Project type: American Gut', response.body)
        self.assertIn('All good', response.body)

    def test_get_enviro_barcode(self):
        self.mock_login()
        db.alter_access_levels('test', [3])
        response = self.get('/barcode_util/', {'barcode': self.ag_enviro})
        self.assertEqual(response.code, 200)
        self.assertIn(
            '<input id="barcode" name="barcode" type="text" '
            'onclick="this.select()" />',
            response.body)

        self.assertIn('<input class="checkbox" type="checkbox" name='
                      '"sample_issue" id="overloaded" value="overloaded" }/>',
                      response.body)

        self.assertIn('Project type: American Gut', response.body)
        self.assertIn('All good', response.body)

    def test_get_handout_barcode(self):
        self.mock_login()
        db.alter_access_levels('test', [3])
        response = self.get('/barcode_util/', {'barcode': self.ag_handout})
        self.assertEqual(response.code, 200)
        self.assertIn(
            '<input id="barcode" name="barcode" type="text" '
            'onclick="this.select()" />',
            response.body)

        self.assertNotIn('<input class="checkbox" type="checkbox" name="sample'
                         '_issue" id="overloaded" value="overloaded" }/>',
                         response.body)

        self.assertIn('Project type: American Gut', response.body)
        self.assertIn('Cannot retrieve metadata: Unassigned handout kit '
                      'barcode', response.body)

    def test_get_unassigned_barcode(self):
        self.mock_login()
        db.alter_access_levels('test', [3])
        response = self.get('/barcode_util/', {'barcode': self.ag_unassigned})
        self.assertEqual(response.code, 200)
        self.assertIn(
            '<input id="barcode" name="barcode" type="text" '
            'onclick="this.select()" />',
            response.body)

        self.assertNotIn('<input class="checkbox" type="checkbox" name="sample'
                         '_issue" id="overloaded" value="overloaded" }/>',
                         response.body)

        self.assertIn('Project type: American Gut', response.body)
        self.assertIn('Cannot retrieve metadata: Unassigned handout kit '
                      'barcode', response.body)

    def test_get_non_ag_barcode(self):
        self.mock_login()
        db.alter_access_levels('test', [3])
        response = self.get('/barcode_util/', {'barcode': self.not_ag})
        self.assertEqual(response.code, 200)
        self.assertIn(
            '<input id="barcode" name="barcode" type="text" '
            'onclick="this.select()" />',
            response.body)

        self.assertNotIn('<input class="checkbox" type="checkbox" name="sample'
                         '_issue" id="overloaded" value="overloaded" }/>',
                         response.body)

        self.assertIn('Project type: UNKNOWN', response.body)
        self.assertIn('Barcode Info is correct', response.body)

    def test_post_not_logged_in(self):
        db.alter_access_levels('test', [3])
        response = self.post('/barcode_util/', self.data)
        self.assertEqual(response.code, 403)

    def test_post_not_authed(self):
        self.mock_login()
        response = self.post('/barcode_util/', self.data)
        self.assertEqual(response.code, 403)

    def test_post_update_ag(self):
        db.alter_access_levels('test', [3])
        notes = ''.join([choice(ascii_letters) for x in range(40)])
        self.data['other_text'] = notes
        self.mock_login()
        response = self.post('/barcode_util/', data=self.data)
        self.assertEqual(response.code, 200)
        self.assertIn('Barcode %s general details updated' % self.ag_good,
                      response.body)
        self.assertIn('Barcode %s AG info was successfully updated' %
                      self.ag_good, response.body)
        obs = db.getAGBarcodeDetails(self.ag_good)
        self.assertEqual(obs['other_text'], notes)

    def test_post_update_ag_project_change(self):
        db.alter_access_levels('test', [3])
        self.data['project'] = 'UNKNOWN'
        self.mock_login()
        response = self.post('/barcode_util/', data=self.data)
        self.assertEqual(response.code, 200)
        self.assertIn('Barcode %s general details updated' % self.ag_good,
                      response.body)
        self.assertIn('Project successfully changed', response.body)
        barcode_projects, parent_project = db.getBarcodeProjType(self.ag_good)
        self.assertEqual(barcode_projects, 'UNKNOWN')
        self.assertEqual(parent_project, 'American Gut')

        # reset back
        db.setBarcodeProjects(self.ag_good, rem_projects=['UNKNOWN'])
        barcode_projects, parent_project = db.getBarcodeProjType(self.ag_good)
        self.assertEqual(barcode_projects, '')
        self.assertEqual(parent_project, 'American Gut')

    def test_post_not_logged_barcode(self):
        db.alter_access_levels('test', [3])
        notes = ''.join([choice(ascii_letters) for x in range(40)])
        self.data['other_text'] = notes
        self.mock_login()
        response = self.post('/barcode_util/', data=self.data_not_logged)
        self.assertEqual(response.code, 200)
        # I believe this is correct: the sample is marked as received, as well
        # as status such as moldy/etc but there is no consent or tie sample
        # site. This _should_ trigger an email
        self.assertIn('Barcode %s general details updated' %
                      self.not_logged, response.body)

    def test_build_email(self):
        db.alter_access_levels('test', [3])
        self.mock_login()
        subject, body = BarcodeUtilHelper()._build_email(
            u'persøn', '000001018', '0', '2016-12-14', '6:52 pm')
        self.assertEqual(
            subject, 'ACTION REQUIRED - Assign your samples in American Gut')
        self.assertEqual(
            body, u"""
<html>
<body>
<p>Dear persøn,</p>
<p>We have recently received your sample barcode: 000001018, but we cannot
process your sample until the following steps have been completed online.
Please ensure that you have completed <b>both</b> steps outlined below:</p>
<ol>
<li><b>Submit your consent form and survey-<i>if you have already done these
please proceed to step 2 below.</i></b><br/>For human samples, the consent form
is mandatory. Even if you elect not to answer the questions on the survey,
please click through and submit the survey in order to ensure we receive your
completed consent form.</li>
<li><b>Assign your sample(s) to your survey(s)</b><br/>This step is critical as
it connects your consent form to your sample. We cannot legally work with your
sample until this step has been completed.</li>
</ol>
<p>To assign your sample to your survey:</p>
<ul>
<li>Log into your account and click the &quot;Assign&quot; button at the bottom
of the left-hand navigation menu. This will bring you to a screen with the
heading &quot;Choose your sample source&quot;.</li>
<li>Click on the name of the participant that the sample belongs to.</li>
<li>Fill out the required fields and submit.</li>
</ul>
<p>
The American Gut participant website is located at<br/>
<a href='https://microbio.me/americangut'>https://microbio.me/americangut</a>
<br/>The British Gut participant website is located at<br/>
<a href='https://microbio.me/britishgut'>https://microbio.me/britishgut</a>
<br/>If you have any questions, please contact us at
<a href='mailto:info@americangut.org'>info@americangut.org</a>.</p>
<p>Thank you,<br/>
American Gut Team</p>
</body>
</html>""")

        subject, body = BarcodeUtilHelper()._build_email(
            u'persøn', '000001018', '1', '2016-12-14', '6:52 pm')
        self.assertEqual(
            subject, 'American Gut Sample with Barcode 000001018 is Received.')
        self.assertEqual(
            body, u"""<html><body><p>
Dear persøn,</p>

<p>We have recently received your sample with barcode 000001018 dated
2016-12-14 6:52 pm and we have begun processing it.  Please see our
FAQ section for when you can expect results.<br/>
(<a href='https://microbio.me/AmericanGut/faq/#faq4'
>https://microbio.me/AmericanGut/faq/#faq4</a>)</p>

<p>Thank you for your participation!</p>

<p>--American Gut Team--</p></body></html>
""")

        with self.assertRaises(RuntimeError):
            BarcodeUtilHelper()._build_email(
                u'persøn', '000001018', 'UNKNOWN', '2016-12-14', '6:52 pm')


class BarcodeUtilHandler(TestHandlerBase):
    def test_get_not_authed(self):
        response = self.get('/barcode_util/')
        self.assertEqual(response.code, 200)
        port = self.get_http_port()
        self.assertEqual(response.effective_url,
                         'http://localhost:%d/login/?next=%s' %
                         (port, url_escape('/barcode_util/')))

    def test_get(self):
        self.mock_login_admin()

        # test that only textbox for barcode is show, if no barcode is given.
        response = self.get('/barcode_util/')
        self.assertEqual(response.code, 200)
        self.assertNotIn('<h2 class="verification_text">', response.body)
        self.assertNotIn('<form action="/barcode_util/" method="post"',
                         response.body)

        # test display of non existing barcode on website
        barcode = 'NotInDB'
        response = self.get('/barcode_util/', {'barcode': barcode})
        self.assertEqual(response.code, 200)
        self.assertIn('Barcode %s does not exist in the database' % barcode,
                      response.body)
        self.assertIn('<h2 class="verification_text">', response.body)
        self.assertNotIn('<form action="/barcode_util/" method="post"',
                         response.body)
        self.assertIn('Project type: None', response.body)
        self.assertIn('Subprojects: []', response.body)
        self.assertIn('Barcode: %s' % barcode, response.body)

        # TODO: I think we have a problem with spelling the word 'received'!
        # barcode_status_received = '000000001'

        # check that neighter option from the combobox is selected, if status
        # is empty
        barcode_status_empty = "000001003"
        response = self.get('/barcode_util/',
                            {'barcode': barcode_status_empty})
        self.assertEqual(response.code, 200)
        self.assertIn('<option value="Recieved">Recieved</option>',
                      response.body)
        self.assertIn('<option value=""></option>', response.body)

        # check that neighter option from the combobox is selected, if status
        # is an empty quote
        barcode_status_quote = "000001420"
        response = self.get('/barcode_util/',
                            {'barcode': barcode_status_quote})
        self.assertEqual(response.code, 200)
        self.assertIn('<option value="Recieved">Recieved</option>',
                      response.body)
        self.assertIn('<option value="" selected></option>', response.body)

        # test correct option is set for barcodes with biomass remainings
        barcode_biomass_Y = "000003336"
        response = self.get('/barcode_util/',
                            {'barcode': barcode_biomass_Y})
        self.assertEqual(response.code, 200)
        self.assertIn('<option value="N" >No</option>', response.body)
        self.assertIn('<option value="Y" selected>Yes</option>',
                      response.body)
        self.assertIn('<option value="Unknown" >Unknown</option>',
                      response.body)

        # test correct option is set for barcodes without biomass remainings
        barcode_biomass_N = "000004244"
        response = self.get('/barcode_util/',
                            {'barcode': barcode_biomass_N})
        self.assertEqual(response.code, 200)
        self.assertIn('<option value="N" selected>No</option>', response.body)
        self.assertIn('<option value="Y" >Yes</option>', response.body)
        self.assertIn('<option value="Unknown" >Unknown</option>',
                      response.body)

        # test correct option is set for barcodes without info about biomass
        # remainings
        barcode_biomass_empty = "000004242"
        response = self.get('/barcode_util/',
                            {'barcode': barcode_biomass_empty})
        self.assertEqual(response.code, 200)
        self.assertIn('<option value="N" >No</option>', response.body)
        self.assertIn('<option value="Y" >Yes</option>', response.body)
        self.assertIn('<option value="Unknown" selected>Unknown</option>',
                      response.body)

        # check if sequencing status is set to ''
        # (TODO: currently it is set to WAITING, which seems to be wrong!)
        barcode_seqstatus_quote = "000012397"  # ''
        response = self.get('/barcode_util/',
                            {'barcode': barcode_seqstatus_quote})
        self.assertEqual(response.code, 200)
        self.assertIn('<option value="WAITING" >WAITING</option>',
                      response.body)
        self.assertIn('<option value="SUCCESS" >SUCCESS</option>',
                      response.body)
        self.assertIn('<option value="FAILED_SEQUENCING" >%s</option>' %
                      'FAILED_SEQUENCING',
                      response.body)
        self.assertIn('<option value="" selected></option>',
                      response.body)

        # check if sequencing status is set to ''
        # (TODO: currently it is set to WAITING, which seems to be wrong!)
        barcode_seqstatus_empty = "000001131"  #
        response = self.get('/barcode_util/',
                            {'barcode': barcode_seqstatus_empty})
        self.assertEqual(response.code, 200)
        self.assertIn('<option value="WAITING" >WAITING</option>',
                      response.body)
        self.assertIn('<option value="SUCCESS" >SUCCESS</option>',
                      response.body)
        self.assertIn('<option value="FAILED_SEQUENCING" >%s</option>' %
                      'FAILED_SEQUENCING',
                      response.body)
        self.assertIn('<option value="" ></option>',
                      response.body)

        # check if sequencing status is set to 'FAILED_SEQUENCING'
        barcode_seqstatus_fail = "000001139"  # FAILED_SEQUENCING
        response = self.get('/barcode_util/',
                            {'barcode': barcode_seqstatus_fail})
        self.assertEqual(response.code, 200)
        self.assertIn('<option value="WAITING" >WAITING</option>',
                      response.body)
        self.assertIn('<option value="SUCCESS" >SUCCESS</option>',
                      response.body)
        self.assertIn('<option value="FAILED_SEQUENCING" selected>%s</option>'
                      % 'FAILED_SEQUENCING',
                      response.body)
        self.assertIn('<option value="" ></option>',
                      response.body)

        # check if sequencing status is set to 'FAILED_SEQUENCING'
        # (TODO: currently it is set to nothing, which seems to be wrong!)
        barcode_seqstatus_fail1 = "000004053"  # FAILED_SEQUENCING_1
        response = self.get('/barcode_util/',
                            {'barcode': barcode_seqstatus_fail1})
        self.assertEqual(response.code, 200)
        self.assertIn('<option value="WAITING" >WAITING</option>',
                      response.body)
        self.assertIn('<option value="SUCCESS" >SUCCESS</option>',
                      response.body)
        self.assertIn('<option value="FAILED_SEQUENCING" >%s</option>' %
                      'FAILED_SEQUENCING',
                      response.body)
        self.assertIn('<option value="" ></option>',
                      response.body)

        # check if sequencing status is set to 'FAILED_SEQUENCING'
        # (TODO: currently it is set to nothing, which seems to be wrong!)
        barcode_seqstatus_fail2 = "000004244"  # FAILED_SEQUENCING_2
        response = self.get('/barcode_util/',
                            {'barcode': barcode_seqstatus_fail2})
        self.assertEqual(response.code, 200)
        self.assertIn('<option value="WAITING" >WAITING</option>',
                      response.body)
        self.assertIn('<option value="SUCCESS" >SUCCESS</option>',
                      response.body)
        self.assertIn('<option value="FAILED_SEQUENCING" >%s</option>' %
                      'FAILED_SEQUENCING',
                      response.body)
        self.assertIn('<option value="" ></option>',
                      response.body)

        # check if sequencing status is set to 'SUCCESS'
        barcode_seqstatus_succ = "000004234"  # SUCCESS
        response = self.get('/barcode_util/',
                            {'barcode': barcode_seqstatus_succ})
        self.assertEqual(response.code, 200)
        self.assertIn('<option value="WAITING" >WAITING</option>',
                      response.body)
        self.assertIn('<option value="SUCCESS" selected>SUCCESS</option>',
                      response.body)
        self.assertIn('<option value="FAILED_SEQUENCING" >%s</option>' %
                      'FAILED_SEQUENCING',
                      response.body)
        self.assertIn('<option value="" ></option>',
                      response.body)
        # check if sequencing status is set to 'WAITING'
        barcode_seqstatus_wait = "000004247"  # WAITING
        response = self.get('/barcode_util/',
                            {'barcode': barcode_seqstatus_wait})
        self.assertEqual(response.code, 200)
        self.assertIn('<option value="WAITING" selected>WAITING</option>',
                      response.body)
        self.assertIn('<option value="SUCCESS" >SUCCESS</option>',
                      response.body)
        self.assertIn('<option value="FAILED_SEQUENCING" >%s</option>' %
                      'FAILED_SEQUENCING',
                      response.body)
        self.assertIn('<option value="" ></option>',
                      response.body)

        # check if barcode is marked as obsolete
        # TODO: is that correct if the info in DB is ''?
        barcode_obsolete_empty = "000012395"  #
        response = self.get('/barcode_util/',
                            {'barcode': barcode_obsolete_empty})
        self.assertEqual(response.code, 200)
        self.assertIn('<option value="N" selected>No</option>', response.body)
        self.assertIn('<option value="Y" >Yes</option>', response.body)

        # check if barcode is marked as obsolete
        barcode_obsolete_N = "000012397"  # "N"
        response = self.get('/barcode_util/',
                            {'barcode': barcode_obsolete_N})
        self.assertEqual(response.code, 200)
        self.assertIn('<option value="N" selected>No</option>', response.body)
        self.assertIn('<option value="Y" >Yes</option>', response.body)

        # check if barcode is marked as obsolete
        barcode_obsolete_Y = "000012412"  # "Y"
        response = self.get('/barcode_util/',
                            {'barcode': barcode_obsolete_Y})
        self.assertEqual(response.code, 200)
        self.assertIn('<option value="N" >No</option>', response.body)
        self.assertIn('<option value="Y" selected>Yes</option>', response.body)

        # test display of non american gut barcode
        barcode_nonAGP = "000004369"
        response = self.get('/barcode_util/',
                            {'barcode': barcode_nonAGP})
        self.assertEqual(response.code, 200)
        self.assertIn('Barcode Info is correct</h2>', response.body)

        # test display of american gut barcode
        barcode_AGP = "000001001"
        response = self.get('/barcode_util/',
                            {'barcode': barcode_AGP})
        self.assertEqual(response.code, 200)
        self.assertIn('All good</h2>', response.body)


if __name__ == '__main__':
    main()
