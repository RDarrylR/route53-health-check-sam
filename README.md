# Route53 Health Check SAM

### Purpose


### Key Files

- `site_health_check` - Source for the AWS Lambda function
- `samconfig.toml` - Project configuration file.
- `template.yaml` - A template that defines the application's AWS resources.

### Requirements

-   [SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)

### Deploy the sample project

To deploy the projecy, you need the following tools:

```bash
 sam build
 sam deploy
```

### Cleanup

To delete the sample project please use the AWS CLI or Console and delete the Cloudformation stack SAM created. You can also use the SAM CLI as below but please ensure all the resoures are actually gone in the AWS CLI/Console to ensure you have no ongoing AWS charges

```bash
sam delete
```

### Read More

This repository is associated with the following blog [posted here](https://darryl-ruggles.cloud/preview/655cb4d2033e7b0010677e5e/q