#!/usr/bin/env python3

import grpc
from concurrent import futures
import json
import time
from .generated import json_transfer_pb2, json_transfer_pb2_grpc

class JsonTransferService(json_transfer_pb2_grpc.JsonTransferServicer):
    def StartJsonStream(self, request, context):
        if request.command != "start":
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Invalid command. Use 'start' to begin streaming.")
            return

        sample_data = [
            {"id": 1, "timestamp": time.time(), "data": "sample1"},
            {"id": 2, "timestamp": time.time(), "data": "sample2"},
            {"id": 3, "timestamp": time.time(), "data": "sample3"}
        ]

        for data in sample_data:
            try:
                json_str = json.dumps(data)
                yield json_transfer_pb2.JsonResponse(
                    json_data=json_str,
                    success=True,
                    message="Data sent successfully"
                )
                time.sleep(1)
            except Exception as e:
                yield json_transfer_pb2.JsonResponse(
                    json_data="",
                    success=False,
                    message=f"Error processing data: {str(e)}"
                )

def main():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    json_transfer_pb2_grpc.add_JsonTransferServicer_to_server(
        JsonTransferService(), server
    )
    server.add_insecure_port('[::1]:50051')
    server.start()
    print("Server started on port 50051")
    server.wait_for_termination()

if __name__ == '__main__':
    main()
