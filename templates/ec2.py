from base import Base
from troposphere_mate import (
    ec2,
)


class Ec2(Base):
    # ec2.yamlから変数を取得する(10~35行)
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
    def subnet_id_list(self):
        val = []
        for v in self.sceptre_user_data['subnet_id_list']:
            val.extend(v.split(','))
        return val

    def create_template(self):
        self.create_instance(self.subnet_id_list)

    # インスタンスをサブネットごとに作成
    def create_instance(self, subnet_list):
        instances = []
        for index, subnet in enumerate(subnet_list):
            instances.append(
                self.tpl.add_resource(
                    ec2.Instance(
                        f'PrivateInstance{index}',
                        ImageId=self.image_id,
                        InstanceType=self.instance_type,
                        KeyName=self.key_name,
                        SubnetId=subnet,
                    )
                )
            )

        return instances


# SceptreにTemplateを渡してCFnを実行する
def sceptre_handler(sceptre_user_data):
    return Ec2(sceptre_user_data).to_yaml()
