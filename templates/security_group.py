from base import Base
from troposphere_mate import (
    GetAtt,
    Output,
    ec2,
)


class SecurityGroup(Base):
    # security_group.yamlから変数を取得する(11~28行)
    @property
    def prefix(self):
        return self.sceptre_user_data['prefix']
    
    @property
    def project(self):
        return self.sceptre_user_data['project']
    
    @property
    def vpc_id(self):
        return self.sceptre_user_data['vpc_id']
    
    @property
    def vpc_cidr(self):
        return self.sceptre_user_data['vpc_cidr']
    
    def create_template(self):
        self.create_web_sg()
        self.create_db_sg()

    # 443、80番ポートからのアクセスを許可するセキュリティグループを作成
    def create_web_sg(self):
        web_sg = self.tpl.add_resource(
            ec2.SecurityGroup(
                'WebSG',
                GroupDescription='Allow Web From Any',
                VpcId=self.vpc_id,
                SecurityGroupIngress=[
                    ec2.SecurityGroupRule(
                        IpProtocol='tcp',
                        CidrIp='0.0.0.0/0',
                        FromPort=443,
                        ToPort=443
                    ),
                    ec2.SecurityGroupRule(
                        IpProtocol='tcp',
                        CidrIp='0.0.0.0/0',
                        FromPort=80,
                        ToPort=80
                    ),
                ]
            )
        )

        # セキュリティグループの論理IDをアウトプットする
        self.tpl.add_output(
            Output(
                'WebSGId',
                Description='Web Security Group Id',
                Value=GetAtt(web_sg, 'GroupId')
            )
        )

    # Auroraのセキュリティグループを作成
    def create_db_sg(self):
        db_sg = self.tpl.add_resource(
            ec2.SecurityGroup(
                'DBSG',
                GroupDescription='Allow DB From Any',
                VpcId=self.vpc_id,
                SecurityGroupIngress=[
                    ec2.SecurityGroupRule(
                        IpProtocol='tcp',
                        CidrIp='0.0.0.0/0',
                        FromPort=3306,
                        ToPort=3306
                    )
                ]
            )
        )

        # セキュリティグループの論理IDをアウトプットする
        self.tpl.add_output(
            Output(
                'DBSGId',
                Description='DB Security Group Id',
                Value=GetAtt(db_sg, 'GroupId')
            )
        )


# SceptreにTemplateを渡してCFnを実行する
def sceptre_handler(sceptre_user_data):
    return SecurityGroup(sceptre_user_data).to_yaml()
