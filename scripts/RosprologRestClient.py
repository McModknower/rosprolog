import rospy
from json_prolog_msgs.srv import PrologQuery, PrologNextSolution, PrologNextSolutionResponse, PrologFinish
import json
from werkzeug.exceptions import BadRequest

class RosprologRestClient:
	def __init__(self, name_space='rosprolog', timeout=None, wait_for_services=True):
		"""
		@type 	name_space: str
		@param 	timeout: Amount of time in seconds spend waiting for rosprolog to become available.
		@type 	timeout: int
		"""
		self.id = 0
		self._simple_query_srv = rospy.ServiceProxy(
			'{}/query'.format(name_space), PrologQuery)
		self._next_solution_srv = rospy.ServiceProxy(
			'{}/next_solution'.format(name_space), PrologNextSolution)
		self._finish_query_srv = rospy.ServiceProxy(
			'{}/finish'.format(name_space), PrologFinish)
		if wait_for_services:
			rospy.loginfo('waiting for {} services'.format(name_space))
			self._finish_query_srv.wait_for_service(timeout=timeout)
			self._simple_query_srv.wait_for_service(timeout=timeout)
			self._next_solution_srv.wait_for_service(timeout=timeout)
			rospy.loginfo('{} services ready'.format(name_space))

	def post_query(self, query):
		"""
		@param	query: the query string
		@type		query: str
		"""
		self.id += 1
		result = self._simple_query_srv(id=str(self.id), query=query)
		if result.ok:
			return True
		else:
			self.id -= 1
			return False

	def get_solutions(self, max_solution_count):
		"""
		@param	solution_count: the query string
		@type		solution_count: int
		"""
		solutions = []
		try:
			while(len(solutions) < max_solution_count):
				next_solution = self._next_solution_srv(id=str(self.id))
				if next_solution.status == PrologNextSolutionResponse.OK:
					solutions.append(dict(json.loads(next_solution.solution)))
				elif next_solution.status == PrologNextSolutionResponse.NO_SOLUTION:
					break
				else:
					raise BadRequest('Bad query')
		finally:
			self.finish_query()
		return solutions

	def finish_query(self):
		self._finish_query_srv(id=str(self.id))