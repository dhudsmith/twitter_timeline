import os
import pprint
import pandas as pd
from datetime import datetime

from tweepy.client import Client

from .utils.config_schema import TwitterPullConfig
from .utils.timeline import Timeline
from .utils.pull_timelines import pull_timelines
from .utils.pull_users import pull_users
from .utils.pull_search import pull_search



class PullTwitterAPI():


	def __init__(self, 
		config: TwitterPullConfig = None,
		config_path: str = None,
		save_format: str = 'csv'):
		"""
		Constructor for PullTwitterAPI

		Parameters:
			-bearer_token: str
				-Bearer token for Twitter API
			-config: TwitterPullConfig
				-Initialized configuration object for queries
			-config_path: str
				-Path to a yaml config file. Should not be set if config parameter is passed
			-save_format: str
				-Format to save query results in. One of ['csv', 'json']
		"""

		# Configuration initialization
		if config:
			self.config = config
		else:
			if config_path:
				self.config = TwitterPullConfig.from_file(config_path)
			else:
				raise ValueError("One of config or config_path must be set.")

		# Exract important values from config
		self.query_params = self.config.twitter.query_params
		self.output_dir = str(self.config.local.output_dir)
		self.bearer_token = os.environ['TW_BEARER_TOKEN']


		# Client initialization
		self.client = Client(self.bearer_token, wait_on_rate_limit = True)
		self.save_format = save_format


	def create_output_dir(self, subcomm):
		# Create output directories
	    dt_fmt = '%Y-%m-%d %H.%M.%S'
	    timestamp = datetime.now().strftime(dt_fmt)
	    subcommand_dir = f"{self.output_dir}/{subcomm}"
	    output_time_dir = f"{subcommand_dir}/{timestamp}"
	    if not os.path.isdir(subcommand_dir):
	        os.mkdir(subcommand_dir)

	    os.makedirs(output_time_dir)

	    return output_time_dir

	def timelines(self, user_csv: str, **kwargs) -> None:
		"""
		Pull timelines of users listed in the passed user_csv

		Parameters:
			-user_csv: str
				-Filepath to the csv containing user handles
		"""

		output_dir = self.create_output_dir('timeline')

		pull_timelines(self.client, 
			self.query_params, 
			user_csv,
			save_format = self.save_format,
			output_dir = output_dir, 
			**kwargs)

	def users(self, user_csv: str, **kwargs) -> None:
		"""
		Pull user information for users listed in the passed user_csv

		Parameters:
			-user_csv: str
				-Filepath to the csv containing user handles
		"""

		output_dir = self.create_output_dir('users')

		pull_users(self.client, 
			self.query_params, 
			user_csv,
			# save_format = self.save_format,
			output_dir = output_dir, 
			**kwargs)

	def search(self, query: str, **kwargs) -> None:
		"""
		Pull tweets satisyfing the given query

		Parameters:
			-query: str
				-The search query to filter tweets
		"""

		output_dir = self.create_output_dir('search')

		pull_search(self.client, 
			self.query_params, 
			query,
			save_format = self.save_format,
			output_dir = output_dir, 
			**kwargs)