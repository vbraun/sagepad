#!/usr/bin/env python

import sys
sys.path.append('.')

from sagepad.frontend.app import app

if __name__ == '__main__':
    app.run(debug=True)
