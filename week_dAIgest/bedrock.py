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


def invoke_jurassic2(client, prompt: str, model_id: str = "ai21.j2-jumbo-instruct") -> str:
    """
    Invokes the AI21 Labs Jurassic-2 large-language model to run an inference
    using the input provided in the request body.

    :param client: A `boto3.client` object for the `bedrock-runtime` service.
    :param prompt: The prompt that you want Jurassic-2 to complete.
    :param model_id: The model ID of the Jurassic-2 model to invoke.
    :return: Inference response from the model.
    """

    try:
        # The different model providers have individual request and response formats.
        # For the format, ranges, and default values for AI21 Labs Jurassic-2, refer to:
        # https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-jurassic2.html
        # The parameters below are just a (subjectively) relevant subset of the available
        # parameters.
        body = {
            "prompt": prompt,
            "temperature": 0.5,
            "topP": 0.5,
            "maxTokens": 200,
        }

        response = client.invoke_model(
            modelId=model_id, body=json.dumps(body)
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

def invoke_claude3(client, prompt: str, model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0") -> str:
    """
    Invokes the Anthropics Claude-3 large-language model to run an inference
    using the input provided in the request body.

    :param client: `boto3.client` object for the Bedrock service.
    :param claude_model: The model ID for the Claude-3 model you want to use.
    :param prompt: The prompt that you want Claude-3 to complete.
    :return: Inference response from the model.
    """

    try:
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "temperature": 0.3,
            "top_p": 0.3,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        }
        response = client.invoke_model(
            modelId=model_id, body=json.dumps(body)
        )
        response_body = json.loads(response["body"].read())
        completion = response_body["content"][0]["text"]

        return completion

    except ClientError as e:
        logger.error("Couldn't invoke Claude-3")
        raise e

if __name__ == '__main__':
    client = init_client('bedrock', 'us-east-1')
    for a in list_models(client, ''):
        print(a)
