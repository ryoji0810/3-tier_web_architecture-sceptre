from base import Base
from troposphere_mate import (
    Output,
    Ref,
    Tag,
    ec2,
)


class RouteTable(Base):
    # security_group.yamlから変数を取得する(11~38行)
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
    def igw_id(self):
        return self.sceptre_user_data['igw_id']

    @property
    def web_subnet_list(self):
        return self.sceptre_user_data['web_subnet_list'].split(',')

    @property
    def private_subnet_list(self):
        return self.sceptre_user_data['private_subnet_list'].split(',')

    @property
    def db_subnet_list(self):
        return self.sceptre_user_data['db_subnet_list'].split(',')

    # Templateを作成
    def create_template(self):
        self.create_web_route()
        self.create_private_route()
        self.create_db_route()

    # Webのルートテーブルを作成
    def create_web_route(self):
        web_route_table = self.tpl.add_resource(
            ec2.RouteTable(
                'WebRouteTable',
                VpcId=self.vpc_id,
                Tags=[
                    Tag('Name', f'{self.prefix}-{self.project}-WebRouteTable')
                ]
            )
        )

        # Webのルートテーブルの論理IDをアウトプット
        self.tpl.add_output(
            Output(
                'WebRouteTableId',
                Description='Web Route Table Id',
                Value=Ref(web_route_table)
            )
        )

        # Webのルートテーブルにルートを追加
        self.tpl.add_resource(
            ec2.Route(
                'WebRoute',
                RouteTableId=Ref(web_route_table),
                DestinationCidrBlock='0.0.0.0/0',
                GatewayId=self.igw_id
            )
        )

        # Webサブネットにルートテーブルを紐つける
        for index, subnet_id in enumerate(self.web_subnet_list):
            self.tpl.add_resource(
                ec2.SubnetRouteTableAssociation(
                    f'WebSubnet{index}RouteTable',
                    RouteTableId=Ref(web_route_table),
                    SubnetId=subnet_id
                )
            )

    # Privateサブネットのルートテーブルを作成
    def create_private_route(self):
        private_route_table = self.tpl.add_resource(
            ec2.RouteTable(
                'PrivateRouteTable',
                VpcId=self.vpc_id,
                Tags=[
                    Tag('Name', f'{self.prefix}-{self.project}-PrivateRouteTable')
                ]
            )
        )

        # Privateサブネットのルートテーブルの論理IDをアウトプット
        self.tpl.add_output(
            Output(
                'PrivateRouteTableId',
                Description='Private Route Table Id',
                Value=Ref(private_route_table)
            )
        )

        # ルートテーブルをPrivateサブネットに紐つける
        for index, subnet_id in enumerate(self.private_subnet_list):
            self.tpl.add_resource(
                ec2.SubnetRouteTableAssociation(
                    f'PrivateSubnet{index}RouteTable',
                    RouteTableId=Ref(private_route_table),
                    SubnetId=subnet_id
                )
            )

    # DBのルートテーブルを作成
    def create_db_route(self):
        db_route_table = self.tpl.add_resource(
            ec2.RouteTable(
                'DBRouteTable',
                VpcId=self.vpc_id,
                Tags=[
                    Tag('Name', f'{self.prefix}-{self.project}-DBRouteTable')
                ]
            )
        )

        # DBのルートテーブルの論理IDをアウトプット
        self.tpl.add_output(
            Output(
                'DBRouteTableId',
                Description='DB Route Table Id',
                Value=Ref(db_route_table)
            )
        )

        # DBのルートテーブルをサブネットに紐つける
        for index, subnet_id in enumerate(self.db_subnet_list):
            self.tpl.add_resource(
                ec2.SubnetRouteTableAssociation(
                    f'DBSubnet{index}RouteTable',
                    RouteTableId=Ref(db_route_table),
                    SubnetId=subnet_id
                )
            )


# SceptreにTemplateを渡してCFnを実行する
def sceptre_handler(sceptre_user_data):
    return RouteTable(sceptre_user_data).to_yaml()
