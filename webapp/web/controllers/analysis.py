# Import modules for running the Flask webapp
from __future__ import print_function, division
import os, sys, flask
from flask import request, render_template, send_from_directory, current_app, session


analysis_page = flask.Blueprint("analysis_page", __name__)
@analysis_page.route('/analysis.html')
def func_name():
	templateDict = {}

	return render_template("analysis.html", **templateDict)




