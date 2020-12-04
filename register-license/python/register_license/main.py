# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.application import Service
import requests
import urllib3
import json
import sys

# ------------------------
# SERVICE CALLBACK EXAMPLE
# ------------------------
class ServiceCallbacks(Service):

    # The create() callback is invoked inside NCS FASTMAP and
    # must always exist.
    @Service.create
    def cb_create(self, tctx, root, service, proplist):
        self.log.info('Service create(service=', service._path, ')')

        device_group = service.device_group
        self.log.info('*** Register_license, device-group: ', device_group)
        idtoken = root.devreglic.inventory.device_groups.device_group[device_group].idtoken
        self.log.info('*** Register_license, idtoken from Inventory: ', idtoken)


        urllib3.disable_warnings()

        client_id = "CMWk9L0mJ6Ynn8SwEnjd32-f_IqlNXWczjV6nC74ve7tFR--1c0LW8qp18N5_y1G"
        client_secret = "7vtLXBnNzDXJ7wu5j9YsmV0cb24YEBKoZFvVihrbbt7yt677fAfZuwsUrKOi8Lvv"
        host = "10.101.1.107"
        port = "8443"
        smartAccountName = "InternalTestDemoAccount9.cisco.com"
        virtualAccountName = "Default"
        accessCodeOk = True

        # url = f'https://{host}:{port}/oauth/token'
        url = "https://" + host + ":" + port + "/oauth/token"
        self.log.info("access_token url: ", url)

        payload = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials"
        }
        headers = {
        'Content-Type': 'application/json'
        }

        try:
            response = requests.request("POST", url, headers=headers, data = json.dumps(payload), verify = False)
            status_code = response.status_code
            self.log.info("status_code: ", status_code)
            if (status_code == 200):
                jsonResponse = response.json()
                access_token = jsonResponse["access_token"]
                self.log.info("access_token: ", access_token)
            else:
                self.log.info('Something went wrong: ', status_code)
                accessCodeOk = False
        except requests.exceptions.HTTPError as err:
            self.log.info("Error in connection --> "+str(err))
            accessCodeOk = False

        if (accessCodeOk):
            # url = f'https://{host}:{port}/api/v1/accounts/{smartAccountName}/virtual-accounts/{virtualAccountName}/tokens'
            url = "https://" + host + ":" + port + "/api/v1/accounts/" + smartAccountName + "/virtual-accounts/" + virtualAccountName + "/tokens"
            self.log.info("token url: ", url)

            payload = {}
            headers = {
            'Authorization': 'Bearer '+access_token
            }

            try:
                response = requests.request("GET", url, headers=headers, data = payload, verify = False)
                status_code = response.status_code
                self.log.info("status_code: ", status_code)
                if (status_code == 200):
                    jsonResponse = response.json()
                    self.log.info("Length of Token List: ", len(jsonResponse["tokens"]))
                    numTokens = len(jsonResponse["tokens"])
                    if numTokens>0:
                        register_token = jsonResponse["tokens"][0]["token"]
                        self.log.info("First token: ", register_token)
                        regTokenOK = True
                    else:
                        regTokenOK = False
                else:
                    self.log.info('Something went wrong: ', status_code)
                    regTokenOK = False
            except requests.exceptions.HTTPError as err:
                self.log.info("Error in connection --> "+str(err))
                regTokenOK = False

        if (regTokenOK == False):
            # url = f'https://{host}:{port}/api/v1/accounts/{smartAccountName}/virtual-accounts/{virtualAccountName}/tokens'
            url = "https://" + host + ":" + port + "/api/v1/accounts/" + smartAccountName + "/virtual-accounts/" + virtualAccountName + "/tokens"
            self.log.info("generate token url: ", url)

            payload = {
                "expiresAfterDays": 1,
                "description": "Test VA Creation",
                "exportControlled": "Allowed"
            }

            headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer '+access_token
            }

            try:
                response = requests.request("POST", url, headers=headers, data = json.dumps(payload), verify = False)
                status_code = response.status_code
                self.log.info("status_code: ", status_code)
                if (status_code == 200):
                    jsonResponse = response.json()
                    register_token = jsonResponse["tokenInfo"]["token"]
                    self.log.info("Token: ", register_token)
                    idtoken = register_token
                else:
                    self.log.info('Something went wrong: ', status_code)
            except requests.exceptions.HTTPError as err:
                self.log.info("Error in connection --> "+str(err))
                regTokenOK = False
                sys.exit()
            finally:
                if response : response.close()
        else:
            idtoken = register_token


        self.log.info('*** Register_license, idtoken from License Server: ', idtoken)

        with ncs.maapi.single_read_trans('admin', 'python') as t: 
            root = ncs.maagic.get_root(t) 
            devs = root.devices.device 
            devgroups = root.devices.device_group 
            for device in devgroups[device_group].device_name:
                self.log.info('*** Register_license, device: ', device)
                any = devs[device].live_status.cisco_ios_xr_stats__exec.any 
                inp = any.get_input() 
                inp.args = ['license smart register idtoken '+idtoken] 
                r = any.request(inp) 
                self.log.info('RESULT: ', r.result)

        # vars = ncs.template.Variables()
        # vars.add('DUMMY', '127.0.0.1')
        # template = ncs.template.Template(service)
        # template.apply('register-license-template', vars)

    # The pre_modification() and post_modification() callbacks are optional,
    # and are invoked outside FASTMAP. pre_modification() is invoked before
    # create, update, or delete of the service, as indicated by the enum
    # ncs_service_operation op parameter. Conversely
    # post_modification() is invoked after create, update, or delete
    # of the service. These functions can be useful e.g. for
    # allocations that should be stored and existing also when the
    # service instance is removed.

    # @Service.pre_lock_create
    # def cb_pre_lock_create(self, tctx, root, service, proplist):
    #     self.log.info('Service plcreate(service=', service._path, ')')

    # @Service.pre_modification
    # def cb_pre_modification(self, tctx, op, kp, root, proplist):
    #     self.log.info('Service premod(service=', kp, ')')

    # @Service.post_modification
    # def cb_post_modification(self, tctx, op, kp, root, proplist):
    #     self.log.info('Service premod(service=', kp, ')')


# ---------------------------------------------
# COMPONENT THREAD THAT WILL BE STARTED BY NCS.
# ---------------------------------------------
class Main(ncs.application.Application):
    def setup(self):
        # The application class sets up logging for us. It is accessible
        # through 'self.log' and is a ncs.log.Log instance.
        self.log.info('Main RUNNING')

        # Service callbacks require a registration for a 'service point',
        # as specified in the corresponding data model.
        #
        self.register_service('register-license-servicepoint', ServiceCallbacks)

        # If we registered any callback(s) above, the Application class
        # took care of creating a daemon (related to the service/action point).

        # When this setup method is finished, all registrations are
        # considered done and the application is 'started'.

    def teardown(self):
        # When the application is finished (which would happen if NCS went
        # down, packages were reloaded or some error occurred) this teardown
        # method will be called.

        self.log.info('Main FINISHED')
