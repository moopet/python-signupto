from urllib import urlencode
from urllib2 import urlopen


SIGNUPTO_API_ENDPOINT = "http://api.sign-up.to/"


class SignuptoAPIException(Exception):
    pass


class SubscriptionAPI():
    def __init__(self, api_hash, cid, pid=None):
        self.api_hash = api_hash
        self.cid = cid
        self.pid = pid


    def _api_call(self, script, *args, **kwargs):
        url = "{url_part}{script}.php?cid={cid}&hash={api_hash}&{data}".format(
            url_part=SIGNUPTO_API_ENDPOINT,
            script=script,
            cid=self.cid,
            api_hash=self.api_hash,
            data=urlencode(kwargs),
        )
        return urlopen(url).read()


    def _api_call_boolean(self, script, *args, **kwargs):
        """ Internal wrapper for _api_call for when the expected return is
        the common case of 0 or 1.
        """
        result = self._api_call(script, *args, **kwargs)
        if result == '1':
            return True
        elif result == '0':
            return False
        raise SignuptoAPIException(result)


    def check_subscription(self, **kwargs):
        """ Check for a subscription based on one of email or username.
        If you do not specify an (optional) pid, or set pid to 0, then
        all of your lists will be searched for the passed subscriber details.
        """
        return self._api_call_boolean(script='capture', mode='check', **kwargs)


    def add_subscription(self, pid, **kwargs):
        """ Add someone to a list either by email or by mobile.
        Optional parameters are title, first_name, surname, day_birth,
        month_birth, year_birth, house_number, street_name, town, county,
        postcode, phone, company_name, confirm, custom
        See http://www.sign-up.to/knowledge/api/subscription-manager-api/
        """
        return self._api_call_boolean(script='capture', mode='add', pid=pid, **kwargs)


    def remove_subscription(self, **kwargs):
        """ Add someone to a list either by email or by mobile.
        If you do not specify an (optional) pid, or set pid to 0, then
        the passed subscriber details will be removed from all of your lists.
        """
        return self._api_call_boolean(script='capture', mode='remove', **kwargs)


    def add_list(self, **kwargs):
        return self._api_call(script='list', mode='add')


    def get_lists(self, **kwargs):
        """ Return an array of list dictionaries, containing id, name and count
        """
        result = self._api_call(script='list', mode='view')
        lines = [x.split(',') for x in result.split('<br>') if x]
        try:
            return [{'id': x[0], 'name': x[1], 'count': x[2]} for x in lines]
        except IndexError:
            raise SignuptoAPIException(result)


    def empty_list(self, list_id):
        """ Performing this action on the selected list will remove ALL data.
        This action is not recoverable.
        """
        result = self._api_call(script='list', mode='empty', list_id=list_id)
        if result == str(list_id):
            return True
        raise SignuptoAPIException(result)


    def remove_list(self, list_id):
        """ Performing this action on the selected list will remove the list and
        ALL data. This action is not recoverable.
        """
        result = self._api_call(script='list', mode='remove', list_id=list_id)
        if result == str(list_id):
            return True
        raise SignuptoAPIException(result)


    def get_blacklist(self, list_id):
        """ Return a CSV of blacklisted subscribers. In the event that no results
        are found for the search, an error will be returned.
        """
        return self._api_call(script='blacklist')


    def get_subscription_count(self, list_id):
        """ Return the number of subscriptions within the list.
        """
        result = self._api_call(script='list', mode='count', list_id=list_id)
        try:
            return int(result)
        except ValueError:
            raise SignuptoAPIException(result)


    def search(self, **kwargs):
        """
        You may search on:  search_email, search_first_name, search_surname, search_mobile
        If you do not specify an (optional) pid, or set pid to 0, then
        all of your lists will be searched for the passed subscriber details.
        """
        return self._api_call(script='review', **kwargs)


    def import_ftp(self, **kwargs):
        """ Data can be imported from username/password protected FTP sites. Clients
        should be aware that this functionality is provided for maximum compatibility;
        we recommend using the SSH import mechanism.
        Returns an import_id.
        """
        result = self._api_call(script='import', **kwargs)
        try:
            return int(result)
        except ValueError:
            raise SignuptoAPIException(result)


    def import_scp(self, **kwargs):
        """ To use this functionality it is imperative that the csv file is
        hosted on a server that can be accessed by SCP. Clients who wish to
        use this functionality must contact support@sign-up.to in order to
        obtain Signup.to's SSH public key, and provide a source server host name.
        Returns an import_id.
        """
        result = self._api_call(script='import_scp', **kwargs)
        try:
            return int(result)
        except ValueError:
            raise SignuptoAPIException(result)


    def import_complete(self, import_id):
        result = self._api_call(script='import_complete', import_id=import_id)
        if result == import_id:
            return True
        if result == '0':
            return False
        raise SignuptoAPIException(result)
