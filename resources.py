from flask_restful import Resource, reqparse, fields, marshal_with, abort

import models

get_parser = reqparse.RequestParser()

get_parser.add_argument('start', type=int, default=0)
get_parser.add_argument('limit', type=int, default=100)

post_queue_parser = reqparse.RequestParser()

post_queue_parser.add_argument('name', type=str, required=True)

queue_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'createdAt': fields.DateTime(dt_format='iso8601'),
    'updatedAt': fields.DateTime(dt_format='iso8601'),
}

queue_post_fields = {
    'name': fields.String
}

queue_get_fields = {
    'start': fields.Integer,
    'limit': fields.Integer,
    'count': fields.Integer,
    'results': fields.List(fields.Nested(queue_fields))
}


class QueueCollection(Resource):
    @marshal_with(queue_get_fields)
    def get(self):
        args = get_parser.parse_args()
        queues = models.Queue.query.offset(args['start']).limit(args['limit']).all()

        res = {
            'start': args['start'],
            'limit': args['limit'],
            'count': len(queues),
            'results': queues
        }

        return res, 200 if len(queues) > 0 else 204

    @marshal_with(queue_fields)
    def post(self):
        args = post_queue_parser.parse_args()
        queue = models.Queue(name=args['name'])
        models.db.session.add(queue)
        models.db.session.commit()

        return queue, 201


class QueueItem(Resource):

    def get_queue(self, queue_id):
        queue = models.Queue.query.filter(models.Queue.id == queue_id).first()

        if not queue:
            abort(404)

        return queue

    @marshal_with(queue_fields)
    def get(self, queue_id):
        return self.get_queue(queue_id)

    @marshal_with(queue_fields)
    def put(self, queue_id):
        args = post_queue_parser.parse_args()
        queue = self.get_queue(queue_id)
        queue.name = args['name']

        models.db.session.commit()

        return queue

    def delete(self, queue_id):
        queue = self.get_queue(queue_id)

        models.db.session.delete(queue)
        models.db.session.commit()
