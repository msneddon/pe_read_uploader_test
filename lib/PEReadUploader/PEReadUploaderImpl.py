#BEGIN_HEADER

from pprint import pprint, pformat


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
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        #END_CONSTRUCTOR
        pass

    def upload(self, ctx, params):
        # ctx is the context object
        # return variables are: output
        #BEGIN upload
        print('Parameters:')
        pprint(params)

        output = {'temp':'test'};

        #END upload

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method upload return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]
