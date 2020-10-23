import boto3
from base import Base
from troposphere_mate import (
    AWS_REGION,
    GetAZs,
    Join,
    Output,
    Ref,
    Select,
    Tag,
    ec2,
)


# CFnを実行したリージョンのAZの数を返す
def get_az_count():
    boto3_ec2 = boto3.client('ec2')
    response = boto3_ec2.describe_availability_zones()
    return len(response['AvailabilityZones'])


class Vpc(Base):
    # vpc.yamlから変数を取得する(22~44行)
    @property
    def prefix(self):
        return self.sceptre_user_data['prefix']
    
    @property
    def project(self):
        return self.sceptre_user_data['project']
    
    @property
    def vpc_cidr_block(self):
        return self.sceptre_user_data['vpc_cidr_block']

    @property
    def web_subnet_addrs(self):
        return self.sceptre_user_data['web_subnet_addrs']

    @property
    def private_subnet_addrs(self):
        return self.sceptre_user_data['private_subnet_addrs']
    
    @property
    def db_subnet_addrs(self):
        return self.sceptre_user_data['db_subnet_addrs']
    
    # 各関数を実行してTemplateを作成する
    def create_template(self):
        vpc, igw = self.create_vpc_base()
        self.create_subnets(vpc, 'Web', self.web_subnet_addrs)
        self.create_subnets(vpc, 'Private', self.private_subnet_addrs)
        self.create_subnets(vpc, 'DB', self.db_subnet_addrs)

    # VPCの構成要素を作成
    def create_vpc_base(self):
        # VPCを作成
        vpc = self.tpl.add_resource(
            ec2.VPC(
                'Vpc',
                CidrBlock=self.vpc_cidr_block,
                EnableDnsSupport=True,
                EnableDnsHostnames=True,
                Tags=[
                    Tag(
                        'Name',
                        f'{self.prefix}-{self.project}-vpc'
                    )
                ]
            )
        )

        # VPCの論理IDをoutputする
        self.tpl.add_output(
            Output(
                'VpcId',
                Description='VpcId',
                Value=Ref(vpc)
            )
        )

        # VPCのCidrBlockをoutputする
        self.tpl.add_output(
            Output(
                'VpcCidr',
                Description='VPC Cidr Block',
                Value=self.vpc_cidr_block
            )
        )

        # InternetGatewayを作成
        igw = self.tpl.add_resource(
            ec2.InternetGateway(
                'Igw'
            )
        )

        # InternetGatewayの論理IDをoutputする
        self.tpl.add_output(
            Output(
                'IgwId',
                Description='Internet Gateway Id',
                Value=Ref(igw)
            )
        )

        # InternetGatewayをVPCにアタッチする
        self.tpl.add_resource(
            ec2.VPCGatewayAttachment(
                'VpcIgwAttachment',
                InternetGatewayId=Ref(igw),
                VpcId=Ref(vpc)
            )
        )

        return vpc, igw
    
    # サブネットを作成
    def create_subnets(self, vpc, prefix, addr_list):
        subnets = []
        for index, addr in enumerate(addr_list):
            subnets.append(
                self.tpl.add_resource(
                    ec2.Subnet(
                        f'{prefix}Subnet{index}',
                        CidrBlock=addr,
                        VpcId=Ref(vpc),
                        AvailabilityZone=Select(index % get_az_count(), GetAZs(Ref(AWS_REGION))),
                        Tags=[
                            Tag('Name', f'{prefix}Subnet{index}')
                        ]
                    )
                )
            )
        
        # サブネットの論理IDをアウトプットする
        self.tpl.add_output(
            Output(
                f'{prefix}SubnetList',
                Description=f'{prefix} subnet list',
                Value=Join(',', [Ref(subnet) for subnet in subnets])
            )
        )

        return subnets


# SceptreにTemplateを渡してCFnを実行する
def sceptre_handler(sceptre_user_data):
    return Vpc(sceptre_user_data).to_yaml()
