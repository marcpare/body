#!/usr/bin/env python

# TODO: could you get rid of the cherrypy server thing?

import cherrypy
import os
import sys
import threading
import traceback
import webbrowser
import csv
from datetime import datetime, timedelta

from base64 import b64encode
import fitbit
from fitbit.api import Fitbit
from oauthlib.oauth2.rfc6749.errors import MismatchingStateError, MissingTokenError


class OAuth2Server:
    def __init__(self, client_id, client_secret,
                 redirect_uri='http://127.0.0.1:8080/'):
        """ Initialize the FitbitOauth2Client """
        self.success_html = """
            <h1>You are now authorized to access the Fitbit API!</h1>
            <br/><h3>You can close this window</h3>"""
        self.failure_html = """
            <h1>ERROR: %s</h1><br/><h3>You can close this window</h3>%s"""

        self.fitbit = Fitbit(
            client_id,
            client_secret,
            redirect_uri=redirect_uri,
            timeout=10,
        )

    def browser_authorize(self):
        """
        Open a browser to the authorization url and spool up a CherryPy
        server to accept the response
        """
        url, _ = self.fitbit.client.authorize_token_url()
        # Open the web browser in a new thread for command-line browser support
        threading.Timer(1, webbrowser.open, args=(url,)).start()
        cherrypy.quickstart(self)

    @cherrypy.expose
    def index(self, state, code=None, error=None):
        """
        Receive a Fitbit response containing a verification code. Use the code
        to fetch the access_token.
        """
        error = None
        if code:
            try:
                self.fitbit.client.fetch_access_token(code)
            except MissingTokenError:
                error = self._fmt_failure(
                    'Missing access token parameter.</br>Please check that '
                    'you are using the correct client_secret')
            except MismatchingStateError:
                error = self._fmt_failure('CSRF Warning! Mismatching state')
        else:
            error = self._fmt_failure('Unknown error while authenticating')
        # Use a thread to shutdown cherrypy so we can return HTML first
        self._shutdown_cherrypy()
        return error if error else self.success_html

    def _fmt_failure(self, message):
        tb = traceback.format_tb(sys.exc_info()[2])
        tb_html = '<pre>%s</pre>' % ('\n'.join(tb)) if tb else ''
        return self.failure_html % (message, tb_html)

    def _shutdown_cherrypy(self):
        """ Shutdown cherrypy in one second, if it's running """
        if cherrypy.engine.state == cherrypy.engine.states.STARTED:
            threading.Timer(1, cherrypy.engine.exit).start()

def export_fitbit_data(client_id, client_secret, access_token, refresh_token):

    authd_client = fitbit.Fitbit(
        client_id,
        client_secret,
        access_token=access_token, 
        refresh_token=refresh_token
    )

    earliest_date = datetime(year=2016, month=1, day=1)
    days30 = timedelta(days=30)

    current_date = earliest_date

    records = []

    while current_date < datetime.utcnow() + days30:
        data = authd_client.get_bodyweight(
            base_date=current_date,
            period="30d")
        current_date += days30


        for d in data['weight']:
            records.append({
                'date': d['date'],
                'fat': d.get('fat', 0),
                'weight': d['weight']
            })

    filename = 'data/fitbit2.csv'
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['date', 'fat', 'weight']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for record in records:
            writer.writerow(record)

    print("Finished exporting data to %s" % filename)

if __name__ == '__main__':

    client_id = os.environ.get('CLIENT_ID')
    client_secret = os.environ.get('CLIENT_SECRET')

    if client_id is None or client_secret is None:
        print("Expecting CLIENT_ID and CLIENT_SECRET")
        sys.exit(1)

    server = OAuth2Server(client_id, client_secret)
    server.browser_authorize()

    profile = server.fitbit.user_profile_get()
    print('You are authorized to access data for the user: {}'.format(
        profile['user']['fullName']))

    tokens = server.fitbit.client.session.token
    access_token = tokens['access_token']
    refresh_token = tokens['refresh_token']

    export_fitbit_data(client_id, client_secret, access_token, refresh_token)




