from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.errors import AnsibleError, AnsibleFilterError
import subprocess
from tempfile import TemporaryFile

def jq(data, expr):
    ''' Use jq to modify json
    '''
    try:
        p1 = subprocess.Popen(["jq",  expr], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p1.communicate(data)
        if p1.returncode != 0:
            raise AnsibleFilterError('jq returned non-zero exit code:\n%s' % err)
        return out
    except Exception as e:
        raise AnsibleFilterError('Error running jq in filter plugin:\n%s' % e)


class FilterModule(object):
    ''' Query filter '''

    def filters(self):
        return {
            'jq': jq
        }
