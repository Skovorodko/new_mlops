from flask_restx import reqparse


def make_req_parser(bundle_errors=True, parser_args=[]):
    parser = reqparse.RequestParser(bundle_errors=bundle_errors)
    for arg_name, kwargs in parser_args:
        parser.add_argument(arg_name, **kwargs)
    return parser


Removing_Parser = make_req_parser(parser_args=[
    [
        'name_model',
        {"type": str,
         "required": True,
         "help": "Model for removing",
         "location": "args"}
    ]
])
Train_Parser = make_req_parser(parser_args=[
    [
        'name_model',
        {"type": str,
         "required": True,
         "help": "Model for training",
         "location": "args"}
    ],
    [
        'path',
        {"type": str,
         "required": True,
         "location": "args"}
    ]
])

Test_Parser = make_req_parser(parser_args=[
    [
        'name_model',
        {"type": str,
         "required": True,
         "help": "Name of a model you want to test",
         "location": "args"},
    ],
    [
        'path',
        {"type": str,
         "required": True,
         "location": "args"}
    ]
])
