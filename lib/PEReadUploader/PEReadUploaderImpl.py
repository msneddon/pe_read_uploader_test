#BEGIN_HEADER

from pprint import pprint, pformat


import os
import json
import time
import requests

from os import environ
from ConfigParser import ConfigParser
from requests_toolbelt import MultipartEncoder

from biokbase.workspace.client import Workspace as workspaceService
from biokbase.AbstractHandle.Client import AbstractHandle as HandleService

#END_HEADER


class PEReadUploaderTest:
    '''
    Module Name:
    PEReadUploaderTest

    Module Description:
    A KBase module to wrap the MegaHit package.
    '''

    ######## WARNING FOR GEVENT USERS #######
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    #########################################
    #BEGIN_CLASS_HEADER

    # Helper script borrowed from the transform service, logger removed
    def upload_file_to_shock(self,
                             shock_service_url = None,
                             filePath = None,
                             ssl_verify = True,
                             token = None):
        """
        Use HTTP multi-part POST to save a file to a SHOCK instance.
        """

        if token is None:
            raise Exception("Authentication token required!")

        #build the header
        header = dict()
        header["Authorization"] = "Oauth {0}".format(token)

        if filePath is None:
            raise Exception("No file given for upload to SHOCK!")

        dataFile = open(os.path.abspath(filePath), 'rb')
        m = MultipartEncoder(fields={'upload': (os.path.split(filePath)[-1], dataFile)})
        header['Content-Type'] = m.content_type

        #logger.info("Sending {0} to {1}".format(filePath,shock_service_url))
        try:
            response = requests.post(shock_service_url + "/node", headers=header, data=m, allow_redirects=True, verify=ssl_verify)
            dataFile.close()
        except:
            dataFile.close()
            raise

        if not response.ok:
            response.raise_for_status()

        result = response.json()

        if result['error']:
            raise Exception(result['error'][0])
        else:
            return result["data"]
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.workspaceURL = config['workspace-url']
        self.shockURL = config['shock-url']
        self.handleURL = config['handle-service-url']
        self.scratch = os.path.abspath(config['scratch'])
        # HACK!! temporary hack for issue where megahit fails on mac because of silent named pipe error
        #self.host_scratch = self.scratch
        self.scratch = os.path.join('/kb','module','local_scratch')
        # end hack
        if not os.path.exists(self.scratch):
            os.makedirs(self.scratch)
        #END_CONSTRUCTOR
        pass

    def upload(self, ctx, params):
        # ctx is the context object
        # return variables are: output
        #BEGIN upload
        print('Parameters:')
        pprint(params)

        # 0) download file from shock

        ### NOTE: this section is what could be replaced by the transform services
        forward_reads_file_location = os.path.join(self.scratch,'f1.fq')
        forward_reads_file = open(forward_reads_file_location, 'w', 0)
        print('downloading reads file from staging: '+str(forward_reads_file_location))
        headers = {'Authorization': 'OAuth '+ctx['token']}
        r = requests.get(self.shockURL+'/node/'+params['fastqFile1']+'?download', stream=True, headers=headers)
        for chunk in r.iter_content(1024):
            forward_reads_file.write(chunk)
        forward_reads_file.close();
        print('done downloading')


        # 1) upload files to shock
        token = self.ctx['token']
        forward_shock_file = self.upload_file_to_shock(
            shock_service_url = self.shockURL,
            filePath = forward_reads_file_location,
            token = token
            )
        pprint(forward_shock_file)

        # 2) create handle
        hs = HandleService(url=self.handleURL, token=token)
        forward_handle = hs.persist_handle({
                                        'id' : forward_shock_file['id'], 
                                        'type' : 'shock',
                                        'url' : self.shockURL,
                                        'file_name': forward_shock_file['file']['name'],
                                        'remote_md5': forward_shock_file['file']['checksum']['md5']})

        # 3) save to WS
        paired_end_library = {
            'lib1': {
                'file': {
                    'hid':forward_handle,
                    'file_name': forward_shock_file['file']['name'],
                    'id': forward_shock_file['id'],
                    'url': self.shockURL,
                    'type':'shock',
                    'remote_md5':forward_shock_file['file']['checksum']['md5']
                },
                'encoding':'UTF8',
                'type':'fastq',
                'size':forward_shock_file['file']['size']
            },
            'interleaved':1,
            'sequencing_tech':'artificial reads'
        }

        new_obj_info = self.ws.save_objects({
                        'workspace':params['workspace_name'],
                        'objects':[
                            {
                                'type':'KBaseFile.PairedEndLibrary',
                                'data':paired_end_library,
                                'name':params['read_library_name'],
                                'meta':{},
                                'provenance':[
                                    {
                                        'service':'MegaHit',
                                        'method':'test_megahit'
                                    }
                                ]
                            }]
                        })

        pprint(new_obj_info)

        output = {'temp':'test'};

        #END upload

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method upload return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]
