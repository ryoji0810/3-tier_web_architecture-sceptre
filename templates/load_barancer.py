from base import Base
from troposphere_mate import (
    elasticloadbalancingv2 as elb,
    Ref,
    Output
)


class ElasticLoadBarancer(Base):
    # load-barancer.yamlから変数を取得する(11~39行)
    @property
    def prefix(self):
        return self.sceptre_user_data['prefix']

    @property
    def project(self):
        return self.sceptre_user_data['project']

    @property
    def elb_log_bucket(self):
        return self.sceptre_user_data['elb_log_bucket']

    @property
    def subnet_id_list(self):
        val = []
        for v in self.sceptre_user_data['subnet_id_list']:
            val.extend(v.split(','))
        return val

    @property
    def security_group_list(self):
        val = []
        for v in self.sceptre_user_data['security_group_list']:
            val.extend(v.split(','))
        return val

    @property
    def vpc_id(self):
        return self.sceptre_user_data['vpc_id']

    def create_template(self):
        # ALBを作成する
        alb = self.tpl.add_resource(
            elb.LoadBalancer(
                'LoadBarancer',
                Name=f'{self.prefix}-{self.project}-alb',
                LoadBalancerAttributes=[
                    elb.LoadBalancerAttributes(
                        Key='access_logs.s3.enabled',
                        Value='true'
                    ),
                    elb.LoadBalancerAttributes(
                        Key='access_logs.s3.bucket',
                        Value=self.elb_log_bucket
                    )
                ],
                Scheme='internet-facing',
                SecurityGroups=self.security_group_list,
                Subnets=self.subnet_id_list
            )
        )

        # ALBの論理IDをアウトプット
        self.tpl.add_output(
            Output(
                'LoadBalancer',
                Description='ALB ARN',
                Value=Ref(alb)
            )
        )

        # ターゲットグループを作成
        target_group = self.tpl.add_resource(
            elb.TargetGroup(
                'TargetGroup',
                HealthCheckPath='/',
                HealthCheckPort='80',
                HealthCheckProtocol='HTTP',
                Matcher=elb.Matcher(
                    HttpCode='200'
                ),
                Name=f'{self.prefix}-{self.project}-target-group',
                Port=80,
                Protocol='HTTP',
                TargetType='instance',
                VpcId=self.vpc_id
            )
        )

        # ターゲットグループの論理IDをアウトプット
        self.tpl.add_output(
            Output(
                'TargetGroupId',
                Description='TargetGroup Id',
                Value=Ref(target_group)
            )
        )

        # リスナーを作成
        self.tpl.add_resource(
            elb.Listener(
                'Listener',
                DefaultActions=[
                    elb.Action(
                        Type='forward',
                        TargetGroupArn=Ref(target_group),
                    )
                ],
                LoadBalancerArn=Ref(alb),
                Port=80,
                Protocol='HTTP'
                )
            )


# SceptreにTemplateを渡してCFnを実行する
def sceptre_handler(sceptre_user_data):
    return ElasticLoadBarancer(sceptre_user_data).to_yaml()
