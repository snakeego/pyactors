__author__ = 'Andrey Usov <https://github.com/ownport/pyactors>'
__version__ = '0.2'
__license__ = """
Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS 'AS IS'
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE."""


import logging
_logger = logging.getLogger('pyactors.thread')

from multiprocessing import Process
from pyactors.greenlet import GreenletActor
from pyactors.generator import GeneratorActor

class ForkedGeneratorActor(GeneratorActor):
    ''' Forked GeneratorActor
    '''        
    def start(self):
        ''' start actor
        '''
        super(ForkedGeneratorActor, self).start()

        self._process = Process(name=self._name,target=self.run)
        self._process.daemon = False
        self._process.start()

class ForkedGreenletActor(GeneratorActor):
    ''' Forked GreenletActor
    '''        
    def start(self):
        ''' start actor
        '''
        super(ForkedGreenletActor, self).start()

        self._process = Process(name=self._name, target=self.run)
        self._process.daemon = False
        self._process.start()

