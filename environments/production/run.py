#!/usr/bin/env python
# Run script for production environment

from app import create_app
from environments.production.config import ProductionConfig

app = create_app(ProductionConfig)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=80)