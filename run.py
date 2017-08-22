#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author:
# @file:run.py
# @time:2017/8/22
from KBase import app
import click

@click.command()
@click.option('--port', '-p', default='5000', help='listening port')

def run(port):
    app.run(debug=True, port=port, host='0.0.0.0')

if __name__ == '__main__':
    run()