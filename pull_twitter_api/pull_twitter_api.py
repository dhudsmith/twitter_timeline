import os
import pprint
import pandas as pd
from datetime import datetime
import json
import yaml

from tweepy.client import Client

from .utils.config_schema import TwitterPullConfig
from .utils.timeline import Timeline
from .utils.pull_timelines import pull_timelines
from .utils.pull_users import pull_users
from .utils.pull_search import pull_search



class PullTwitterAPI():
	'''
	Python interface class for tool usage within python scripts and notebooks
	'''

	def __init__(self, 
		config: TwitterPullConfig = None,
		config_path: str = None,
		save_format: str = 'csv'):
		"""
		Constructor for PullTwitterAPI

		Parameters:
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
				self.load_config(config_path = config_path)

		# Exract important values from config
		self.query_params = self.config.twitter.query_params
		self.output_dir = str(self.config.local.output_dir)
		self.bearer_token = os.environ['TW_BEARER_TOKEN']


		# Client initialization
		self.client = Client(self.bearer_token, wait_on_rate_limit = True)
		self.save_format = save_format

	# Configuration and directory setup
	
	def load_config(self, 
		config: TwitterPullConfig = None, 
		config_path: str = None) -> None:
		"""
		Load or change the api configuration file

		Parameters:
			-config: TwitterPullConfig
				An instantiated configuration object
			-config_path: str
				Filepath to a configuration yaml file
		"""

		if config:
			self.config = config
		else:
			if config_path:
				self.config = TwitterPullConfig.from_file(config_path)
			else:
				raise ValueError("One of config or config_path must be set.")

	def create_output_dir(self, subcomm: str) -> None:
		"""
		If they do not exist, create all necessary subdirectories to store data and metadata

		Parameters:
			-subcomm: str
				-Subcommand (timeline, users, search) called
		"""

		# Create output directories
		dt_fmt = '%Y-%m-%d %H.%M.%S'
		timestamp = datetime.now().strftime(dt_fmt)
		subcommand_dir = f"{self.output_dir}/{subcomm}"
		output_time_dir = f"{subcommand_dir}/{timestamp}"
		if not os.path.isdir(subcommand_dir):
			os.mkdir(subcommand_dir)

		os.makedirs(output_time_dir)

		return output_time_dir

	def save_meta(self, 
		output_dir: str, 
		subcommand: str = None, 
		**kwargs) -> None:
		"""
		Store the metadata of the request (config and command parameters)

		Parameters:
			-output_dir: str
				Directory where response data should be saved
			-subcommand: str
				Subcommand (timeline, users, search) called
		"""

		# Config storing
		with open(f"{output_dir}/config.yaml", 'w') as f:
			# go through json to convert secret string
			config_secret = json.loads(self.config.json())
			yaml.dump(config_secret, f)


		# Parameter storing
		command = f"Python interface - {subcommand}\n" + '\n'.join([f"{key} : {value}" for key, value in kwargs.items()])

		with open(f"{output_dir}/params.txt", "w") as pf:
			pf.write(command)


	# Subcommands

	def timelines(self, user_csv: str, **kwargs) -> None:
		"""
		Pull timelines of users listed in the passed user_csv

		Parameters:
			-user_csv: str
				-Filepath to the csv containing user handles
		"""

		if not self.config:
			raise ValueError("One of config or config_path must be set.")

		output_dir = self.create_output_dir('timeline')

		all_kwargs = dict({'user_csv': user_csv}, **kwargs)
		self.save_meta(output_dir, subcommand = 'timeline', **all_kwargs)

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

		if not self.config:
			raise ValueError("One of config or config_path must be set.")

		output_dir = self.create_output_dir('users')

		all_kwargs = dict({'user_csv': user_csv}, **kwargs)
		self.save_meta(output_dir, subcommand = 'timeline', **all_kwargs)

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

		if not self.config:
			raise ValueError("One of config or config_path must be set.")

		output_dir = self.create_output_dir('search')

		all_kwargs = dict({'query': query}, **kwargs)
		self.save_meta(output_dir, subcommand = 'timeline', **all_kwargs)

		pull_search(self.client, 
			self.query_params, 
			query,
			save_format = self.save_format,
			output_dir = output_dir, 
			**kwargs)
