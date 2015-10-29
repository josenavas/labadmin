#!/usr/bin/env python
from StringIO import StringIO
from future.utils import viewitems
from tornado.web import authenticated
from wtforms import (Form, SelectField, FileField, TextField, validators)

from knimin.handlers.base import BaseHandler
from knimin import db


class ThirdPartyData(Form):
    required = validators.required
    survey = SelectField('Third Party survey',
                         choices=[(x, x) for x in db.list_external_surveys()],
                         validators=[required("Required field")])
    file_in = FileField('Third party survey data',
                        validators=[required("Required field")])
    seperator = SelectField('File seperator', choices=[
        ('comma', 'comma'), ('tab', 'tab'), ('space', 'space')],
        validators=[required("Required field")])
    survey_id = TextField('Survey id column name',
                          validators=[required("Required field")])
    trim = TextField('Regex to trim survey id (leave blank for none)')


class NewThirdParty(Form):
    required = validators.required
    name = TextField('Survey Name', validators=[required("Required field")])
    description = TextField('Description',
                            validators=[required("Required field")])
    url = TextField('Survey URL', validators=[required("Required field")])


class AGThirdPartyHandler(BaseHandler):
    @authenticated
    def get(self):
        self.render("ag_third_party.html", the_form=ThirdPartyData(),
                    errors='')

    @authenticated
    def post(self):
        form = ThirdPartyData()
        msg = ''
        args = {a: v[0] for a, v in viewitems(self.request.arguments)}
        form.process(data=args)
        if not form.validate():
            self.render("ag_third_party.html", the_form=form,
                        errors=msg)
            return

        try:
            db.store_external_survey(
                StringIO(form.file_in.data), form.survey.data,
                separator=form.seperator.data,
                survey_id_col=form.survey_id.data, trim=form.trim.data)
        except ValueError as e:
            msg = str(e)
        else:
            msg = "Data added to '%s' successfully" % form.survey.data
        self.render("ag_third_party.html", the_form=form,
                    errors=msg)


class AGNewThirdPartyHandler(BaseHandler):
    @authenticated
    def get(self):
        self.render("new_third_party.html", the_form=NewThirdParty(),
                    errors='')

    @authenticated
    def post(self):
        form = NewThirdParty()
        msg = ''
        args = {a: v[0] for a, v in viewitems(self.request.arguments)}
        form.process(data=args)
        if not form.validate():
            self.render("new_third_party.html", the_form=form,
                        errors=msg)
            return

        try:
            db.add_external_survey(form.name.data, form.description.data,
                                   form.url.data)
        except ValueError as e:
            msg = str(e)
        else:
            msg = "Added '%s' successfully" % form.name.data
        self.render("new_third_party.html", the_form=form,
                    errors=msg)
