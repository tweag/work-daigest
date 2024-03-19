import boto3
import json
import logging
from botocore.exceptions import ClientError


logger = logging.getLogger(__name__)


def list_models(client, pattern: str):
    response = client.list_foundation_models()
    return [model['modelId'] for model in response['modelSummaries']
            if pattern in model['modelId'] and 'TEXT' in model['outputModalities']]


def init_client(service_name: str, region_name: str):
    return boto3.client(service_name, region_name=region_name)


def invoke_jurassic2(client, jurassic_model, prompt):
    """
    Invokes the AI21 Labs Jurassic-2 large-language model to run an inference
    using the input provided in the request body.

    :param prompt: The prompt that you want Jurassic-2 to complete.
    :return: Inference response from the model.
    """

    try:
        # The different model providers have individual request and response formats.
        # For the format, ranges, and default values for AI21 Labs Jurassic-2, refer to:
        # https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-jurassic2.html

        body = {
            "prompt": prompt,
            "temperature": 0.5,
            "maxTokens": 1000,
        }

        response = client.invoke_model(
            modelId=jurassic_model, body=json.dumps(body)
        )

        response_body = json.loads(response["body"].read())
        completion = response_body["completions"][0]["data"]["text"]

        return completion

    except ClientError:
        logger.error("Couldn't invoke Jurassic-2")
        raise


def invoke_llama2(client, model_id: str, prompt: str) -> str:
    """
    Invokes the Meta Llama 2 large-language model to run an inference
    using the input provided in the request body.

    :param prompt: The prompt that you want Jurassic-2 to complete.
    :return: Inference response from the model.
    """

    try:
        body = {
            "prompt": prompt,
            "temperature": 0.3,
            "top_p": 0.3,
            "max_gen_len": 1000,
        }

        response = client.invoke_model(
            modelId=model_id, body=json.dumps(body)
        )

        response_body = json.loads(response["body"].read())
        completion = response_body["generation"]

        return completion

    except ClientError:
        logger.error("Couldn't invoke Llama 2")
        raise


if __name__ == '__main__':
    client = init_client('bedrock', 'us-east-1')
    for a in list_models(client, ''):
        print(a)
