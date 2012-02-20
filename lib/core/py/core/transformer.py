import json

import webob

import basedec 

class transformer(basedec.BaseDecorator):
	def __init__(self, func):
		self.func = func
		self.json_decoder = json.JSONDecoder()
		self.json_encoder = json.JSONEncoder(sort_keys=True, indent=4)

	def recursive_easydict(self, obj):
		if isinstance(obj, list):
			for (i, item) in enumerate(obj):
				obj[i] = self.recursive_easydict(item)
		elif isinstance(obj, dict):
			obj = core.EasyDict(obj)
			for (key, value) in obj.iteritems():
				obj[key] = self.recursive_easydict(value)
		return obj

	def decode_json(self, json):
		result = self.json_decoder.decode(json)
		return self.recursive_easydict(result)

	def encode_json(self, obj):
		return self.json_encoder.encode(obj)

	def __call__(self, request, *args):
		if request.content_type == 'application/json':
			request.json = self.decode_json(request.body)

		response_code, response_type, response_body = self.func(request, *args)

		if isinstance(response_type, str):
			if response_type == 'application/json':
				response_body = self.encode_json(response_body)			
			return webob.Response(
				status_int=response_code,
				content_type=response_type,
				body=response_body)

		elif isinstance(response_type, dict):
			if response_type['Content-Type'] == 'application/json':
				response_body = self.encode_json(response_body)
			response = webob.Response(status_int=response_code, body=response_body)
			response.headers.update(response_type)
			return response
