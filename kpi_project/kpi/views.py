from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import KPI, Asset , Message
from .serializers import KPISerializer
import json
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .message_processor import MessageProcessor  
from datetime import datetime
from .validators import is_valid_equation  
import os
from django.conf import settings

class IngestMessageView(APIView):
    @swagger_auto_schema(
        operation_description="Ingest a message, process it, and save the result in the database.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "asset_id": openapi.Schema(type=openapi.TYPE_STRING, description="The ID of the asset"),
                "attribute_id": openapi.Schema(type=openapi.TYPE_STRING, description="The attribute ID"),
                "timestamp": openapi.Schema(type=openapi.TYPE_STRING, format="date-time", description="The timestamp of the message (e.g., 2022-07-31T23:28:37Z[UTC])"),
                "value": openapi.Schema(type=openapi.TYPE_STRING, description="The value to be processed")
            },
            required=["asset_id", "attribute_id", "timestamp", "value"]
        ),
        responses={
            201: openapi.Response(description="Message successfully ingested and saved."),
            400: openapi.Response(description="Invalid message format."),
            500: openapi.Response(description="Internal server error during message processing.")
        }
    )
    def post(self, request):
        message = request.data

        # Validate the message
        required_fields = ["asset_id", "attribute_id", "timestamp", "value"]
        if not all(field in message for field in required_fields):
            return Response({"error": "Invalid message format"}, status=status.HTTP_400_BAD_REQUEST)

        # Read the equation from the configuration file
        equation = read_equation_from_config()
        processor = MessageProcessor(equation)

        try:
            # Process the message
            result_value = processor.process_message(message)

            # Construct the output message
            output_message = {
                "asset_id": message["asset_id"],
                "attribute_id": "output_" + message["attribute_id"],
                "timestamp": message["timestamp"],
                "value": result_value
            }

            # Save the message to the database
            Message.objects.create(
                asset_id=output_message["asset_id"],
                attribute_id=output_message["attribute_id"],
                timestamp=datetime.fromisoformat(output_message["timestamp"].replace("Z[UTC]", "+00:00")),
                value=output_message["value"]
            )

            return Response(output_message, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class KPIListCreateView(APIView):
    @swagger_auto_schema(
        operation_description="Retrieve a list of all KPIs.",
        responses={
            200: KPISerializer(many=True)  # Indicating that the response returns a list of KPIs
        }
    )
    def get(self, request):
        
        kpis = KPI.objects.all()
        serializer = KPISerializer(kpis, many=True)
        return Response(serializer.data)
    @swagger_auto_schema(
        operation_description="Create a new KPI.",
        request_body=KPISerializer,  # The serializer that defines the request body
        responses={
            201: KPISerializer,  # Response when the KPI is created successfully
            400: "Bad Request"  # Response when the input data is invalid
        }
    )
    def post(self, request):
        serializer = KPISerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LinkAssetToKPIView(APIView):
    @swagger_auto_schema(
    operation_description="Link an Asset to a KPI using their IDs.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "kpi_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="The ID of the KPI to link"),
            "asset_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="The ID of the Asset to link")
        },
        required=["kpi_id", "asset_id"]
    ),
    responses={
        200: openapi.Response(description="Asset linked to KPI successfully."),
        400: openapi.Response(description="Both 'kpi_id' and 'asset_id' are required."),
        404: openapi.Response(description="KPI or Asset not found."),
        500: openapi.Response(description="Internal server error.")
    }
    )
    def post(self, request):
        kpi_id = request.data.get('kpi_id')
        asset_id = request.data.get('asset_id')

        if not kpi_id or not asset_id:
            return Response({"error": "Both 'kpi_id' and 'asset_id' are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the KPI and Asset objects
            kpi = KPI.objects.get(id=kpi_id)
            asset = Asset.objects.get(id=asset_id)

            # Link the asset to the KPI
            kpi.asset = asset
            kpi.save()

            return Response({"message": "Asset linked to KPI successfully."}, status=status.HTTP_200_OK)
        except KPI.DoesNotExist:
            return Response({"error": "KPI not found."}, status=status.HTTP_404_NOT_FOUND)
        except Asset.DoesNotExist:
            return Response({"error": "Asset not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateConfigView(APIView):
    @swagger_auto_schema(
    operation_description="Update the configuration file (config.json) with a new equation.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "equation": openapi.Schema(type=openapi.TYPE_STRING, description="The new equation to be updated in the config.")
        },
        required=["equation"]
    ),
    responses={
        200: openapi.Response(description="Configuration updated successfully."),
        400: openapi.Response(
            description="Bad request with validation errors.",
            examples={
                "application/json": {
                    "error": "The provided equation is not valid.",
                    "valid_examples": [
                        "ATTR + 5",
                        "Regex(\"ATTR\", \"^pattern\")"
                    ],
                    "note": "Valid equations should either be an arithmetic expression containing 'ATTR', or a Regex pattern of the format 'Regex(\"ATTR\", \"pattern\")'."
                }
            }
        ),
        500: openapi.Response(description="Internal server error.")
    }
    )
    def post(self, request):
        new_equation = request.data.get("equation")

        if not new_equation:
            return Response(
                {"error": "The 'equation' field is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate the equation
        if not is_valid_equation(new_equation):
            return Response(
                {
                    "error": "The provided equation is not valid.",
                    "valid_examples": [
                        "ATTR + 5",  # Example of a valid arithmetic expression
                        "Regex(\"ATTR\", \"^pattern\")"  # Example of a valid regex pattern
                    ],
                    "note": "Valid equations should either be an arithmetic expression containing 'ATTR', or a Regex pattern of the format 'Regex(\"ATTR\", \"pattern\")'."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Construct the path to the config file
        config_path = os.path.join(settings.BASE_DIR, 'config.json')

        try:
            # Read the existing config file
            with open(config_path, 'r') as file:
                config = json.load(file)

            # Update the equation in the config
            config['equation'] = new_equation

            # Write the updated config back to the file
            with open(config_path, 'w') as file:
                json.dump(config, file, indent=4)

            return Response({"message": "Configuration updated successfully."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
def read_equation_from_config():
    """
    Reads the equation from the config file.

    Returns:
        str: The equation as read from the config file.
    """
    with open('config.json', 'r') as file:
        config = json.load(file)
    return config['equation']
