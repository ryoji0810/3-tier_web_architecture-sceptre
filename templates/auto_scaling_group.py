from base import Base

from troposphere_mate import (
    autoscaling
)


class AutoScalingGroup(Base):
    # auto-scaling.yamlから変数を取得する(10~38行)
    @property
    def prefix(self):
        return self.sceptre_user_data['prefix']

    @property
    def project(self):
        return self.sceptre_user_data['project']

    @property
    def launch_template_latest_version(self):
        return self.sceptre_user_data['launch_template_latest_version']

    @property
    def subnet_id_list(self):
        val = []
        for v in self.sceptre_user_data['subnet_id_list']:
            val.extend(v.split(','))
        return val

    @property
    def target_group(self):
        val = []
        for v in self.sceptre_user_data['target_group']:
            val.extend(v.split(','))
        return val

    @property
    def launch_template(self):
        return self.sceptre_user_data['launch_template']

    def create_template(self):
        # AutoScalingGroupを作成
        self.tpl.add_resource(
            autoscaling.AutoScalingGroup(
                'AutoScalingGroup',
                AutoScalingGroupName=f'{self.prefix}-{self.project}-auto-scaling-group',
                Cooldown=60,
                DesiredCapacity=4,
                HealthCheckGracePeriod=30,
                HealthCheckType='ELB',
                LaunchTemplate=autoscaling.LaunchTemplateSpecification(
                    LaunchTemplateId=self.launch_template,
                    Version=self.launch_template_latest_version
                ),
                MaxSize=6,
                MinSize=3,
                TargetGroupARNs=self.target_group,
                VPCZoneIdentifier=self.subnet_id_list,
            )
        )


# SceptreにTemplateを渡してCFnを実行する
def sceptre_handler(sceptre_user_data):
    return AutoScalingGroup(sceptre_user_data).to_yaml()
