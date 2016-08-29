#! /usr/bin/env python
# -*- coding: utf-8 -*-

from flask import request, Blueprint, jsonify

mod = Blueprint('api', __name__, url_prefix='/api')

@mod.route('/v1.0/profile', methods=['GET'])
def get_pear_profile():
    pass

@mod.route('/v1.0/files', methods=['GET'])
def get_pear_files():
    pass
