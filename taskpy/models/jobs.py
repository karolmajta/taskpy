import os
import taskpy.worker

from taskpy.models.run import RunConfig, RunResult

class Job(object):
	def __init__(self, name, configuration, data={}):
		self.name = name
		self.tasks = [configuration.tasks.get(x) for x in data.get('tasks', [])]
		self.runs = [RunResult(x) for x in data.get('runs', [])]
		self.configuration = configuration

	def as_json(self):
		return  { 'name': self.name
				, 'tasks': [x.name for x in self.tasks]
				, 'runs': [x.as_json() for x in self.runs]
				}

	def update_tasks(self, tasks):
		self.tasks = [self.configuration.tasks.get(x) for x in tasks]

	@property
	def status(self):
		if self.runs:
			return self.runs[-1].state
		return None

	@property
	def last_run(self):
		if self.runs:
			return self.runs[-1].start_time
		return None

	@property
	def folder(self):
		return os.path.join(self.configuration.base_dir, 'jobs', self.name)

	def get_run(self, run_id):
		for run in self.runs:
			if run.run_id == run_id:
				return run
		return None

	def run(self):
		cfg = RunConfig(self)
		task = taskpy.worker.run_job.delay(cfg)
		result = RunResult(data=task.get(), run_id=task.id)
		self.runs.append(result)
		self.configuration.save()