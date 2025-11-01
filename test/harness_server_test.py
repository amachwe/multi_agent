# TEST
from harness import serve
from a2a_grpc.a2a_pb2_grpc import A2AServiceServicer


class Test_A2A_Server(A2AServiceServicer):
    
    def SendMessage(self, request, context):
        print("Test_A2A_Server received SendMessage request:", request)
        # You can add assertions here to validate the request
        

if __name__ == "__main__":
    serve(Test_A2A_Server(), port="50051")