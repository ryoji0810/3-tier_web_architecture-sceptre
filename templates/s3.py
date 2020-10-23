from troposphere import AWS_ACCOUNT_ID
from troposphere_mate import (
    Output,
    Ref,
    s3,
    Sub,
)

from base import Base


class S3(Base):
    # s3.yamlから変数を取得する(14~20行)
    @property
    def project(self):
        return self.sceptre_user_data['project']

    @property
    def prefix(self):
        return self.sceptre_user_data['prefix']

    def create_template(self):
        # ELBのログを保存する
        elb_log_bucket = self.tpl.add_resource(
            s3.Bucket(
                'ElbLogBucket',
                BucketName=f'{self.prefix}-{self.project}-lb-log-bucket',
            )
        )

        # ELBの論理IDをアウトプット
        self.tpl.add_output(
            Output(
                'ElbLogBucket',
                Description='LoadBalancer Log Bucket',
                Value=Ref(elb_log_bucket)
            )
        )

        # ELBのログを保存させるためのBucketPolicyを作成
        self.tpl.add_resource(
            s3.BucketPolicy(
                'AlbLogPolicy',
                Bucket=Ref(elb_log_bucket),
                PolicyDocument={
                    'Version': '2012-10-17',
                    'Statement': [
                        {
                            'Effect': 'Allow',
                            'Principal': {
                                'AWS': 'arn:aws:iam::582318560864:root'
                            },
                            'Action': 's3:PutObject',
                            'Resource': Sub(
                                f'arn:aws:s3:::${{{elb_log_bucket.title}}}/AWSLogs/${{{AWS_ACCOUNT_ID}}}/*'
                            )
                        },
                        {
                            'Effect': 'Allow',
                            'Principal': {
                                'Service': 'delivery.logs.amazonaws.com'
                            },
                            'Action': 's3:PutObject',
                            'Resource': Sub(
                                f'arn:aws:s3:::${{{elb_log_bucket.title}}}/AWSLogs/${{{AWS_ACCOUNT_ID}}}/*'
                            ),
                            'Condition': {
                                'StringEquals': {
                                    's3:x-amz-acl': 'bucket-owner-full-control'
                                }
                            }
                        },
                        {
                            'Effect': 'Allow',
                            'Principal': {
                                'Service': 'delivery.logs.amazonaws.com'
                            },
                            'Action': 's3:GetBucketAcl',
                            'Resource': Sub(
                                f'arn:aws:s3:::${{{elb_log_bucket.title}}}'
                            )
                        }
                    ]
                }

            )
        )


# SceptreにTemplateを渡してCFnを実行する
def sceptre_handler(sceptre_user_data):
    return S3(sceptre_user_data).to_yaml()
