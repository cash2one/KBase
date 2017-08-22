# -*- coding:utf-8 -*-
# @author:
# @file:__init__.py
# @time:2017/8/22
from flask import Flask
import click
# from flask import current_app

app = Flask(__name__)

import KBase.views

if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler

    file_handler = RotatingFileHandler('itkbase.log', 'a',
                                       1 * 1024 * 1024, 10)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('KBase startup')

click.disable_unicode_literals_warning = True
app.config.from_pyfile('app.cfg')

# def get_css_framework():
#     return current_app.config.get('CSS_FRAMEWORK', 'bootstrap3')
#
# def get_link_size():
#     return current_app.config.get('LINK_SIZE', 'sm')
