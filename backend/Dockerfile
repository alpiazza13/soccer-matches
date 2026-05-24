FROM public.ecr.aws/lambda/python:3.13

# Copy dependency matrix
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install packages target-mapped straight into the execution directory
RUN pip install --no-cache-dir -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Copy application source modules
COPY ./app ${LAMBDA_TASK_ROOT}/app

# Command placeholder (Overridden explicitly for each Lambda function)
CMD [ "app.main.handler" ]