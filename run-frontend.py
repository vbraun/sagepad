#!/usr/bin/env python

import os, sys
sys.path.append('src')

from sagepad.frontend.app import app
app.config.from_pyfile(os.path.join(os.getcwd(), 'secure', 'config.py'))

if __name__ == '__main__':
    app.run(debug=True)
