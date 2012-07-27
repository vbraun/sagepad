#!./bin/python/bin/python

import os, sys
sys.path.append('src')
sys.path.append('secure')

from sagepad.frontend.app import app
app.config.from_pyfile(os.path.join(os.getcwd(), 'secure', 'flask_config.py'))

if __name__ == '__main__':
    app.run(debug=True)