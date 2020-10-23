from base import Base
from troposphere_mate import (
    Output,
    Ref,
    GetAtt,
    ec2,
)


class LaunchTemplate(Base):
    # launch-template.yamlから変数を取得する(12行~34行)
    @property
    def prefix(self):
        return self.sceptre_user_data['prefix']

    @property
    def project(self):
        return self.sceptre_user_data['project']

    @property
    def image_id(self):
        return self.sceptre_user_data['image_id']

    @property
    def instance_type(self):
        return self.sceptre_user_data['instance_type']

    @property
    def key_name(self):
        return self.sceptre_user_data['key_name']

    @property
    def web_sg_id(self):
        return self.sceptre_user_data['web_sg_id']

    def create_template(self):
        self.create_launch_template()

    # 起動テンプレートを作成
    def create_launch_template(self):
        web_sg_list = [self.web_sg_id]
        launch_template = self.tpl.add_resource(
            ec2.LaunchTemplate(
                'LaunchTemplate',
                LaunchTemplateName=f'{self.prefix}-{self.project}-LaunchTemplate',
                LaunchTemplateData=ec2.LaunchTemplateData(
                    ImageId=self.image_id,
                    InstanceType=self.instance_type,
                    KeyName=self.key_name,
                    SecurityGroupIds=web_sg_list
                )
            )
        )

        # 起動テンプレートの論理IDをアウトプット
        self.tpl.add_output(
            Output(
                'LaunchTemplateId',
                Description='LaunchTemplate Id',
                Value=Ref(launch_template)
            )
        )

        # 起動テンプレートのバージョンをアウトプット
        self.tpl.add_output(
            Output(
                'LaunchTemplateLatestVersion',
                Description='LaunchTemplate Latest Version',
                Value=GetAtt(launch_template, 'LatestVersionNumber')
            )
        )


# SceptreにTemplateを渡してCFnを実行する
def sceptre_handler(sceptre_user_data):
    return LaunchTemplate(sceptre_user_data).to_yaml()
